"""Wiki lint: every claim in a topic's wiki must trace to a source that was really read.

Rules for each wiki page, applied to every paragraph and list item:
- It cites at least one ledger id, like [s3], or carries `[not in sources]`.
- Every cited id exists in sources.json.
- A quoted passage of four or more words appears in the cited sources' raw/ text.
- A number with two or more digits appears in the cited sources' raw/ text.
- Links to other wiki pages point at pages that exist.
Headings, code blocks, Mermaid diagrams and blockquotes are skipped.
A page whose frontmatter says `status: unverified` passes, with a warning.
"""

import re
from pathlib import Path

from core.common import store
from core.tools.learning import topics
from core.tools.learning.sources import ledger
from core.tools.learning.sources.verify import normal, raw_text

CITE = re.compile(r"\[(s\d+(?:\s*,\s*s\d+)*)\]")
UNSOURCED = "[not in sources]"
QUOTE = re.compile(r"[\"“]([^\"”]{12,})[\"”]")
NUMBER = re.compile(r"(?<![\w.])(\d[\d,.]*\d)(%?)")
LINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]|\]\(((?!https?:|#)[^)]+\.md)\)")


def _blocks(text: str) -> list[tuple[int, str]]:
    """Paragraphs and list items with their first line number, skipping non-claims."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        start = end + 1
    blocks, current, first, fenced = [], [], 0, False

    def flush():
        if current:
            blocks.append((first, " ".join(current)))
            current.clear()

    for number, line in enumerate(lines[start:], start=start + 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            fenced = not fenced
            continue
        if fenced or not stripped or stripped.startswith(("#", ">", "|", "<!--")):
            flush()
            continue
        if re.match(r"^([-*+]|\d+\.)\s", stripped):
            flush()
        if not current:
            first = number
        current.append(stripped)
    flush()
    return blocks


def lint_page(topic: str, page: Path, known: set[str], raw_cache: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    text = page.read_text(errors="replace")
    name = f"{page.parent.name}/{page.name}"
    if re.search(r"^status:\s*unverified\s*$", text.split("\n---", 1)[0], re.MULTILINE):
        warnings.append(f"{name}: marked unverified.")
    wiki = page.parent
    for line, block in _blocks(text):
        where = f"{name}:{line}"
        cited = [i.strip() for group in CITE.findall(block) for i in group.split(",")]
        if not cited:
            if UNSOURCED not in block:
                errors.append(f"{where}: no citation. Cite a source like [s1], or mark it {UNSOURCED}.")
            continue
        missing = [i for i in cited if i not in known]
        if missing:
            errors.append(f"{where}: cites {', '.join(missing)}, which sources.json doesn't have.")
            continue
        evidence = []
        for source_id in cited:
            if source_id not in raw_cache:
                raw_cache[source_id] = raw_text(topic, source_id)
            if raw_cache[source_id]:
                evidence.append(raw_cache[source_id][1])
        if not evidence:
            warnings.append(f"{where}: none of {', '.join(cited)} has raw/ text, so quotes and numbers weren't checked.")
            continue
        body = " ".join(evidence)
        for quote in QUOTE.findall(block):
            if len(quote.split()) >= 4 and normal(quote) not in body:
                errors.append(f"{where}: quote not found in {', '.join(cited)}: \"{quote[:70]}\"")
        for digits, percent in NUMBER.findall(CITE.sub("", block)):
            if normal(digits) not in body:
                errors.append(f"{where}: {digits}{percent} doesn't appear in {', '.join(cited)}.")
    for match in LINK.finditer(text):
        target = match.group(1) or match.group(2)
        target_path = wiki / (target if target.endswith(".md") else f"{target}.md")
        if not target_path.exists():
            errors.append(f"{name}: broken link to {target}.")
    return errors, warnings


def write_index(topic: str) -> Path:
    wiki = topics.folder(topic) / "wiki"
    lines = [f"# Wiki: {topics.slug(topic)}", ""]
    for page in sorted(wiki.glob("*.md")):
        if page.name == "index.md":
            continue
        heading = next((l[2:].strip() for l in page.read_text().splitlines() if l.startswith("# ")), page.stem)
        lines.append(f"- [{heading}]({page.name})")
    path = wiki / "index.md"
    store.write_text(path, "\n".join(lines) + "\n")
    return path


def lint(topic: str) -> tuple[list[str], list[str]]:
    known = {source["id"] for source in ledger.load(topic)}
    errors, warnings, cache = [], [], {}
    pages = [p for p in sorted((topics.folder(topic) / "wiki").glob("*.md")) if p.name != "index.md"]
    for page in pages:
        page_errors, page_warnings = lint_page(topic, page, known, cache)
        errors += page_errors
        warnings += page_warnings
    if pages:
        write_index(topic)
    return errors, warnings
