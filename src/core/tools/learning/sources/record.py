"""The shape every provider returns, and how duplicates are recognised.

A record is a plain dict, so it can go straight into sources.json:
  kind      paper | survey | book | course | doc | web | discussion
  title, authors (at most 5), year, venue, doi, url, abstract
  cited_by  citation count
  editions  edition count, for books
  refs      {"openalex": "W1", "s2": "abc", "arxiv": "1706.03762", "ol": "OL1W"}
"""

import re
import unicodedata

KINDS = ("paper", "survey", "book", "course", "doc", "web", "discussion")


def make(**fields) -> dict:
    record = {
        "kind": fields.get("kind") or "paper",
        "title": " ".join((fields.get("title") or "").split()),
        "authors": [a for a in (fields.get("authors") or []) if a][:5],
        "year": fields.get("year"),
        "venue": fields.get("venue") or "",
        "doi": clean_doi(fields.get("doi")),
        "url": fields.get("url") or "",
        "abstract": " ".join((fields.get("abstract") or "").split()),
        "cited_by": fields.get("cited_by"),
        "editions": fields.get("editions"),
        "refs": {k: v for k, v in (fields.get("refs") or {}).items() if v},
    }
    return record


def clean_doi(doi: str | None) -> str:
    if not doi:
        return ""
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi.strip(), flags=re.IGNORECASE).lower()


def normal_title(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def keys(record: dict) -> set[str]:
    """Identifiers that mean "the same work" when two records share any of them."""
    found = set()
    if record.get("doi"):
        found.add(f"doi:{record['doi']}")
    url = re.sub(r"^https?://(www\.)?", "", (record.get("url") or "").strip().lower()).rstrip("/")
    if url and not url.startswith("doi.org/"):
        found.add(f"url:{url}")
    for provider, value in record.get("refs", {}).items():
        if provider == "arxiv":
            value = re.sub(r"v\d+$", "", value)
        found.add(f"{provider}:{value}")
    title = normal_title(record.get("title", ""))
    if len(title) > 12:
        found.add(f"title:{title}:{record.get('year') or ''}")
    return found


def merge(into: dict, other: dict) -> dict:
    """Fill gaps in `into` from `other`; keep the larger citation count."""
    for field in ("title", "authors", "year", "venue", "doi", "url", "abstract"):
        if not into.get(field) and other.get(field):
            into[field] = other[field]
    for field in ("cited_by", "editions"):
        counts = [c for c in (into.get(field), other.get(field)) if c is not None]
        into[field] = max(counts) if counts else None
    into["refs"] = {**other.get("refs", {}), **into.get("refs", {})}
    if into.get("kind") == "paper" and other.get("kind") in ("survey", "book"):
        into["kind"] = other["kind"]
    return into


def dedupe(records: list[dict]) -> list[dict]:
    merged: list[dict] = []
    for record in records:
        match = next((m for m in merged if keys(m) & keys(record)), None)
        if match:
            merge(match, record)
        else:
            merged.append(record)
    return merged


def rank(record: dict) -> tuple[int, int]:
    return record.get("cited_by") or 0, record.get("editions") or 0


def best_ref(record: dict) -> str:
    """The identifier to pass back to `puck sources add` or `graph`."""
    refs = record.get("refs", {})
    for provider in ("openalex", "s2", "arxiv", "ol"):
        if refs.get(provider):
            return f"{provider}:{refs[provider]}"
    return f"doi:{record['doi']}" if record.get("doi") else record.get("url", "")


def one_line(record: dict) -> str:
    authors = ", ".join(record["authors"][:2]) + (" et al." if len(record["authors"]) > 2 else "")
    counts = []
    if record.get("cited_by") is not None:
        counts.append(f"cited {record['cited_by']}")
    if record.get("editions"):
        counts.append(f"{record['editions']} editions")
    count = ", ".join(counts)
    parts = [best_ref(record), str(record.get("year") or "n.d."), record["kind"], count,
             record["title"], f"— {authors}" if authors else ""]
    return "  ".join(part for part in parts if part)
