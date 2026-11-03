"""Agent scaffolding: `puck agent new` copies the template for a lead or a worker."""

from pathlib import Path

from core.common import paths, store
from core.common.errors import PuckError
from core.common.model import frontmatter, split_frontmatter
from core.primitives import lint

TEMPLATES = {"worker": "agent.md", "lead": "agent-lead.md"}


def new(name: str, mode: str, description: str) -> Path:
    if mode not in TEMPLATES:
        raise PuckError("--mode must be worker or lead.")
    if not lint.NAME.match(name):
        raise PuckError("Agent names are lowercase words joined by hyphens.")
    meta, body = split_frontmatter((paths.templates() / TEMPLATES[mode]).read_text())
    meta["name"] = name
    meta["description"] = description
    with store.locked("agents"):
        path = paths.agents() / f"{name}.md"
        if path.exists():
            raise PuckError(f"Agent '{name}' exists. Change it instead of making a new one.")
        if mode == "lead" and (paths.skills() / name).exists():
            raise PuckError(f"A lead becomes a skill, and the skill '{name}' exists. Pick another name.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(frontmatter(meta, body))
    return path
