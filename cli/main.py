"""The puck command line."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from cli import anchors, build, context, hooks, hosts, lint, scratch, skills, store, tasks


def status(as_json: bool) -> int:
    root = store.home()
    info = {
        "home": str(root),
        "hosts": {name: config["tier"] for name, config in hosts.load(root).items()},
        "sessions_seen": len(list((store.state_dir() / "sessions").glob("*.json"))),
        "open_tasks": sum(t["status"] == "open" for t in tasks.all_tasks()),
        "proposals": len(skills.list_proposals()),
    }
    if as_json:
        print(json.dumps(info))
    else:
        print(f"Puck home: {info['home']}")
        print("Hosts: " + ", ".join(f"{k} ({v})" for k, v in info["hosts"].items()))
        print(f"Sessions seen: {info['sessions_seen']}")
        print(f"Open tasks: {info['open_tasks']}")
        print(f"Proposals waiting: {info['proposals']}")
    return 0


def run_lint() -> int:
    errors = lint.lint_all()
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


def run_build() -> int:
    if run_lint():
        print("Build stopped: fix the lint errors above.", file=sys.stderr)
        return 1
    for path in build.build_all():
        print(path)
    return 0


def metrics() -> int:
    """Context use so far: the evidence for or against a model proxy."""
    tools: dict[str, list[int]] = defaultdict(list)
    injected = 0
    path = store.state_dir() / "metrics.jsonl"
    for line in path.read_text().splitlines() if path.exists() else []:
        record = json.loads(line)
        if record["kind"] == "tool":
            tools[record["tool"]].append(record["chars"])
        else:
            injected += record["chars"]
    root = store.home()
    print(f"Listing cost per session: {lint.listing_chars(root)} chars")
    print(f"Injected by Puck: {injected} chars")
    print("Tool output by tool (calls, total chars, largest):")
    for name, sizes in sorted(tools.items(), key=lambda item: -sum(item[1])):
        print(f"  {name}: {len(sizes)}, {sum(sizes)}, {max(sizes)}")
    return 0


def task_command(args) -> int:
    cwd = Path.cwd()
    if args.action == "start":
        task = tasks.start(args.goal, args.type, cwd, args.worktree)
        print(f"{tasks.MARKER} {task['id']}")
        print(f"Folder: {task['folder']}")
        if task["worktree"]:
            print(f"Worktree: {task['cwd']} (open the session there)")
        print(context.pack(args.goal))
    elif args.action == "list":
        for task in tasks.all_tasks():
            if args.all or task["status"] == "open":
                print(tasks.summary_line(task))
    elif args.action == "show":
        print(json.dumps(tasks.resolve(args.task, cwd), indent=2))
    elif args.action == "step":
        task = tasks.resolve(args.task, cwd)
        print(tasks.add_step(task["id"], args.description, args.check))
    elif args.action == "check":
        task = tasks.resolve(args.task, cwd)
        passed, output = tasks.run_check(task["id"], args.step)
        print("PASS" if passed else "FAIL")
        print(output)
        return 0 if passed else 1
    elif args.action == "close":
        task = tasks.resolve(args.task, cwd)
        print(tasks.close(task["id"], args.outcome))
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


def scratch_command(args) -> int:
    if args.action == "gc":
        for path in scratch.collect_garbage():
            print(f"Removed {path}")
        return 0
    task = tasks.resolve(args.task, Path.cwd())
    if args.action == "new":
        print(scratch.new_experiment(task, args.name))
    else:
        scratch.log(task, args.hypothesis, args.command_run, args.result, args.verdict)
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="puck")
    commands = root.add_subparsers(dest="command", required=True)
    status_parser = commands.add_parser("status", help="show Puck's state")
    status_parser.add_argument("--json", action="store_true")
    commands.add_parser("lint", help="check skills, agents, hooks and budgets")
    commands.add_parser("build", help="lint, then generate per-host packages")
    commands.add_parser("metrics", help="show context use so far")
    checkpoint = commands.add_parser("checkpoint", help="print a session's checkpoint")
    checkpoint.add_argument("session_id")

    hook = commands.add_parser("hook", help="entry point for host hooks")
    hook.add_argument("hook_id", choices=sorted(hooks.HANDLERS))
    hook.add_argument("--event", required=True)
    hook.add_argument("--host", required=True)

    task = commands.add_parser("task", help="work with tasks").add_subparsers(dest="action", required=True)
    start = task.add_parser("start")
    start.add_argument("goal")
    start.add_argument("--type", default="build")
    start.add_argument("--worktree", action="store_true")
    listing = task.add_parser("list")
    listing.add_argument("--all", action="store_true")
    show = task.add_parser("show")
    show.add_argument("--task")
    step = task.add_parser("step")
    step.add_argument("description")
    step.add_argument("--check", required=True)
    step.add_argument("--task")
    check = task.add_parser("check")
    check.add_argument("step")
    check.add_argument("--task")
    close = task.add_parser("close")
    close.add_argument("--outcome", default="done")
    close.add_argument("--task")

    note = commands.add_parser("note", help="record a finding on a task")
    note.add_argument("text")
    note.add_argument("--type", required=True)
    note.add_argument("--task")

    skill = commands.add_parser("skill", help="manage skills").add_subparsers(dest="action", required=True)
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

    space = commands.add_parser("scratch", help="disposable experiments")
    spaces = space.add_subparsers(dest="action", required=True)
    experiment = spaces.add_parser("new")
    experiment.add_argument("name")
    experiment.add_argument("--task")
    entry = spaces.add_parser("log")
    entry.add_argument("--hypothesis", required=True)
    entry.add_argument("--command-run", required=True)
    entry.add_argument("--result", required=True)
    entry.add_argument("--verdict", required=True)
    entry.add_argument("--task")
    spaces.add_parser("gc")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "status":
            return status(args.json)
        if args.command == "lint":
            return run_lint()
        if args.command == "build":
            return run_build()
        if args.command == "metrics":
            return metrics()
        if args.command == "checkpoint":
            print(anchors.render(store.safe_id(args.session_id)) or "No checkpoint for that session.")
            return 0
        if args.command == "hook":
            return hooks.main(args.hook_id, args.event, args.host)
        if args.command == "note":
            tasks.note(tasks.resolve(args.task, Path.cwd()), args.type, args.text)
            return 0
        return {"task": task_command, "skill": skill_command, "proposal": proposal_command,
                "scratch": scratch_command}[args.command](args)
    except tasks.TaskError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
