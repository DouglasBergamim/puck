"""The one place that knows Puck's folder layout."""

import os
from pathlib import Path

CONTEXT = Path("context")
BUILT = ("instructions", "skills", "agents", "hooks.yaml", "profile.md", "templates")


def home() -> Path:
    override = os.environ.get("PUCK_HOME")
    return Path(override) if override else Path(__file__).resolve().parents[2]


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


def wiki(root: Path | None = None) -> Path:
    return context(root) / "knowledge" / "wiki"


def retros(root: Path | None = None) -> Path:
    return context(root) / "tasks"


def proposals(root: Path | None = None) -> Path:
    return context(root) / "proposals"


def state(root: Path | None = None) -> Path:
    return (root or home()) / "state"


def dist(root: Path | None = None) -> Path:
    return (root or home()) / "dist"
