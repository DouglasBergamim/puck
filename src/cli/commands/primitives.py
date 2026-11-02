"""Commands you run on Puck itself: status, lint, build, skills and proposals."""

import json
import sys
from pathlib import Path

import adapters
from core.common import store
from core.primitives import build, lint, skills
from core.tools.work import tasks


def status(args) -> int:
    info = {
        "home": str(store.home()),
        "hosts": {name: adapter.tier for name, adapter in adapters.ADAPTERS.items()},
        "open_tasks": sum(t["status"] == "open" for t in tasks.all_tasks()),
        "proposals": len(skills.list_proposals()),
    }
    if args.json:
        print(json.dumps(info))
    else:
        print(f"Puck home: {info['home']}")
        print("Hosts: " + ", ".join(f"{k} ({v})" for k, v in info["hosts"].items()))
        print(f"Open tasks: {info['open_tasks']}")
        print(f"Proposals waiting: {info['proposals']}")
    return 0


def run_lint(args=None) -> int:
    errors = lint.lint_all()
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


def run_build(args) -> int:
    if run_lint():
        print("Build stopped: fix the lint errors above.", file=sys.stderr)
        return 1
    for path in build.build_all():
        print(path)
    return 0


def skill_command(args) -> int:
    if args.action == "new":
        print(skills.new(args.name, args.description, args.origin))
    elif args.action == "try":
        print(skills.try_draft(args.name))
    elif args.action == "promote":
        print(f"Promoted {skills.promote(args.name, not args.no_evals)}.")
    return 0


def proposal_command(args) -> int:
    if args.action == "add":
        body = Path(args.body_file).read_text() if args.body_file else args.body or ""
        print(skills.propose(args.kind, args.task, args.target, args.summary, body))
    elif args.action == "list":
        for item in skills.list_proposals():
            print(f"{item['id']}  [{item['kind']}]  {item['target']}: {item['summary']}")
    else:
        print(skills.resolve(args.id, args.action == "approve", not args.no_evals))
    return 0


def register(commands) -> None:
    status_parser = commands.add_parser("status", help="show Puck's state")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(run=status)
    commands.add_parser("lint", help="check skills, agents, hooks and budgets").set_defaults(run=run_lint)
    commands.add_parser("build", help="lint, then generate per-host packages").set_defaults(run=run_build)

    skill_parser = commands.add_parser("skill", help="manage skills")
    skill_parser.set_defaults(run=skill_command)
    skill = skill_parser.add_subparsers(dest="action", required=True)
    new = skill.add_parser("new")
    new.add_argument("name")
    new.add_argument("--description", required=True)
    new.add_argument("--origin", required=True)
    trial = skill.add_parser("try")
    trial.add_argument("name")
    promote = skill.add_parser("promote")
    promote.add_argument("name")
    promote.add_argument("--no-evals", action="store_true")

    proposal = commands.add_parser("proposal", help="changes waiting for the user")
    proposal.set_defaults(run=proposal_command)
    proposals = proposal.add_subparsers(dest="action", required=True)
    add = proposals.add_parser("add")
    add.add_argument("--kind", required=True)
    add.add_argument("--task", required=True)
    add.add_argument("--target", required=True)
    add.add_argument("--summary", required=True)
    add.add_argument("--body")
    add.add_argument("--body-file")
    proposals.add_parser("list")
    for name in ("approve", "reject"):
        resolve = proposals.add_parser(name)
        resolve.add_argument("id")
        resolve.add_argument("--no-evals", action="store_true")
