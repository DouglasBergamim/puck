"""Commands the agent uses to research and teach: topics, sources, wiki, sessions, exercises."""

import json
import sys
import webbrowser
from pathlib import Path

from core.common.errors import PuckError
from core.tools.learning import exercises, kb, sources, topics
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
        print(topics.new(args.name))
    elif args.action == "list":
        for name in topics.all_topics():
            print(name)
    elif args.action == "show":
        print(topics.status_report(args.topic))
    elif args.action == "check":
        problems = topics.check(args.topic, [k.strip() for k in args.has.split(",")])
        return _report(problems, [], f"{args.topic}: has {args.has}")
    return 0


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
        return 0
    if args.action == "list":
        for source in ledger.load(args.topic):
            role = f"[{source['role']}] " if source.get("role") else ""
            print(f"{source['id']}  {role}{source.get('year') or 'n.d.'}  {source['title']}")
        return 0
    if args.action == "fetch":
        path, notes = verify.fetch(args.topic, args.id, args.force)
        for note in notes:
            print(f"note: {note}")
        print(path)
        return 0
    if args.action == "excerpt":
        print(verify.excerpt(args.topic, args.id, _read(args.file), args.origin, args.force))
        return 0
    errors, warnings = verify.verify(args.topic, not args.no_links)
    return _report(errors, warnings, f"{args.topic}: sources verified")


def kb_command(args) -> int:
    errors, warnings = kb.lint(args.topic)
    return _report(errors, warnings, f"{args.topic}: wiki passes")


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
    elif args.action == "open":
        path = Path(args.path).expanduser().resolve()
        if not path.exists():
            raise PuckError(f"No file {path}.")
        webbrowser.open(path.as_uri())
        print(f"Opened {path}")
    return 0


def exercise_command(args) -> int:
    passed, output = exercises.check(args.topic, args.id)
    print("PASS" if passed else "FAIL")
    print(output)
    return 0 if passed else 1


def register(commands) -> None:
    topic_parser = commands.add_parser("topic", help="study topics")
    topic_parser.set_defaults(run=topic_command)
    topic = topic_parser.add_subparsers(dest="action", required=True)
    topic.add_parser("new").add_argument("name")
    topic.add_parser("list")
    topic.add_parser("show").add_argument("topic")
    check = topic.add_parser("check", help="fail unless the named files are written")
    check.add_argument("topic")
    check.add_argument("--has", required=True, help="comma-separated: mission, map, path, sources")

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
    source.add_parser("list").add_argument("topic")
    fetch = source.add_parser("fetch", help="save the abstract or page text to raw/")
    fetch.add_argument("topic")
    fetch.add_argument("id")
    fetch.add_argument("--force", action="store_true")
    excerpt = source.add_parser("excerpt", help="save text you read yourself, e.g. from a PDF")
    excerpt.add_argument("topic")
    excerpt.add_argument("id")
    excerpt.add_argument("--file", required=True, help="a file, or - for stdin")
    excerpt.add_argument("--origin", required=True, help="where the text came from: URL and pages")
    excerpt.add_argument("--force", action="store_true")
    verify_parser = source.add_parser("verify", help="fail unless sources resolve and quotes match raw/")
    verify_parser.add_argument("topic")
    verify_parser.add_argument("--no-links", action="store_true", help="skip network checks")

    kb_parser = commands.add_parser("kb", help="the topic wiki")
    kb_parser.set_defaults(run=kb_command)
    kb_actions = kb_parser.add_subparsers(dest="action", required=True)
    kb_actions.add_parser("lint", help="fail unless every claim traces to a source").add_argument("topic")

    learn_parser = commands.add_parser("learn", help="study sessions")
    learn_parser.set_defaults(run=learn_command)
    learn = learn_parser.add_subparsers(dest="action", required=True)
    learn.add_parser("status").add_argument("topic")
    learn.add_parser("next").add_argument("topic")
    record = learn.add_parser("record", help="write the session record and update concept statuses")
    record.add_argument("topic")
    record.add_argument("--file", required=True, help="the record, or - for stdin")
    record.add_argument("--status", action="append", help="concept=status; repeatable")
    learn.add_parser("open", help="open an HTML visual in the browser").add_argument("path")

    exercise_parser = commands.add_parser("exercise", help="practice exercises")
    exercise_parser.set_defaults(run=exercise_command)
    exercise = exercise_parser.add_subparsers(dest="action", required=True)
    exercise_check = exercise.add_parser("check", help="run a code exercise's tests; only exit 0 passes")
    exercise_check.add_argument("topic")
    exercise_check.add_argument("id")
