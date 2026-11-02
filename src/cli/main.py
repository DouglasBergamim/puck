"""The puck command line: builds the parser and dispatches. Commands live in cli/commands/."""

import argparse
import sys

from cli.commands import learning, primitives, work
from core.common.errors import PuckError
from core import hooks

AREAS = (primitives, work, learning)


def run_hook(args) -> int:
    return hooks.main(args.hook_id, args.event, args.host)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="puck")
    commands = root.add_subparsers(dest="command", required=True)
    hook = commands.add_parser("hook", help="entry point for host hooks")
    hook.add_argument("hook_id", choices=sorted(hooks.HANDLERS))
    hook.add_argument("--event", required=True)
    hook.add_argument("--host", required=True)
    hook.set_defaults(run=run_hook)
    for area in AREAS:
        area.register(commands)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.run(args)
    except PuckError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
