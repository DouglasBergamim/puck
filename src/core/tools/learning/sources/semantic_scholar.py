"""Semantic Scholar: papers and the citation graph.

Without a key, all anonymous users share one rate limit, so requests often get
HTTP 429. Set S2_API_KEY in the environment to get a personal limit.
"""

import os

from core.tools.learning.sources import net
from core.tools.learning.sources.record import make

BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,title,year,authors,citationCount,externalIds,venue,url,publicationTypes,abstract"


def _headers() -> dict:
    key = os.environ.get("S2_API_KEY")
    return {"x-api-key": key} if key else {}


def to_record(paper: dict) -> dict:
    ids = paper.get("externalIds") or {}
    types = paper.get("publicationTypes") or []
    return make(
        kind="survey" if "Review" in types else "book" if "Book" in types else "paper",
        title=paper.get("title"),
        authors=[a.get("name") for a in paper.get("authors") or []],
        year=paper.get("year"),
        venue=paper.get("venue"),
        doi=ids.get("DOI"),
        url=paper.get("url"),
        abstract=paper.get("abstract"),
        cited_by=paper.get("citationCount"),
        refs={"s2": paper.get("paperId"), "arxiv": ids.get("ArXiv")},
    )


def search(query: str, kind: str, limit: int) -> list[dict]:
    params = {"query": query, "limit": limit, "fields": FIELDS}
    if kind == "survey":
        params["publicationTypes"] = "Review"
    data = net.get_json(f"{BASE}/paper/search", params, _headers())
    return [to_record(paper) for paper in data.get("data") or []]


def get(paper_id: str) -> dict:
    return to_record(net.get_json(f"{BASE}/paper/{paper_id}", {"fields": FIELDS}, _headers()))


def _edges(paper_id: str, edge: str, side: str, limit: int) -> list[dict]:
    fields = ",".join(f"{side}.{f}" for f in FIELDS.split(","))
    data = net.get_json(f"{BASE}/paper/{paper_id}/{edge}", {"fields": fields, "limit": 1000}, _headers())
    papers = [item[side] for item in data.get("data") or [] if item.get(side, {}).get("title")]
    papers.sort(key=lambda p: p.get("citationCount") or 0, reverse=True)
    return [to_record(paper) for paper in papers[:limit]]


def references(paper_id: str, limit: int) -> list[dict]:
    return _edges(paper_id, "references", "citedPaper", limit)


def cited_by(paper_id: str, limit: int, since: int | None = None) -> list[dict]:
    found = _edges(paper_id, "citations", "citingPaper", limit * 3)
    return [r for r in found if not since or (r.get("year") or 0) >= since][:limit]
