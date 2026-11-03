"""Commands the agent uses to research and teach: topics, sources, wiki, sessions, exercises."""

import json
import sys
import webbrowser
from pathlib import Path

from core.common.errors import PuckError
from core.tools.learning import exercises, kb, roadmap, sources, topics
from core.tools.learning.sources import ledger, verify
from core.tools.learning.sources.record import KINDS, make


def _report(errors: list[str], warnings: list[str], ok: str) -> int:
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    if not errors:
        print(ok)
    return 1 if errors else 0


def _read(file: str) -> str:
    return sys.stdin.read() if file == "-" else Path(file).read_text()


def topic_command(args) -> int:
    if args.action == "new":
        print(topics.new(args.name, args.kind))
    elif args.action == "list":
        for name in topics.all_topics():
            print(name)
    elif args.action == "check":
        return check_topic(args)
    return 0


def check_topic(args) -> int:
    """One validator per topic: the named files, the sources, then the wiki."""
    required = [k.strip() for k in args.has.split(",")] if args.has else []
    errors = topics.check(args.topic, required)
    # With --has, an empty ledger fails only through `sources`, which topics.check reports.
    source_errors, warnings = verify.verify(args.topic, not args.no_links, require_sources=not required)
    wiki_errors, wiki_warnings = kb.lint(args.topic)
    return _report(errors + source_errors + wiki_errors, warnings + wiki_warnings, f"{args.topic}: check passes")


def sources_command(args) -> int:
    if args.action == "search":
        found, warnings = sources.search(args.query, args.kind, args.limit)
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if args.json:
            print(json.dumps(found, indent=2))
        else:
            for record in found:
                print(sources.one_line(record))
            if not found:
                print("No results.")
        return 0 if found or not warnings else 1
    if args.action == "graph":
        for record in sources.graph(args.ref, args.direction, args.limit, args.since):
            print(sources.one_line(record))
        return 0
    if args.action == "add":
        if args.ref:
            record = sources.resolve(args.ref)
            if args.kind:
                record["kind"] = args.kind
        elif args.url and args.title:
            record = make(kind=args.kind or "web", title=args.title, url=args.url,
                          authors=args.author or [], year=args.year)
        else:
            raise PuckError("Give a reference (e.g. openalex:W123), or --url with --title for a web page.")
        source_id, created = ledger.add(args.topic, record, args.role, args.why, args.quote, args.group)
        print(f"{source_id} {'added' if created else 'already there, updated'}: {record['title']}")
        if args.fetch:
            path, notes = verify.fetch(args.topic, source_id)
            for note in notes:
                print(f"note: {note}")
            print(path)
        return 0
    if args.action == "list":
        for source in ledger.load(args.topic):
            role = f"[{source['role']}] " if source.get("role") else ""
            print(f"{source['id']}  {role}{source.get('year') or 'n.d.'}  {source['title']}")
        return 0
    # fetch
    if args.file:
        if not args.origin:
            raise PuckError("--file needs --origin: where the text came from, e.g. a URL and pages.")
        print(verify.excerpt(args.topic, args.id, _read(args.file), args.origin, args.force))
        return 0
    path, notes = verify.fetch(args.topic, args.id, args.force)
    for note in notes:
        print(f"note: {note}")
    print(path)
    return 0


def learn_command(args) -> int:
    if args.action == "status":
        print(topics.status_report(args.topic))
    elif args.action == "next":
        upcoming = topics.next_concept(args.topic)
        print(json.dumps(upcoming) if upcoming else "Nothing ready: every concept is can-explain, or map.md has none.")
    elif args.action == "record":
        statuses = {}
        for item in args.status or []:
            concept_id, _, status = item.partition("=")
            if not status:
                raise PuckError(f"--status takes concept=status, got '{item}'")
            statuses[concept_id.strip()] = status.strip()
        print(topics.record(args.topic, _read(args.file), statuses))
    elif args.action == "roadmap":
        page = roadmap.render(args.topic)
        if not args.no_open:
            webbrowser.open(page.as_uri())
        print(page)
    elif args.action == "open":
        path = Path(args.path).expanduser().resolve()
        if not path.exists():
            raise PuckError(f"No file {path}.")
        webbrowser.open(path.as_uri())
        print(f"Opened {path}")
    elif args.action == "check":
        passed, output = exercises.check(args.topic, args.id)
        print("PASS" if passed else "FAIL")
        print(output)
        return 0 if passed else 1
    return 0


def register(commands) -> None:
    topic_parser = commands.add_parser("topic", help="study topics")
    topic_parser.set_defaults(run=topic_command)
    topic = topic_parser.add_subparsers(dest="action", required=True)
    topic_new = topic.add_parser("new", help="learn: a subject to learn; research: a question to answer")
    topic_new.add_argument("name")
    topic_new.add_argument("--kind", default="learn", choices=topics.KINDS)
    topic.add_parser("list")
    check = topic.add_parser(
        "check", help="fail unless the named files are written, sources resolve and quotes match raw/, "
                      "and every wiki claim traces to a source")
    check.add_argument("topic")
    check.add_argument("--has", help="comma-separated: mission, map, path, sources, report")
    check.add_argument("--no-links", action="store_true", help="skip network checks")

    source_parser = commands.add_parser(
        "sources", help="find, record and verify papers and books",
        description="Optional keys, from the environment: OPENALEX_API_KEY, S2_API_KEY.")
    source_parser.set_defaults(run=sources_command)
    source = source_parser.add_subparsers(dest="action", required=True)
    search = source.add_parser("search")
    search.add_argument("query")
    search.add_argument("--kind", default="any", choices=sorted(sources.BY_KIND))
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--json", action="store_true")
    graph = source.add_parser("graph", help="references: what it builds on; cited-by: what builds on it")
    graph.add_argument("ref")
    graph.add_argument("--direction", default="references", choices=["references", "cited-by"])
    graph.add_argument("--limit", type=int, default=15)
    graph.add_argument("--since", type=int, help="cited-by only: earliest publication year")
    add = source.add_parser("add")
    add.add_argument("topic")
    add.add_argument("ref", nargs="?", help="openalex:W…, s2:…, arxiv:…, ol:OL…W or doi:10.…")
    add.add_argument("--url")
    add.add_argument("--title")
    add.add_argument("--author", action="append")
    add.add_argument("--year", type=int)
    add.add_argument("--kind", choices=KINDS)
    add.add_argument("--role", choices=ledger.ROLES)
    add.add_argument("--why", default="")
    add.add_argument("--quote", default="", help="a passage copied exactly from the source")
    add.add_argument("--group", default="", help="independence group: sources that echo one origin share it")
    add.add_argument("--fetch", action="store_true", help="also save its text to raw/, as `sources fetch` does")
    source.add_parser("list").add_argument("topic")
    fetch = source.add_parser(
        "fetch", help="save a source's text to raw/: its abstract or page, or with --file text you read yourself")
    fetch.add_argument("topic")
    fetch.add_argument("id")
    fetch.add_argument("--file", help="text you read yourself, e.g. from a PDF; a file, or - for stdin")
    fetch.add_argument("--origin", help="with --file: where the text came from, e.g. URL and pages")
    fetch.add_argument("--force", action="store_true")

    learn_parser = commands.add_parser("learn", help="study sessions")
    learn_parser.set_defaults(run=learn_command)
    learn = learn_parser.add_subparsers(dest="action", required=True)
    learn.add_parser("status").add_argument("topic")
    learn.add_parser("next").add_argument("topic")
    record = learn.add_parser("record", help="write the session record and update concept statuses")
    record.add_argument("topic")
    record.add_argument("--file", required=True, help="the record, or - for stdin")
    record.add_argument("--status", action="append", help="concept=status; repeatable")
    page = learn.add_parser("roadmap", help="write the topic's roadmap page from path.md, map.md and sources.json, "
                                           "and open it")
    page.add_argument("topic")
    page.add_argument("--no-open", action="store_true", help="only write the page")
    learn.add_parser("open", help="open an HTML visual in the browser").add_argument("path")
    exercise_check = learn.add_parser("check", help="run a code exercise's tests; only exit 0 passes")
    exercise_check.add_argument("topic")
    exercise_check.add_argument("id", help="the exercise folder name")
