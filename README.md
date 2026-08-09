# multiagent-client-demo

**Part 2 of the client-server agent tutorial.** A small LangGraph multi-agent
system that connects to the
[`spectra-mcp-server`](https://github.com/HEP-KE/spectra-mcp-server) (Part 1),
plans, calls its tools, and reproduces a matter-power-spectrum figure from a
one-sentence science question.

Setup for both repos: [`prep.md`](prep.md). Then open
**`notebooks/02_demo_client.ipynb`** — the tutorial is driven from there.
`notebooks/03_next_steps.ipynb` covers the extras (skills, memory, follow-up
queries, switching LLM backends).

## Architecture

```
 science question
        │
        ▼
   ┌────────┐  plan   ┌──────────┐
   │  lead  │ ──────► │  worker  │──┐
   │        │ ◄────── │          │◄─┘ one step per visit,
   └────────┘  done   └──────────┘    calls MCP tools
        │
        ▼                  ▲ ▲
     report       MCP (HTTP or stdio)
                           │ │
                 spectra-mcp-server   ← CLASS, data, plotting live here
```

Two LLM roles — think PI and grad student. The **lead** plans first and writes
the report last; the **worker** executes one step per visit. ~300 lines of
Python in `agents/`:

| file | lines | job |
|---|---|---|
| `llm.py` | ~40 | Gemini (default) or Groq via OpenAI-compatible endpoints — `make_llm("groq")` |
| `mcp.py` | ~25 | load the server's tools as LangChain tools |
| `state.py` | ~30 | the shared state: task, plan, cursor, results, history |
| `nodes.py` | ~150 | the lead and worker roles |
| `graph.py` | ~55 | wire them up (+ `new_run` / `follow_up` helpers); the two `route_from_*` functions are the entire "supervisor" |
| `skills.py` | ~55 | named recipes in `skills/*.md`, loaded on demand via the `load_skill` tool |
| `memory.py` | ~30 | `MEMORY.md` lessons read at planning time; agents append via `remember` |

The client knows **nothing about cosmology** — every tool name, argument, and
description arrives over MCP from the server. Point it at a different MCP
server and the same ~300 lines run a different science.

## Run

```bash
# terminal 1, in ../spectra-mcp-server:
python -m mcp_server --transport streamable-http --port 8000

# terminal 2, here:
jupyter lab notebooks/02_demo_client.ipynb
```

The notebook also shows the stdio variant (client spawns the server; no
terminal 1 needed) — the config style production MCP clients use.

## Extras (implemented, covered in notebook 03)

- **Skills**: drop a `skills/my-workflow.md` (frontmatter `name:`/`description:`)
  and the lead sees it at planning time; the worker loads the full recipe on
  demand with the `load_skill` tool — tools are *verbs*, skills are *recipes*.
- **Memory**: lessons in `MEMORY.md` persist across runs; agents append via
  the `remember` tool.
- **Follow-up queries**: `graph.ainvoke(follow_up(prev_state, "now also ..."))`
  continues from a previous run's results instead of starting cold.
- **Groq backend**: `make_llm("groq")` — free open-weight `gpt-oss-120b`,
  ~14,400 requests/day (Gemini's free tier is ~20/day).

## What a production version adds

Everything here scales up without changing the concepts: a typed plan with
DAG dependencies and retries, several specialized workers (data / compute /
literature / visualization), checkpointing and resume, human-in-the-loop
approval before execution, report generation with citations, and MCP servers
with dozens of tools. Build any of them on top of exactly this skeleton.
