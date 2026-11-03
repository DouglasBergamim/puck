"""The one place that knows Puck's folder layout."""

import os
import re
from pathlib import Path

from core.common.errors import PuckError

CONTEXT = Path("context")
BUILT = ("instructions", "skills", "agents", "hooks.yaml", "profile.md", "templates")


def home() -> Path:
    override = os.environ.get("PUCK_HOME")
    return Path(override) if override else Path(__file__).resolve().parents[3]


def topic_slug(name: str) -> str:
    """A topic's folder name. Tasks and topics both use it, so it lives here."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not cleaned:
        raise PuckError("A topic name needs at least one letter or digit.")
    return cleaned[:60]


def context(root: Path | None = None) -> Path:
    return (root or home()) / CONTEXT


def instructions(root: Path | None = None) -> Path:
    return context(root) / "instructions" / "global.md"


def profile(root: Path | None = None) -> Path:
    return context(root) / "profile.md"


def skills(root: Path | None = None) -> Path:
    return context(root) / "skills"


def agents(root: Path | None = None) -> Path:
    return context(root) / "agents"


def hook_rules(root: Path | None = None) -> Path:
    return context(root) / "hooks.yaml"


def templates(root: Path | None = None) -> Path:
    return context(root) / "templates"


def knowledge(root: Path | None = None) -> Path:
    return context(root) / "knowledge"


def topic(name: str, root: Path | None = None) -> Path:
    """One folder per study topic: mission, map, path, sources, wiki, sessions."""
    return knowledge(root) / name


def retros(root: Path | None = None) -> Path:
    return context(root) / "tasks"


def state(root: Path | None = None) -> Path:
    return (root or home()) / "state"


def dist(root: Path | None = None) -> Path:
    return (root or home()) / "dist"
