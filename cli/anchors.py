"""Session checkpoints: mechanical anchors that survive compaction.

Anchors build up incrementally from hooks, so there are no per-host transcript
parsers. Checkpoints hold verbatim prompts, which is why state/ is gitignored.
"""

import re
from pathlib import Path

from cli import store

CHECKPOINT_LIMIT = 8_000
LINE_LIMIT = 300
RECENT_PROMPTS = 5

URL = re.compile(r"https?://[^\s\"'<>)\]]+")
# Neighbouring - / . rule out UUID segments and pieces of paths.
SHA = re.compile(r"(?<![\w/.-])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}(?![\w/-])")
PATH = re.compile(r"(?:~/|\.{1,2}/|/)[\w.@-]+(?:/[\w.@-]+)*\.\w+")
ERROR = re.compile(r"^.*\b(?:Traceback|\w*Error|FAILED|fatal:|panic:).*$", re.MULTILINE)


def checkpoint_path(session_id: str) -> Path:
    return store.state_dir() / "checkpoints" / f"{store.safe_id(session_id)}.md"


def extract(text: str) -> list[tuple[str, str]]:
    """Return (kind, value) anchors in a stable order, without duplicates."""
    found: list[tuple[str, str]] = []
    for kind, pattern in (("path", PATH), ("sha", SHA), ("url", URL), ("error", ERROR)):
        for match in pattern.finditer(text):
            found.append((kind, " ".join(match.group(0).split())[:LINE_LIMIT]))
    return list(dict.fromkeys(found))


def record_prompt(session_id: str, prompt: str) -> None:
    line = " ".join(prompt.split())[:LINE_LIMIT]
    if line:
        store.append(checkpoint_path(session_id), f"- [prompt] {line}\n")


def record_anchors(session_id: str, text: str) -> None:
    anchors = extract(text)
    if anchors:
        lines = "".join(f"- [{kind}] {value}\n" for kind, value in anchors)
        store.append(checkpoint_path(session_id), lines)


def render(session_id: str, limit: int = CHECKPOINT_LIMIT) -> str:
    """Summarise a checkpoint for injection, newest first, within the limit."""
    try:
        lines = checkpoint_path(session_id).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ""
    prompts = [line for line in lines if line.startswith("- [prompt]")][-RECENT_PROMPTS:]
    seen: set[str] = set()
    anchors = []
    for line in reversed(lines):
        if line not in seen and not line.startswith("- [prompt]"):
            seen.add(line)
            anchors.append(line)
    output = ["Checkpoint from before compaction.", "Recent prompts:", *prompts, "Anchors:"]
    size = sum(len(line) + 1 for line in output)
    for line in anchors:
        if size + len(line) + 1 > limit:
            break
        output.append(line)
        size += len(line) + 1
    return "\n".join(output)
