"""Evidence: save what a source says to raw/, then check claims against it.

raw/<id>.md is written once and never edited. Its header says who fetched it:
`puck` (fetched here, so quotes can be trusted to come from the source) or
`agent` (pasted in by a model, so a matching quote proves less).
"""

import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

from core.common import store
from core.common.errors import PuckError
from core.tools.learning import topics
from core.tools.learning.sources import ledger, net

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form"}
BLOCK_TAGS = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "section", "article", "blockquote"}
MAX_CHARS = 200_000
BLOCKED = {401, 402, 403, 429}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skipping += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skipping:
            self.skipping -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            self.parts.append(data)


def html_text(html: str) -> str:
    parser = _Text()
    parser.feed(html)
    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines())
    return "\n".join(line for line in lines if line)


def normal(text: str) -> str:
    """Compare quotes by content, ignoring typography and line wrapping."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                         "–": "-", "—": "-", " ": " "}))
    text = re.sub(r"-\s*\n\s*", "", text)
    return " ".join(text.split()).casefold()


def raw_path(topic: str, source_id: str) -> Path:
    return topics.folder(topic) / "raw" / f"{source_id}.md"


def _write_raw(topic: str, source_id: str, fetched_by: str, origin: str, body: str, force: bool) -> Path:
    path = raw_path(topic, source_id)
    if path.exists() and not force:
        raise PuckError(f"{path} already exists, and raw files are never edited. Pass --force to replace it.")
    source = ledger.get(topic, source_id)
    header = f"---\nsource: {source_id}\nfetched_by: {fetched_by}\norigin: {origin}\n---\n# {source['title']}\n\n"
    store.write_text(path, header + body.strip()[:MAX_CHARS] + "\n")
    return path


def fetch(topic: str, source_id: str, force: bool = False) -> tuple[Path, list[str]]:
    """Save the source's abstract and, for HTML pages, its text. PDFs are left to `excerpt`."""
    source = ledger.get(topic, source_id)
    sections, notes = [], []
    if source.get("abstract"):
        sections.append("## Abstract\n\n" + source["abstract"])
    url = source.get("url") or (f"https://doi.org/{source['doi']}" if source.get("doi") else "")
    if url and source["kind"] in ("web", "doc"):
        try:
            status, body, final = net.fetch(url)
            kind = "html" if b"<html" in body[:2000].lower() or b"<!doctype html" in body[:2000].lower() else "other"
            if status == 200 and kind == "html":
                sections.append(f"## Page text ({final})\n\n" + html_text(body.decode("utf-8", "replace")))
            else:
                notes.append(f"{url}: HTTP {status}, {kind}; use `puck sources excerpt` for this text.")
        except net.SourceError as error:
            notes.append(str(error))
    if not sections:
        raise PuckError(f"Nothing to fetch for {source_id}: no abstract and no readable page. "
                        f"Paste the text you read with `puck sources excerpt {topic} {source_id} --file …`.")
    return _write_raw(topic, source_id, "puck", url or "provider abstract", "\n\n".join(sections), force), notes


def excerpt(topic: str, source_id: str, text: str, origin: str, force: bool = False) -> Path:
    """Save text a model read itself, e.g. from a PDF. Marked as agent-fetched."""
    if not text.strip():
        raise PuckError("The excerpt is empty.")
    return _write_raw(topic, source_id, "agent", origin, text, force)


def raw_text(topic: str, source_id: str) -> tuple[str, str] | None:
    """(fetched_by, normalised text), or None if there is no raw file."""
    path = raw_path(topic, source_id)
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    match = re.search(r"^fetched_by: (\w+)$", text, re.MULTILINE)
    return (match.group(1) if match else "agent"), normal(text)


def resolves(source: dict) -> tuple[bool | None, str]:
    """True if the DOI or URL exists, False if it doesn't, None if we couldn't tell."""
    try:
        if source.get("doi"):
            data = net.get_json(f"https://doi.org/api/handles/{source['doi']}")
            return data.get("responseCode") == 1, f"doi {source['doi']}"
        if source.get("url"):
            status, _, _ = net.fetch(source["url"])
            if status in BLOCKED:
                return None, f"{source['url']} refused automated access (HTTP {status})"
            return status < 400, f"{source['url']} HTTP {status}"
    except net.SourceError as error:
        if "HTTP 404" in str(error):
            return False, str(error)
        return None, str(error)
    return bool(source.get("refs")), "found through a provider; no DOI or URL to check"


def verify(topic: str, check_links: bool = True) -> tuple[list[str], list[str]]:
    """Errors fail the check. Warnings are shown but don't."""
    errors, warnings = [], []
    sources = ledger.load(topic)
    if not sources:
        errors.append("sources.json is empty.")
    for source in sources:
        label = f"{source['id']} ({source['title'][:60]})"
        if not source.get("role"):
            warnings.append(f"{label}: no role; set one with `puck sources add … --role`.")
        if check_links:
            ok, detail = resolves(source)
            if ok is False:
                errors.append(f"{label}: does not resolve: {detail}")
            elif ok is None:
                warnings.append(f"{label}: could not confirm: {detail}")
        if source.get("quotes"):
            raw = raw_text(topic, source["id"])
            if raw is None:
                errors.append(f"{label}: has quotes but no raw/{source['id']}.md. Run `puck sources fetch`.")
                continue
            fetched_by, text = raw
            for quote in source["quotes"]:
                if normal(quote) not in text:
                    errors.append(f"{label}: quote not found in raw/{source['id']}.md: \"{quote[:80]}\"")
            if fetched_by != "puck":
                warnings.append(f"{label}: raw text was pasted by an agent, so its quotes are weaker evidence.")
    return errors, warnings
