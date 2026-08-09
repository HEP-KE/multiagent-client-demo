"""Shared state that flows through the LangGraph graph.

Deliberately minimal: no worker types, no DAG dependencies, no checkpointing —
just a plan, a cursor, and results. Production systems grow each of those.
"""

from typing import TypedDict


class Step(TypedDict):
    id: int
    description: str


class AgentState(TypedDict):
    task: str                 # the user's science question
    plan: list[Step]          # written once by the lead's first visit
    current: int              # index of the next step to execute
    step_results: list[str]   # one summary per completed step
    final_report: str         # written by the lead's last visit
    history: list[str]        # summaries of previous runs (for follow-ups)
