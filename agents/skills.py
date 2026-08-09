"""Client-side skills: named recipes the agents load on demand.

A skill is procedural know-how (HOW to use the tools well), as opposed to a
tool (a capability). Each skill is a markdown file in skills/ with a tiny
frontmatter header:

    ---
    name: my-skill
    description: one line shown to the lead at planning time
    ---
    ...full instructions...

Progressive disclosure keeps context small: the lead only ever sees the
name+description index; the worker pulls the full text with the load_skill
tool when a step calls for it. Same idea as Claude Code's Agent Skills.
"""

from pathlib import Path

from langchain_core.tools import tool

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"


def _frontmatter(path: Path) -> dict:
    meta, lines = {}, path.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta


def skill_index() -> str:
    """One 'name: description' line per skill, for the planning prompt."""
    entries = []
    for path in sorted(SKILLS_DIR.glob("*.md")):
        meta = _frontmatter(path)
        if "name" in meta:
            entries.append(f"- {meta['name']}: {meta.get('description', '')}")
    return "\n".join(entries)


@tool
def load_skill(name: str) -> str:
    """Load the full instructions of a named skill.

    Use this when the current step matches a skill from the known-skills list;
    then follow the loaded instructions.
    """
    for path in sorted(SKILLS_DIR.glob("*.md")):
        if _frontmatter(path).get("name") == name:
            return path.read_text(encoding="utf-8")
    return f"No skill named '{name}'. Available:\n{skill_index()}"
