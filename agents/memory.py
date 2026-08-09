"""Persistent memory: lessons that survive across runs.

MEMORY.md (repo root) is read into the lead's planning prompt at the start of
every run; the remember tool lets agents append a lesson worth keeping. This
is the smallest possible version of the memory systems in coding agents like
Claude Code.
"""

from pathlib import Path

from langchain_core.tools import tool

MEMORY_FILE = Path(__file__).resolve().parents[1] / "MEMORY.md"


def read_memory() -> str:
    """Return remembered lessons (empty string if none yet)."""
    if MEMORY_FILE.exists():
        return MEMORY_FILE.read_text(encoding="utf-8").strip()
    return ""


@tool
def remember(lesson: str) -> str:
    """Save a one-line lesson to persistent memory for future runs.

    Use this sparingly, when you learn something non-obvious that would help
    next time (a pitfall, a working parameter choice, a file convention).
    """
    with MEMORY_FILE.open("a", encoding="utf-8") as f:
        f.write(f"- {lesson.strip()}\n")
    return f"Remembered: {lesson.strip()}"
