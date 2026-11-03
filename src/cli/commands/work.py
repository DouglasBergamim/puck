"""Commands the agent uses to run a task: tasks, notes and scratch."""

import json
from pathlib import Path

from core.tools.work import pack, scratch, tasks


def task_command(args) -> int:
    cwd = Path.cwd()
    if args.action == "start":
        task = tasks.start(args.goal, args.type, cwd, args.worktree, args.agent, args.topic)
        print(f"Task: {task['id']}")
        print(f"Folder: {task['folder']}")
        if task["worktree"]:
            print(f"Worktree: {task['cwd']} (open the session there)")
        if task["steps"]:
            print(tasks.checklist(task))
        workflow = tasks.lead(args.agent).workflow if args.agent else ()
        print(pack.pack(args.goal, workflow=workflow))
    elif args.action == "list":
        for task in tasks.all_tasks():
            if args.all or task["status"] == "open":
                print(tasks.summary_line(task))
    elif args.action == "show":
        task = tasks.resolve(args.task, cwd)
        print(json.dumps(task, indent=2) if args.json else tasks.checklist(task))
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
        for path in scratch.collect_garbage():  # old experiments go when any task closes
            print(f"Removed old scratch {path}")
    return 0


def note_command(args) -> int:
    tasks.note(tasks.resolve(args.task, Path.cwd()), args.type, args.text)
    return 0


def scratch_command(args) -> int:
    task = tasks.resolve(args.task, Path.cwd())
    if args.action == "new":
        print(scratch.new_experiment(task, args.name))
    else:
        scratch.log(task, args.hypothesis, args.command_run, args.result, args.verdict)
    return 0


def register(commands) -> None:
    task_parser = commands.add_parser("task", help="work with tasks")
    task_parser.set_defaults(run=task_command)
    task = task_parser.add_subparsers(dest="action", required=True)
    start = task.add_parser("start")
    start.add_argument("goal")
    start.add_argument("--type", default="build")
    start.add_argument("--worktree", action="store_true")
    start.add_argument("--agent", help="a lead whose workflow stages become the task's steps")
    start.add_argument("--topic", help="the topic the workflow runs on; its mission is the contract")
    listing = task.add_parser("list")
    listing.add_argument("--all", action="store_true")
    show = task.add_parser("show")
    show.add_argument("--task")
    show.add_argument("--json", action="store_true")
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
    note.set_defaults(run=note_command)

    space = commands.add_parser("scratch", help="disposable experiments")
    space.set_defaults(run=scratch_command)
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
