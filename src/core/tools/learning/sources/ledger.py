"""sources.json: one numbered entry per source a topic relies on.

Ledger ids (s1, s2, ...) are assigned here, never by a model, so a citation can
only point at a source that was really found.
"""

from core.common import store
from core.common.errors import PuckError
from core.tools.learning import topics
from core.tools.learning.sources.record import KINDS, keys, merge

ROLES = ("anchor", "canon", "frontier", "textbook", "practical", "critique")


def _path(topic: str):
    return topics.folder(topic) / topics.FILES["sources"]


def load(topic: str) -> list[dict]:
    return (store.read_json(_path(topic)) or {}).get("sources", [])


def get(topic: str, source_id: str) -> dict:
    found = next((s for s in load(topic) if s["id"] == source_id), None)
    if found is None:
        raise PuckError(f"No source '{source_id}' in {topic}. Run `puck sources list {topic}`.")
    return found


def add(topic: str, record: dict, role: str = "", why: str = "", quote: str = "",
        group: str = "") -> tuple[str, bool]:
    """Add or merge a source. Returns (id, created)."""
    if role and role not in ROLES:
        raise PuckError(f"--role must be one of {', '.join(ROLES)}")
    if record.get("kind") not in KINDS:
        raise PuckError(f"kind must be one of {', '.join(KINDS)}")
    with store.locked(f"topic-{topics.slug(topic)}-ledger"):
        sources = load(topic)
        existing = next((s for s in sources if keys(s) & keys(record)), None)
        if existing is None:
            number = max((int(s["id"][1:]) for s in sources), default=0) + 1
            existing = {"id": f"s{number}", **record, "role": "", "why": "", "quotes": [], "group": ""}
            sources.append(existing)
            created = True
        else:
            merge(existing, record)
            created = False
        if role:
            existing["role"] = role
        if why:
            existing["why"] = why
        if group:
            existing["group"] = group
        if quote and quote not in existing["quotes"]:
            existing["quotes"].append(quote)
        store.write_json(_path(topic), {"sources": sources})
    return existing["id"], created
