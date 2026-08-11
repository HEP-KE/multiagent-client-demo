"""Assemble the graph: lead -> worker (loop) -> lead -> END.

The lead plans (first visit) and reports (last visit); the worker executes one
step per visit. The two route functions below are the entire "supervisor":
deterministic Python, no LLM — not every agent in a multi-agent system needs
to be a model call.
"""

from langgraph.graph import END, START, StateGraph

from .memory import remember
from .nodes import make_lead, make_worker
from .skills import load_skill
from .state import AgentState


def new_run(task: str) -> AgentState:
    """Fresh initial state for graph.ainvoke / graph.astream."""
    return {"task": task, "plan": [], "current": 0,
            "step_results": [], "final_report": "", "history": []}


def follow_up(previous: AgentState, task: str) -> AgentState:
    """Initial state for a follow-up question that remembers the previous run."""
    entry = f"Task: {previous['task']}\nOutcome: {previous['final_report']}"
    return {**new_run(task), "history": previous["history"] + [entry]}


def route_from_lead(state: AgentState) -> str:
    """After planning: hand off to the worker. After reporting: stop."""
    if state["current"] < len(state["plan"]):
        return "worker"
    return END


def route_from_worker(state: AgentState) -> str:
    """Keep the worker looping until the plan is exhausted, then back to lead."""
    if state["current"] < len(state["plan"]):
        return "worker"
    return "lead"


def build_graph(llm, tools, extras: bool = False):
    """Compile the lead/worker graph.

    extras=True additionally enables skills and memory: the load_skill and
    remember tools ride along with the MCP tools, the skill index appears in
    the lead's planning prompt, and MEMORY.md is read at planning time.
    Notebook 02 runs without extras; notebook 03 turns them on.
    """
    if extras:
        tools = list(tools) + [load_skill, remember]
    graph = StateGraph(AgentState)
    graph.add_node("lead", make_lead(llm, tools, extras=extras))
    graph.add_node("worker", make_worker(llm, tools))

    graph.add_edge(START, "lead")
    graph.add_conditional_edges("lead", route_from_lead, ["worker", END])
    graph.add_conditional_edges("worker", route_from_worker, ["worker", "lead"])
    return graph.compile()
