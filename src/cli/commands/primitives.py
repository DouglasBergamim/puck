"""Commands you run on Puck itself: setup, status, lint, build and skills."""

import argparse
import json
import os
import sys
from pathlib import Path

import adapters
from core.common import store
from core.primitives import agents, build, install, lint, skills
from core.tools import AGENT_COMMANDS
from core.tools.work import tasks


def status(args) -> int:
    info = {
        "home": str(store.home()),
        "hosts": {name: adapter.tier for name, adapter in adapters.ADAPTERS.items()},
        "open_tasks": sum(t["status"] == "open" for t in tasks.all_tasks()),
    }
    if args.json:
        print(json.dumps(info))
    else:
        print(f"Puck home: {info['home']}")
        print("Hosts: " + ", ".join(f"{k} ({v})" for k, v in info["hosts"].items()))
        print(f"Open tasks: {info['open_tasks']}")
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


def run(args) -> int:
    """Rebuild, then start the host with Puck loaded, in the current folder."""
    if args.host and args.host not in adapters.ADAPTERS:
        args.rest, args.host = [args.host, *args.rest], None  # `puck run "<prompt>"`
    adapter = adapters.get(args.host) if args.host else adapters.primary()
    if run_lint():
        print("Not starting: fix the lint errors above.", file=sys.stderr)
        return 1
    package = build.build_adapter(adapter, store.home())
    command = adapter.launch_command(package, store.home(), AGENT_COMMANDS, tuple(args.rest))
    if command is None:
        print(f"{adapter.name} has no launcher. Point it at {package}.", file=sys.stderr)
        return 1
    os.execvp(command[0], command)


def install_command(args) -> int:
    """Load Puck in every session of the host, or take it out again."""
    adapter = adapters.get(args.host) if args.host else adapters.primary()
    if args.action == "install" and run_lint():
        print("Not installing: fix the lint errors above.", file=sys.stderr)
        return 1
    change = install.install if args.action == "install" else install.uninstall
    for line in change(adapter, store.home(), Path.home(), AGENT_COMMANDS):
        print(line)
    if args.action == "install":
        print(f"Done. New {adapter.title} sessions start with Puck loaded.")
    return 0


def skill_command(args) -> int:
    if args.action == "new":
        print(skills.new(args.name, args.description, args.origin))
    elif args.action == "promote":
        print(f"Promoted {skills.promote(args.name, not args.no_evals)}.")
    return 0


def agent_command(args) -> int:
    print(agents.new(args.name, args.mode, args.description))
    return 0


def register(commands) -> None:
    status_parser = commands.add_parser("status", help="show Puck's state")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(run=status)
    commands.add_parser("lint", help="check skills, agents, hooks and budgets").set_defaults(run=run_lint)
    commands.add_parser("build", help="lint, then generate per-host packages").set_defaults(run=run_build)
    start = commands.add_parser(
        "run", help=f"rebuild, then start the host with Puck loaded (default: {adapters.PRIMARY})",
        description="Anything after the host is passed to it, so `puck run \"<first message>\"` "
                    "starts with that message.")
    start.add_argument("host", nargs="?", help=f"one of: {', '.join(adapters.ADAPTERS)}")
    start.add_argument("rest", nargs=argparse.REMAINDER)
    start.set_defaults(run=run)
    for action, help_text in (("install", "load Puck in every session of a host (default: %s)"),
                              ("uninstall", "undo install for a host (default: %s)")):
        parser = commands.add_parser(action, help=help_text % adapters.PRIMARY)
        parser.add_argument("host", nargs="?", choices=sorted(adapters.ADAPTERS))
        parser.set_defaults(run=install_command, action=action)

    skill_parser = commands.add_parser("skill", help="manage skills")
    skill_parser.set_defaults(run=skill_command)
    skill = skill_parser.add_subparsers(dest="action", required=True)
    new = skill.add_parser("new")
    new.add_argument("name")
    new.add_argument("--description", required=True)
    new.add_argument("--origin", required=True)
    promote = skill.add_parser("promote")
    promote.add_argument("name")
    promote.add_argument("--no-evals", action="store_true")

    agent_parser = commands.add_parser("agent", help="manage agents")
    agent_parser.set_defaults(run=agent_command)
    agent = agent_parser.add_subparsers(dest="action", required=True)
    new_agent = agent.add_parser("new")
    new_agent.add_argument("name")
    new_agent.add_argument("--mode", required=True, choices=sorted(agents.TEMPLATES))
    new_agent.add_argument("--description", required=True)
