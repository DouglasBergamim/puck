"""OpenAlex: papers, reviews and books, with the citation graph in both directions.

Without a key, requests share a small free daily budget per IP address. A free
personal key raises it: set OPENALEX_API_KEY in the environment.
"""

import os

from core.tools.learning.sources import net
from core.tools.learning.sources.record import make

BASE = "https://api.openalex.org"
FIELDS = "id,doi,display_name,publication_year,authorships,cited_by_count,primary_location,type,ids,abstract_inverted_index"
TYPES = {"survey": "type:review", "book": "type:book"}


def _params(**extra) -> dict:
    return {"select": FIELDS, "api_key": os.environ.get("OPENALEX_API_KEY"), **extra}


def short_id(value: str) -> str:
    return value.rsplit("/", 1)[-1]


def abstract(index: dict | None) -> str:
    if not index:
        return ""
    positions = [(pos, word) for word, places in index.items() for pos in places]
    return " ".join(word for _, word in sorted(positions))


def to_record(work: dict) -> dict:
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    kind = {"review": "survey", "book": "book", "book-chapter": "book"}.get(work.get("type"), "paper")
    ids = work.get("ids") or {}
    arxiv = ""
    landing = location.get("landing_page_url") or ""
    if "arxiv.org/abs/" in landing:
        arxiv = landing.rsplit("/abs/", 1)[-1]
    return make(
        kind=kind,
        title=work.get("display_name"),
        authors=[(a.get("author") or {}).get("display_name") for a in work.get("authorships") or []],
        year=work.get("publication_year"),
        venue=source.get("display_name"),
        doi=work.get("doi") or ids.get("doi"),
        url=landing or work.get("doi") or "",
        abstract=abstract(work.get("abstract_inverted_index")),
        cited_by=work.get("cited_by_count"),
        refs={"openalex": short_id(work.get("id", "")), "arxiv": arxiv},
    )


def search(query: str, kind: str, limit: int) -> list[dict]:
    params = _params(search=query, per_page=limit)
    if kind in TYPES:
        params["filter"] = TYPES[kind]
    data = net.get_json(f"{BASE}/works", params)
    return [to_record(work) for work in data.get("results", [])]


def get(work_id: str) -> dict:
    data = net.get_json(f"{BASE}/works/{work_id}", _params(select=FIELDS + ",referenced_works"))
    record = to_record(data)
    record["_referenced"] = [short_id(w) for w in data.get("referenced_works") or []]
    return record


def references(work_id: str, limit: int) -> list[dict]:
    """The work's own references, most cited first: usually the field's canon."""
    referenced = get(work_id)["_referenced"][:100]
    if not referenced:
        return []
    data = net.get_json(f"{BASE}/works", _params(
        filter="openalex:" + "|".join(referenced), sort="cited_by_count:desc", per_page=limit))
    return [to_record(work) for work in data.get("results", [])]


def cited_by(work_id: str, limit: int, since: int | None = None) -> list[dict]:
    """Works citing this one, most cited first: the frontier built on it."""
    query = f"cites:{work_id}" + (f",from_publication_date:{since}-01-01" if since else "")
    data = net.get_json(f"{BASE}/works", _params(filter=query, sort="cited_by_count:desc", per_page=limit))
    return [to_record(work) for work in data.get("results", [])]
