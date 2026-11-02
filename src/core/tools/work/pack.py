"""The task pack: a small map of existing context relevant to a goal.

It holds paths and one-line summaries, never content, so the model decides what
to read. `puck task start` prints it, which works on every harness.
"""

import re
from pathlib import Path

from core.common import paths, store
from core.common.model import split_frontmatter

PACK_LIMIT = 2_000
STOPWORDS = {
    "about", "after", "again", "also", "and", "because", "before", "build", "could", "does",
    "from", "have", "into", "make", "need", "should", "that", "the", "this", "using", "want",
    "what", "when", "where", "which", "will", "with", "would", "your",
}


def keywords(goal: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", goal.lower())
    return {word for word in words if len(word) >= 3 and word not in STOPWORDS}


def _score(words: set[str], text: str) -> int:
    lowered = text.lower()
    return sum(1 for word in words if word in lowered)


def _skills(root: Path) -> list[tuple[str, str, str]]:
    found = []
    for path in sorted(paths.skills(root).glob("*/SKILL.md")):
        meta, _ = split_frontmatter(path.read_text())
        if meta.get("metadata", {}).get("status") == "active":
            found.append(("skill", str(path), " ".join(meta["description"].split())))
    return found


def _markdown(folder: Path, label: str, pattern: str) -> list[tuple[str, str, str]]:
    found = []
    for path in sorted(folder.glob(pattern)):
        text = path.read_text(errors="replace")
        headings = " ".join(re.findall(r"^#+ (.+)$", text, re.MULTILINE))
        first = next((l for l in text.splitlines() if l.strip() and not l.startswith("#")), "")
        found.append((label, str(path), f"{path.stem}: {headings} {first}"))
    return found


def _proposals(root: Path) -> list[str]:
    return [str(path) for path in sorted(paths.proposals(root).glob("*.md"))]


CHAINS = {
    "research": "Research chain: scope, field-map, literature, reading-path. Each skill names the next.",
}


def pack(goal: str, root: Path | None = None, kind: str | None = None) -> str:
    root = root or store.home()
    words = keywords(goal)
    candidates = (_skills(root)
                  + _markdown(paths.knowledge(root), "topic", "*/mission.md")
                  + _markdown(paths.knowledge(root), "wiki", "*/wiki/*.md")
                  + _markdown(paths.retros(root), "retro", "*.md"))
    scored = [(_score(words, f"{path} {text}"), label, path, text)
              for label, path, text in candidates]
    ranked = sorted((item for item in scored if item[0] > 0), key=lambda item: -item[0])
    lines = ["Task pack: read only what you need."]
    if kind in CHAINS:
        lines.append(f"- {CHAINS[kind]}")
    size = sum(len(line) + 1 for line in lines)
    for _, label, path, text in ranked:
        line = f"- [{label}] {path}: {text[:120]}"
        if size + len(line) + 1 > PACK_LIMIT - 200:
            break
        lines.append(line)
        size += len(line) + 1
    if not ranked:
        lines.append("- Nothing relevant found.")
    pending = _proposals(root)
    if pending:
        lines.append(f"- {len(pending)} proposal(s) await the user: `puck proposal list`.")
    return "\n".join(lines)
