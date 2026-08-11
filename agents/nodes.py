"""The two LLM roles: lead and worker.

The lead is visited twice: at the start it breaks the task into a plan, and
after the worker has finished every step it writes the final report. The
worker executes one step at a time by calling MCP tools. (Think supervisor and grad
student.)

All model calls go through _ainvoke, which waits out HTTP 429 responses:
Gemini's free tier allows only a few requests per minute, and a graph run is a
burst of ~10 calls. Paid or institutional endpoints won't hit this.
"""

import asyncio
import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .memory import read_memory
from .skills import skill_index

MAX_TOOL_ITERATIONS = 6
RATE_LIMIT_WAIT_S = 60


async def _ainvoke(model, messages, attempts=5):
    """Call the model, sleeping through free-tier rate limits (HTTP 429)."""
    for attempt in range(attempts):
        try:
            return await model.ainvoke(messages)
        except Exception as exc:
            if "429" not in str(exc) or attempt == attempts - 1:
                raise
            print(f"      (rate limited — waiting {RATE_LIMIT_WAIT_S}s)")
            await asyncio.sleep(RATE_LIMIT_WAIT_S)


def _tool_catalog(tools) -> str:
    return "\n".join(
        f"- {t.name}: {t.description.strip().splitlines()[0]}" for t in tools
    )


def _parse_json_list(text: str) -> list:
    """Parse a JSON array, tolerating a markdown code fence around it."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.removeprefix("json").strip()
    return json.loads(text)


def make_lead(llm, tools, extras: bool = False):
    skills_section = (
        f"Known skills (the worker can load one with load_skill):\n{skill_index()}\n\n"
        if extras
        else ""
    )
    plan_prompt = (
        "You are the lead of a small multi-agent science system.\n"
        "Break the user's task into 2-5 sequential steps. Each step must be\n"
        "achievable with the tools below, and later steps may use files created\n"
        "by earlier ones.\n\n"
        f"Available tools:\n{_tool_catalog(tools)}\n\n"
        + skills_section
        + 'Reply with ONLY a JSON array like [{"id": 1, "description": "..."}].'
    )

    async def lead(state):
        if not state["plan"]:
            # First visit: write the plan. Memory and any previous-run context
            # are read fresh each run.
            context = ""
            if extras and (memory := read_memory()):
                context += f"\n\nLessons from earlier runs:\n{memory}"
            if state["history"]:
                context += "\n\nContext from previous runs (follow-up):\n" + "\n\n".join(state["history"])
            messages = [SystemMessage(plan_prompt + context), HumanMessage(state["task"])]
            reply = await _ainvoke(llm, messages)
            try:
                plan = _parse_json_list(reply.content)
            except (json.JSONDecodeError, IndexError):
                # One repair attempt: ask again, insisting on bare JSON.
                messages += [reply, HumanMessage("Reply with ONLY the JSON array, no prose.")]
                plan = _parse_json_list((await _ainvoke(llm, messages)).content)
            return {"plan": plan, "current": 0, "step_results": []}

        # Second visit, after the worker finished every step: write the report.
        steps = "\n".join(
            f"{i + 1}. {r}" for i, r in enumerate(state["step_results"])
        )
        reply = await _ainvoke(
            llm,
            [
                SystemMessage(
                    "Write a short markdown report (a few sentences plus a file "
                    "list) summarizing what was done and what was found."
                ),
                HumanMessage(f"Task: {state['task']}\n\nStep results:\n{steps}"),
            ],
        )
        return {"final_report": reply.content}

    return lead


def make_worker(llm, tools):
    tools_by_name = {t.name: t for t in tools}
    bound = llm.bind_tools(tools)

    async def worker(state):
        step = state["plan"][state["current"]]
        earlier = [f"Previous run: {h}" for h in state["history"]] + [
            f"Step {i + 1} result: {r}" for i, r in enumerate(state["step_results"])
        ]
        context = "\n".join(earlier) or "Nothing yet."
        messages = [
            SystemMessage(
                "You are a worker agent. Complete the step you are given by calling "
                "tools. Results from earlier steps (including file paths) are listed "
                "below — reuse those paths instead of recomputing.\n\n"
                f"Overall task: {state['task']}\n\nEarlier results:\n{context}\n\n"
                "Call each tool at most once unless a call fails. When the step "
                "is done, reply WITHOUT tool calls: a 1-2 sentence summary that "
                "includes any file paths you created."
            ),
            HumanMessage(f"Step {step['id']}: {step['description']}"),
        ]

        for _ in range(MAX_TOOL_ITERATIONS):
            reply = await _ainvoke(bound, messages)
            messages.append(reply)
            if not reply.tool_calls:
                break
            for call in reply.tool_calls:
                result = await tools_by_name[call["name"]].ainvoke(call["args"])
                messages.append(ToolMessage(str(result), tool_call_id=call["id"]))

        if reply.tool_calls:
            # Some models keep requesting tools until the budget runs out.
            # Force a text wrap-up so the next step still gets the file paths.
            messages.append(
                HumanMessage(
                    "Tool budget reached. Without calling any more tools, summarize "
                    "in 1-2 sentences what was accomplished, including the exact "
                    "file paths of any files created."
                )
            )
            reply = await _ainvoke(llm, messages)

        summary = reply.content or "(no summary produced)"
        return {
            "step_results": state["step_results"] + [summary],
            "current": state["current"] + 1,
        }

    return worker
