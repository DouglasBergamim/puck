"""Topics, sources, the wiki lint and exercises. No test touches the network."""

import json
import threading
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from cli import main as cli
from core.common.errors import PuckError
from core.tools.learning import exercises, kb, roadmap, sources, topics
from core.tools.learning.sources import arxiv, ledger, net, openalex, openlibrary, semantic_scholar, verify
from core.tools.learning.sources.record import dedupe, make

FIXTURES = Path(__file__).parent / "fixtures" / "sources"


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


@pytest.fixture
def offline(monkeypatch):
    """Route every request to a recorded response; anything unexpected fails loudly."""
    routes = {
        ("api.openalex.org", "/works"): fixture("openalex_search.json"),
        ("api.openalex.org", "/works/W3134435812"): fixture("openalex_work.json"),
        ("api.semanticscholar.org", "/graph/v1/paper/search"): fixture("s2_search.json"),
        ("export.arxiv.org", "/api/query"): fixture("arxiv_search.xml"),
        ("openlibrary.org", "/search.json"): fixture("openlibrary_search.json"),
    }
    extra: dict[str, tuple[int, bytes]] = {}

    def fake(url, params=None, headers=None):
        if url in extra:
            status, body = extra[url]
            return status, body, url
        parts = urlsplit(url)
        key = (parts.netloc, parts.path)
        if key not in routes:
            raise AssertionError(f"unexpected request: {url}")
        return 200, routes[key], url

    monkeypatch.setattr(net, "fetch", fake)
    return extra


@pytest.fixture
def topic(puck_home):
    topics.new("Attention mechanisms")
    return "attention-mechanisms"


# Providers ------------------------------------------------------------------------

def test_openalex_rebuilds_abstracts_and_marks_reviews(offline):
    records = openalex.search("attention", "survey", 3)
    first = records[0]
    assert first["kind"] == "survey" and first["refs"]["openalex"] == "W3134435812"
    assert first["doi"] == "10.3390/e23030283"
    assert first["abstract"].startswith("Deep learning models and graphics processing units")


def test_each_provider_parses_its_recorded_response(offline):
    s2 = semantic_scholar.search("attention", "any", 2)
    assert s2[0]["refs"] == {"s2": "204e3073870fae3d05bcbc2f6a8e263d9b72e776", "arxiv": "1706.03762"}
    assert s2[1]["kind"] == "survey"
    papers = arxiv.search("attention survey", "any", 2)
    assert papers[0]["refs"]["arxiv"] == "2103.01498v2" and papers[0]["kind"] == "survey"
    books = openlibrary.search("deep learning", "book", 3)
    assert books[0]["title"] == "Deep Learning" and books[0]["editions"] == 5 and books[0]["cited_by"] is None


def test_search_merges_providers_and_reports_failures(offline, monkeypatch):
    def down(*args):
        raise net.SourceError("rate limited")

    monkeypatch.setattr(semantic_scholar, "search", down)
    found, warnings = sources.search("attention", "any", 50)
    assert warnings == ["s2: rate limited"]
    works = [(r["title"].lower(), r["year"]) for r in found]
    assert len(works) == len(set(works))
    counts = [r.get("cited_by") or 0 for r in found]
    assert counts == sorted(counts, reverse=True)


def test_duplicates_merge_on_shared_identifiers():
    a = make(title="Attention Is All You Need", year=2017, refs={"arxiv": "1706.03762v7"}, cited_by=10)
    b = make(title="Attention is all you need", year=2017, refs={"s2": "x", "arxiv": "1706.03762"}, cited_by=99)
    merged = dedupe([a, b])
    assert len(merged) == 1 and merged[0]["cited_by"] == 99 and merged[0]["refs"]["s2"] == "x"


def test_refs_must_name_a_provider():
    with pytest.raises(PuckError, match="isn't a source reference"):
        sources.parse_ref("W123")


# Ledger ---------------------------------------------------------------------------

def test_ledger_assigns_ids_and_merges_duplicates(topic):
    first, created = ledger.add(topic, make(title="Deep Learning", year=2016, doi="10.1/DL"), role="textbook")
    again, created_again = ledger.add(topic, make(title="Deep learning book", doi="https://doi.org/10.1/dl"),
                                      quote="a quote")
    other, _ = ledger.add(topic, make(title="Something else entirely", year=2020))
    assert (first, created, again, created_again, other) == ("s1", True, "s1", False, "s2")
    entry = ledger.get(topic, "s1")
    assert entry["role"] == "textbook" and entry["quotes"] == ["a quote"]


def test_concurrent_adds_get_distinct_ids(topic):
    def add(n):
        ledger.add(topic, make(title=f"Distinct paper number {n} on attention", year=2000 + n))

    threads = [threading.Thread(target=add, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    ids = [s["id"] for s in ledger.load(topic)]
    assert sorted(ids, key=lambda i: int(i[1:])) == [f"s{n}" for n in range(1, 9)]


# Evidence -------------------------------------------------------------------------

def test_ledger_takes_courses_and_recommendation_threads(topic):
    assert cli.main(["sources", "add", topic, "--url", "https://ocw.example.edu/gt", "--title", "Game Theory course",
                     "--kind", "course", "--role", "textbook"]) == 0
    assert cli.main(["sources", "add", topic, "--url", "https://forum.example.com/best-books", "--title", "Best books?",
                     "--kind", "discussion", "--role", "recommendation", "--why", "Osborne recommended by most replies"]) == 0
    kinds = {s["kind"]: s["role"] for s in ledger.load(topic)}
    assert kinds == {"course": "textbook", "discussion": "recommendation"}


def add_with_raw(topic, text, quote="", doi="10.1/ok"):
    source_id, _ = ledger.add(topic, make(title="A source about attention", doi=doi), role="anchor", quote=quote)
    verify.excerpt(topic, source_id, text, "test")
    return source_id


def test_verify_checks_quotes_against_raw_text(topic, offline):
    offline["https://doi.org/api/handles/10.1/ok"] = (200, b'{"responseCode": 1}')
    add_with_raw(topic, "Attention lets a model\nweigh every token “equally” at first.",
                 quote="weigh every token \"equally\"")
    errors, warnings = verify.verify(topic)
    assert errors == []
    assert any("pasted by an agent" in w for w in warnings)


def test_verify_fails_on_invented_quotes_and_dead_dois(topic, offline):
    offline["https://doi.org/api/handles/10.1/gone"] = (404, b'{"responseCode": 100}')
    add_with_raw(topic, "Real text.", quote="text the source never said", doi="10.1/gone")
    errors, _ = verify.verify(topic)
    assert any("quote not found" in e for e in errors)
    assert any("does not resolve" in e for e in errors)


def test_raw_files_are_never_overwritten(topic):
    source_id = add_with_raw(topic, "First reading.")
    with pytest.raises(PuckError, match="never edited"):
        verify.excerpt(topic, source_id, "Second reading.", "test")


def test_html_text_drops_scripts_and_navigation():
    html = "<html><nav>Menu</nav><script>x=1</script><p>Real   text</p><p>More</p></html>"
    assert verify.html_text(html) == "Real text\nMore"


# Wiki lint ------------------------------------------------------------------------

def write_page(topic, name, body):
    path = topics.folder(topic) / "wiki" / name
    path.write_text(body)
    return path


def test_a_grounded_page_passes_and_gets_indexed(topic):
    add_with_raw(topic, "The model reached 28.4 BLEU. \"Attention is all you need\" was the title.")
    write_page(topic, "transformer.md",
               "# Transformer\n\n- It reached 28.4 BLEU [s1].\n- Its title claims \"attention is all you need\" [s1].\n"
               "- My own analogy: a spotlight. [not in sources]\n\n```mermaid\ngraph TD\n a-->b\n```\n"
               "See [[transformer]].\n[s1]\n")
    errors, _ = kb.lint(topic)
    assert errors == []
    assert "transformer.md" in (topics.folder(topic) / "wiki" / "index.md").read_text()


def test_list_items_inherit_a_cited_lead_in(topic):
    add_with_raw(topic, "Section 6 covers entropy.")
    write_page(topic, "reading.md", "# Reading\n\nConcepts: entropy, capacity.\n\nWhere to read [s1]:\n"
               "- Section 6: entropy.\n\nAn uncited paragraph.\n- An uncited item after it.\n\nLimits:\n\n"
               "My advice [not in sources: ours].\n\nSupported by s1 without brackets.\n")
    errors, _ = kb.lint(topic)
    assert [e.split(":")[1] for e in errors] == ["8", "9", "15"]


def test_lint_catches_each_kind_of_ungrounded_claim(topic):
    add_with_raw(topic, "The model reached 28.4 BLEU.")
    write_page(topic, "bad.md",
               "# Bad\n\nNo citation here.\n\nCites a ghost [s9].\n\nIt reached 41.0 BLEU [s1].\n\n"
               "It said \"something the source never said at all\" [s1].\n\nSee [[missing-page]] [s1].\n")
    errors, _ = kb.lint(topic)
    joined = "\n".join(errors)
    assert "bad.md:3: no citation" in joined
    assert "cites s9" in joined
    assert "41.0" in joined
    assert "quote not found" in joined
    assert "broken link to missing-page" in joined


# Topics and sessions ----------------------------------------------------------------

MAP = """# Map

## Concepts

| id | concept | prerequisites | status |
|---|---|---|---|
| embeddings | Embeddings | - | practised |
| attention | Attention | embeddings | unseen |
| multi-head | Multi-head attention | attention | unseen |
| positional | Positional encoding | - | unseen |
"""


def test_new_topic_has_its_folders_and_templates(topic):
    path = topics.folder(topic)
    assert all((path / sub).is_dir() for sub in topics.FOLDERS)
    assert "Attention mechanisms" in (path / "mission.md").read_text()
    assert topics.check(topic, ["mission", "path"]) == [
        "mission.md is missing or still a template", "path.md is missing or still a template"]


def test_next_concept_waits_for_practised_prerequisites(topic):
    (topics.folder(topic) / "map.md").write_text(MAP)
    assert topics.next_concept(topic)["id"] == "attention"
    topics.set_status(topic, "attention", "introduced")
    assert topics.next_concept(topic)["id"] == "attention"
    topics.set_status(topic, "attention", "practised")
    assert topics.next_concept(topic)["id"] == "multi-head"


def test_next_concept_falls_back_to_recall(topic):
    (topics.folder(topic) / "map.md").write_text(MAP.replace("| unseen |", "| can-explain |"))
    assert topics.next_concept(topic)["id"] == "embeddings"


def test_records_number_sessions_and_update_the_map(topic):
    (topics.folder(topic) / "map.md").write_text(MAP)
    first = topics.record(topic, "# Session\nCovered attention.", {"attention": "introduced"})
    second = topics.record(topic, "# Session\nPractised it.", {"attention": "practised"})
    assert (first.name, second.name) == ("0001.md", "0002.md")
    assert "attention: practised" in second.read_text()
    assert next(c for c in topics.concepts(topic) if c["id"] == "attention")["status"] == "practised"
    assert "Practised it." in topics.status_report(topic)


def test_unknown_statuses_are_rejected(topic):
    (topics.folder(topic) / "map.md").write_text(MAP)
    with pytest.raises(PuckError, match="Status must be one of"):
        topics.set_status(topic, "attention", "mastered")


# Exercises --------------------------------------------------------------------------

def make_exercise(topic, check):
    folder = topics.folder(topic) / "exercises" / "e1"
    folder.mkdir(parents=True)
    (folder / "exercise.json").write_text(json.dumps({"concept": "attention", "kind": "code", "check": check}))


def test_exercise_check_passes_only_on_exit_zero(topic):
    make_exercise(topic, "test -f answer.py")
    assert exercises.check(topic, "e1")[0] is False
    (topics.folder(topic) / "exercises" / "e1" / "answer.py").write_text("x = 1\n")
    assert exercises.check(topic, "e1")[0] is True
    assert "exit 0" in (topics.folder(topic) / "exercises" / "e1" / "last-check.txt").read_text()


# Command line -----------------------------------------------------------------------

def test_cli_creates_and_checks_a_topic(puck_home, capsys):
    assert cli.main(["topic", "new", "Linear algebra"]) == 0
    assert cli.main(["topic", "list"]) == 0
    assert "linear-algebra" in capsys.readouterr().out
    assert cli.main(["topic", "check", "linear-algebra", "--has", "mission"]) == 1


LEARN_MISSION = """# Mission: linear algebra

## Subject
Linear algebra.

## Applied to
Machine learning.

## Goal
By the end I can explain what an eigenvector of a covariance matrix says about the data.

## Why
To read ML papers without skipping the maths.

## Depth
use

## Out of scope
- Abstract vector spaces over arbitrary fields.

## Background
Not stated.
"""


def test_topic_check_has_mission_passes_before_any_sources(puck_home, capsys):
    assert cli.main(["topic", "new", "Linear algebra"]) == 0
    (topics.folder("linear-algebra") / "mission.md").write_text(LEARN_MISSION)
    assert cli.main(["topic", "check", "linear-algebra", "--has", "mission", "--no-links"]) == 0
    assert cli.main(["topic", "check", "linear-algebra", "--has", "mission,sources", "--no-links"]) == 1
    assert cli.main(["topic", "check", "linear-algebra", "--no-links"]) == 1
    assert "sources.json" in capsys.readouterr().out


def test_topic_check_runs_every_check_for_the_topic(topic, capsys):
    source_id = add_with_raw(topic, "Real text.", quote="text the source never said")
    assert cli.main(["sources", "fetch", topic, source_id, "--file", "-"]) == 1  # --origin is required
    write_page(topic, "page.md", "# Page\n\nNo citation here.\n")
    assert cli.main(["topic", "check", topic, "--has", "mission", "--no-links"]) == 1
    out = capsys.readouterr().out
    assert "mission.md" in out and "quote not found" in out and "no citation" in out


def test_mission_templates_follow_the_topic_kind(puck_home):
    learn = topics.new("Linear algebra") / "mission.md"
    research = topics.new("HFT and liquidity", kind="research") / "mission.md"
    assert "## Subject" in learn.read_text() and "## Question" not in learn.read_text()
    assert "## Question" in research.read_text() and "## Areas" in research.read_text()
    with pytest.raises(PuckError):
        topics.new("Other", kind="survey")


def test_mission_check_wants_each_section_filled_and_a_real_depth(puck_home):
    topics.new("Linear algebra")
    mission = topics.folder("linear-algebra") / "mission.md"
    # The template mark removed, but every section still holds only its guidance comment.
    mission.write_text(mission.read_text().replace("<!-- template -->\n", ""))
    problems = topics.check("linear-algebra", ["mission"])
    assert "mission.md: ## Subject is empty" in problems and "mission.md: ## Goal is empty" in problems
    mission.write_text(LEARN_MISSION.replace("## Applied to\nMachine learning.\n", "## Applied to\n"))
    assert topics.check("linear-algebra", ["mission"]) == []  # Applied to is optional
    mission.write_text(LEARN_MISSION.replace("\nuse\n", "\ndeep\n"))
    assert topics.check("linear-algebra", ["mission"]) == [
        "mission.md: ## Depth must start with one of orient, use, master"]


def test_topic_check_has_report(topic):
    assert topics.check(topic, ["report"]) == ["report.md is missing or still a template"]
    (topics.folder(topic) / "report.md").write_text("# Report\n\n## Answer\nYes [s1].\n")
    assert topics.check(topic, ["report"]) == []


def test_sources_add_can_fetch_in_the_same_command(topic, offline, capsys):
    offline["https://forum.example.com/best-books"] = (200, b"<html><body><p>Read Osborne first.</p></body></html>")
    assert cli.main(["sources", "add", topic, "--url", "https://forum.example.com/best-books",
                     "--title", "Best books?", "--kind", "discussion", "--role", "recommendation", "--fetch"]) == 0
    assert "Read Osborne first." in (topics.folder(topic) / "raw" / "s1.md").read_text()


ROADMAP_MAP = """# Map: game theory

## Concepts

| id | concept | prerequisites | status |
|---|---|---|---|
| normal-form | Normal-form game | - | practised |
| nash | Nash equilibrium | normal-form | unseen |
| kyle | Kyle model | nash | unseen |
"""

ROADMAP_PATH = """# Path: game theory for finance

Depth: use. Total time: about 12 hours.
Order: Gibbons' order, which the MIT course follows [s1].
Agreed: {agreed}

## Stage 1: Static games
- Goal: find a Nash equilibrium.
- Concepts: normal-form, nash.
- Read: [s1] chapter 1. Why this one.
- Time: about 6 hours.
- Checkpoint: find every equilibrium of a 2x2 game.

## Stage 2: Informed trading
- Goal: solve Kyle.
- Concepts: kyle
- Read: [s1] the Kyle chapter, and [s99] which isn't in the ledger.
- Time: about 6 hours.
- Checkpoint (the mission's Goal): model a market maker facing an informed trader.

## Skip unless
- [s1] the appendix, for the proofs.
"""


def roadmap_topic(agreed):
    topics.new("Game theory")
    folder = topics.folder("game-theory")
    (folder / "mission.md").write_text(LEARN_MISSION)
    (folder / "map.md").write_text(ROADMAP_MAP)
    (folder / "path.md").write_text(ROADMAP_PATH.format(agreed=agreed))
    ledger.add("game-theory", make(title="Game Theory for Applied Economists", url="https://example.edu/gibbons",
                                   year=1992, kind="book"), role="textbook")
    return folder


def test_study_waits_until_the_roadmap_is_agreed(puck_home):
    roadmap_topic("not yet")
    assert topics.agreed("game-theory") is False
    with pytest.raises(PuckError, match="isn't agreed yet"):
        topics.next_concept("game-theory")
    assert "Roadmap: not agreed yet" in topics.status_report("game-theory")
    path = topics.folder("game-theory") / "path.md"
    path.write_text(path.read_text().replace("Agreed: not yet", "Agreed: 2026-11-03"))
    assert topics.next_concept("game-theory")["id"] == "nash"


def test_a_topic_without_a_roadmap_is_not_blocked(topic):
    assert topics.agreed(topic) is None


def test_roadmap_page_shows_stages_statuses_and_sources(puck_home):
    folder = roadmap_topic("not yet")
    page = roadmap.render("game-theory")
    assert page == folder / "visuals" / "roadmap.html"
    text = page.read_text()
    assert "<title>Roadmap: game theory for finance</title>" in text
    assert "Draft roadmap: not agreed yet" in text
    assert text.count('<li class="stage') == 2 and "you are here" in text  # stage 1 is unfinished
    assert 'class="chip practised"' in text and "Kyle model" in text and "not in map.md" not in text
    assert 'href="https://example.edu/gibbons"' in text and "[s99]" in text  # unknown ids stay as text
    assert "1 of 3 concepts practised" in text and "about 12 hours" in text
    assert "http" not in text.split("<style>")[1].split("</style>")[0]  # no network in the page itself
    (folder / "path.md").write_text(ROADMAP_PATH.format(agreed="2026-11-03"))
    assert "Draft roadmap" not in roadmap.render("game-theory").read_text()


def test_roadmap_page_needs_a_written_path(topic):
    with pytest.raises(PuckError, match="path.md"):
        roadmap.render(topic)
