"""Open Library: books, with edition counts as a popularity signal. No key needed."""

from core.tools.learning.sources import net
from core.tools.learning.sources.record import make

BASE = "https://openlibrary.org"
FIELDS = "key,title,author_name,first_publish_year,isbn,edition_count,first_sentence"


def to_record(doc: dict) -> dict:
    work = doc.get("key", "").rsplit("/", 1)[-1]
    first = doc.get("first_sentence")
    return make(
        kind="book",
        title=doc.get("title"),
        authors=doc.get("author_name"),
        year=doc.get("first_publish_year"),
        url=f"{BASE}/works/{work}" if work else "",
        abstract=first[0] if isinstance(first, list) and first else "",
        editions=doc.get("edition_count"),
        refs={"ol": work},
    )


def search(query: str, kind: str, limit: int) -> list[dict]:
    data = net.get_json(f"{BASE}/search.json", {"q": query, "limit": limit, "fields": FIELDS})
    return [to_record(doc) for doc in data.get("docs") or []]


def get(work_id: str) -> dict:
    data = net.get_json(f"{BASE}/search.json", {"q": f"key:/works/{work_id}", "fields": FIELDS})
    docs = data.get("docs") or []
    if not docs:
        raise net.SourceError(f"Open Library has no work {work_id}.")
    return to_record(docs[0])
