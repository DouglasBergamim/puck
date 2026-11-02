"""arXiv: preprints, the frontier of fast-moving fields. No key needed."""

import xml.etree.ElementTree as ET

from core.tools.learning.sources import net
from core.tools.learning.sources.record import make

BASE = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _parse(body: bytes) -> list[dict]:
    try:
        root = ET.fromstring(body)
    except ET.ParseError as error:
        raise net.SourceError("arXiv returned something that isn't Atom XML.") from error
    records = []
    for entry in root.findall("atom:entry", NS):
        abs_url = entry.findtext("atom:id", "", NS)
        if "/abs/" not in abs_url:
            continue
        arxiv_id = abs_url.rsplit("/abs/", 1)[-1]
        title = entry.findtext("atom:title", "", NS)
        records.append(make(
            kind="survey" if "survey" in title.lower() or "review" in title.lower() else "paper",
            title=title,
            authors=[a.findtext("atom:name", "", NS) for a in entry.findall("atom:author", NS)],
            year=int(entry.findtext("atom:published", "0000", NS)[:4]) or None,
            venue="arXiv",
            doi=entry.findtext("arxiv:doi", "", NS),
            url=abs_url.replace("http://", "https://"),
            abstract=entry.findtext("atom:summary", "", NS),
            refs={"arxiv": arxiv_id},
        ))
    return records


def _get(params: dict) -> list[dict]:
    status, body, _ = net.fetch(BASE, params)
    if status != 200:
        raise net.SourceError(f"arXiv returned HTTP {status}.")
    return _parse(body)


def search(query: str, kind: str, limit: int) -> list[dict]:
    terms = " AND ".join(f"all:{word}" for word in query.split())
    if kind == "survey":
        terms = f"({terms}) AND (ti:survey OR ti:review)"
    return _get({"search_query": terms, "max_results": limit})


def get(arxiv_id: str) -> dict:
    found = _get({"id_list": arxiv_id})
    if not found:
        raise net.SourceError(f"arXiv has no paper {arxiv_id}.")
    return found[0]
