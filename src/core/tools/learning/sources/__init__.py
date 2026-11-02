"""Find papers and books across free scholarly APIs, and walk their citation graph.

Each provider module offers search(query, kind, limit) and get(id). OpenAlex and
Semantic Scholar also offer references(id, limit) and cited_by(id, limit, since).
A failing provider becomes a warning, so one outage never blocks a search.
"""

from core.tools.learning.sources import arxiv, net, openalex, openlibrary, semantic_scholar
from core.tools.learning.sources.record import KINDS, best_ref, dedupe, one_line, rank

PROVIDERS = {"openalex": openalex, "s2": semantic_scholar, "arxiv": arxiv, "ol": openlibrary}
BY_KIND = {
    "any": ("openalex", "s2", "arxiv", "ol"),
    "paper": ("openalex", "s2", "arxiv"),
    "survey": ("openalex", "s2", "arxiv"),
    "book": ("ol", "openalex"),
}
GRAPH = ("openalex", "s2")

__all__ = ["KINDS", "BY_KIND", "best_ref", "one_line", "search", "resolve", "graph", "parse_ref"]


def parse_ref(ref: str) -> tuple[str, str]:
    """`openalex:W123`, `s2:abc`, `arxiv:1706.03762`, `ol:OL1W` or `doi:10.1/x`."""
    provider, _, value = ref.partition(":")
    if provider not in (*PROVIDERS, "doi") or not value:
        raise net.SourceError(
            f"'{ref}' isn't a source reference. Use openalex:W…, s2:…, arxiv:…, ol:OL…W or doi:10.…")
    return provider, value


def search(query: str, kind: str = "any", limit: int = 10,
           providers: tuple[str, ...] | None = None) -> tuple[list[dict], list[str]]:
    """Results from every provider for this kind, merged and sorted by citations."""
    if kind not in BY_KIND:
        raise net.SourceError(f"--kind must be one of {', '.join(BY_KIND)}")
    found, warnings = [], []
    for name in providers or BY_KIND[kind]:
        try:
            found += PROVIDERS[name].search(query, kind, limit)
        except net.SourceError as error:
            warnings.append(f"{name}: {error}")
    merged = dedupe(found)
    if kind in ("survey", "book"):
        merged = [r for r in merged if r["kind"] == kind] or merged
    merged.sort(key=rank, reverse=True)
    return merged[:limit], warnings


def resolve(ref: str) -> dict:
    """Full metadata for one reference."""
    provider, value = parse_ref(ref)
    if provider == "doi":
        return openalex.get(f"doi:{value}")
    record = PROVIDERS[provider].get(value)
    record.pop("_referenced", None)
    return record


def graph(ref: str, direction: str, limit: int = 15, since: int | None = None) -> list[dict]:
    """`references`: what this work builds on. `cited-by`: what builds on it."""
    provider, value = parse_ref(ref)
    if provider == "doi":
        provider, value = "openalex", f"doi:{value}"
    if provider not in GRAPH:
        record = resolve(ref)
        if not record.get("doi"):
            raise net.SourceError(f"No citation graph for {ref}: it has no DOI. Try an openalex: or s2: ref.")
        provider, value = "openalex", f"doi:{record['doi']}"
    module = PROVIDERS[provider]
    if direction == "references":
        return module.references(value, limit)
    if direction == "cited-by":
        return module.cited_by(value, limit, since)
    raise net.SourceError("--direction must be references or cited-by")
