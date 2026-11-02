"""Harness-neutral types. Adapters transform these and know nothing else in core."""

from dataclasses import dataclass

import yaml

CAPABILITIES = ("read", "search", "shell-read", "shell", "edit", "web", "subagents")
EVENTS = ("session-start", "stop")
DESCRIPTION = "A layer in front of any agent harness that optimises LLM context and improves its tools"


@dataclass(frozen=True)
class File:
    path: str
    content: bytes
    executable: bool = False


@dataclass(frozen=True)
class ToolMap:
    tools: tuple[str, ...]
    note: str = ""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    invocation: str
    body: str
    files: tuple[File, ...] = ()
    evals: tuple[File, ...] = ()


@dataclass(frozen=True)
class Agent:
    name: str
    description: str
    tools: tuple[str, ...]
    model: str
    max_turns: int | None
    body: str


@dataclass(frozen=True)
class HookRule:
    id: str
    event: str
    run: str
    mode: str
    timeout_ms: int
    on_failure: str


@dataclass(frozen=True)
class Event:
    event: str
    host: str
    cwd: str | None = None
    already_forced: bool = False


@dataclass(frozen=True)
class Result:
    context: str | None = None
    decision: str | None = None
    reason: str | None = None


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    _, head, body = text.split("---\n", 2)
    return yaml.safe_load(head) or {}, body


def frontmatter(meta: dict, body: str) -> str:
    return f"---\n{yaml.safe_dump(meta, sort_keys=False)}---\n{body}"
