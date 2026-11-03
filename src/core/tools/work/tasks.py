"""Tasks: folders on disk plus a registry that works across sessions and worktrees."""

import re
import shutil
import subprocess
import time
from pathlib import Path

from core.common import paths, store
from core.common.errors import PuckError

TYPES = {"build", "learn", "research", "plan"}
FINDING_TYPES = ("procedure", "topic", "one-off")
OUTPUT_PREVIEW = 4_000


class TaskError(PuckError):
    """A problem with a task or its steps."""


def _registry(task_id: str) -> Path:
    return store.state_dir() / "tasks" / f"{store.safe_id(task_id)}.json"


def _git(cwd: Path, *args: str) -> str | None:
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def _slug(goal: str) -> str:
    words = re.findall(r"[a-z0-9]+", goal.lower())[:6]
    return "-".join(words) or "task"


def _exclude_puck(top: Path) -> None:
    """Keep .puck/ out of the project without touching its .gitignore."""
    exclude = Path(_git(top, "rev-parse", "--path-format=absolute", "--git-path", "info/exclude"))
    existing = exclude.read_text() if exclude.exists() else ""
    if ".puck/" not in existing.splitlines():
        store.append(exclude, ".puck/\n")


def _make_worktree(top: Path, task_id: str) -> Path:
    path = top / ".puck" / "worktrees" / task_id
    if _git(top, "worktree", "add", "-q", "-b", f"puck/{task_id}", str(path)) is None:
        raise TaskError(f"git worktree add failed for {task_id}; a commit must exist first.")
    return path


def start(goal: str, kind: str, cwd: Path, worktree: bool = False) -> dict:
    if kind not in TYPES:
        raise TaskError(f"--type must be one of {sorted(TYPES)}")
    top_text = _git(cwd, "rev-parse", "--show-toplevel")
    if worktree and not top_text:
        raise TaskError("--worktree needs a git repository.")
    stem = f"{time.strftime('%Y-%m-%d')}-{_slug(goal)}"
    with store.locked("tasks"):
        task_id, number = stem, 1
        while _registry(task_id).exists():
            number += 1
            task_id = f"{stem}-{number}"
        work = cwd
        if top_text:
            top = Path(top_text)
            _exclude_puck(top)
            work = _make_worktree(top, task_id) if worktree else cwd
            root = (Path(_git(work, "rev-parse", "--show-toplevel")) / ".puck" / "tasks")
        else:
            root = store.state_dir() / "tasks"
        folder = root / task_id
        (folder / "scratch" / "outputs").mkdir(parents=True)
        (folder / "scratch" / "experiments").mkdir()
        (folder / "scratch" / "drafts").mkdir()
        (folder / "findings.md").touch()
        (folder / "scratch" / "LOG.md").touch()
        shutil.copy(paths.templates() / "SPEC.md", folder / "SPEC.md")
        task = {
            "schema": 1, "id": task_id, "goal": goal, "type": kind, "status": "open",
            "cwd": str(work.resolve()), "folder": str(folder), "worktree": worktree,
            "project": Path(top_text).name if top_text else None,
            "started": int(time.time()), "closed": None, "nudged": False, "steps": [],
        }
        save(task)
    return task


def load(task_id: str) -> dict:
    task = store.read_json(_registry(task_id))
    if task is None:
        raise TaskError(f"No task '{task_id}'. Run `puck task list`.")
    return task


def save(task: dict) -> None:
    store.write_json(_registry(task["id"]), task)
    store.write_json(Path(task["folder"]) / "progress.json", {
        key: task[key] for key in ("schema", "id", "goal", "type", "status", "steps")
    })


def all_tasks() -> list[dict]:
    directory = store.state_dir() / "tasks"
    tasks = (store.read_json(path) for path in sorted(directory.glob("*.json")))
    return [task for task in tasks if task]


def open_for(cwd: Path) -> list[dict]:
    """Open tasks at or above this directory, nearest first; a worktree beats its repo."""
    here = cwd.resolve()
    matches = [t for t in all_tasks() if t["status"] == "open" and here.is_relative_to(t["cwd"])]
    nearest = max((len(t["cwd"]) for t in matches), default=0)
    return [t for t in matches if len(t["cwd"]) == nearest]


def resolve(task_id: str | None, cwd: Path) -> dict:
    """Use the given ID, or the only open task for this directory."""
    if task_id:
        return load(task_id)
    open_here = open_for(cwd)
    if len(open_here) == 1:
        return open_here[0]
    if not open_here:
        raise TaskError("No open task here. Pass --task or run `puck task start`.")
    raise TaskError("Several open tasks here; pass --task: " + ", ".join(t["id"] for t in open_here))


def note(task: dict, kind: str, text: str) -> None:
    if kind not in FINDING_TYPES:
        raise TaskError(f"--type must be one of {list(FINDING_TYPES)}")
    line = " ".join(text.split())
    store.append(Path(task["folder"]) / "findings.md", f"- [{kind}] {line}\n")


def add_step(task_id: str, description: str, check: str) -> str:
    with store.locked(f"task-{task_id}"):
        task = load(task_id)
        step_id = f"s{len(task['steps']) + 1}"
        task["steps"].append({
            "id": step_id, "desc": description, "check": check, "passes": False, "evidence": None,
        })
        save(task)
    return step_id


def run_command(command: str, cwd: Path | str, timeout: int | None = None) -> tuple[int, str]:
    """Run a check command in a shell. Returns (exit code, stdout and stderr)."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        return 124, f"Timed out after {timeout}s.\n{error.stdout or ''}{error.stderr or ''}"
    return result.returncode, result.stdout + result.stderr


def run_check(task_id: str, step_id: str) -> tuple[bool, str]:
    """Run a step's check command. Only a real exit 0 can mark a step passed."""
    task = load(task_id)
    step = next((s for s in task["steps"] if s["id"] == step_id), None)
    if step is None:
        raise TaskError(f"No step {step_id}. Steps: {[s['id'] for s in task['steps']]}")
    code, output = run_command(step["check"], task["cwd"])
    evidence = Path(task["folder"]) / "scratch" / "outputs" / f"check-{step_id}.txt"
    evidence.write_text(f"$ {step['check']}\nexit {code}\n{output}")
    with store.locked(f"task-{task_id}"):
        task = load(task_id)
        step = next(s for s in task["steps"] if s["id"] == step_id)
        step["passes"] = code == 0
        step["evidence"] = str(evidence)
        save(task)
    return step["passes"], output[-OUTPUT_PREVIEW:]


def claim_nudge(task_id: str) -> bool:
    """True the first time only, so the stop hook can never loop."""
    with store.locked(f"task-{task_id}"):
        task = load(task_id)
        if task["nudged"]:
            return False
        task["nudged"] = True
        save(task)
    return True


def checklist(task: dict) -> str:
    """The plan at a glance: what it holds, and what's done or not."""
    done = sum(s["passes"] for s in task["steps"])
    lines = [f"Plan {task['id']} [{task['status']}]: {task['goal']}",
             f"{done}/{len(task['steps'])} done. Folder: {task['folder']}"]
    lines += [f"[{'x' if s['passes'] else ' '}] {s['id']} {s['desc']}" for s in task["steps"]]
    if not task["steps"]:
        lines.append("No steps yet. Add them with `puck task step`.")
    return "\n".join(lines)


def ready_to_close(task: dict) -> bool:
    return task["status"] == "open" and bool(task["steps"]) and all(s["passes"] for s in task["steps"])


def close(task_id: str, outcome: str) -> Path:
    if outcome not in {"done", "partial", "abandoned"}:
        raise TaskError("--outcome must be done, partial or abandoned")
    with store.locked(f"task-{task_id}"):
        task = load(task_id)
        folder = Path(task["folder"])
        failing = [s["id"] for s in task["steps"] if not s["passes"]]
        if outcome == "done" and (failing or not task["steps"]):
            detail = f"steps not passing: {failing}" if failing else "it has no acceptance checks"
            raise TaskError(f"Can't close as done: {detail}. Fix it, or use --outcome partial.")
        findings = (folder / "findings.md").read_text().strip()
        retro = folder / "retro.md"
        if findings and not retro.exists():
            raise TaskError("Findings exist but retro.md is missing. Run the retro agent first.")
        if not retro.exists():
            retro.write_text(f"# Retro: {task_id}\n\nOutcome: {outcome}\n\nNo findings.\n")
        project = task["project"] or "personal"
        archive = paths.retros() / f"{store.safe_id(project)}-{task_id}.md"
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(retro, archive)
        task["status"] = "closed"
        task["outcome"] = outcome
        task["closed"] = int(time.time())
        save(task)
    return archive


def summary_line(task: dict) -> str:
    passed = sum(s["passes"] for s in task["steps"])
    where = "worktree " if task["worktree"] else ""
    return (f"{task['id']}  {task['status']}  {task['type']}  steps {passed}/{len(task['steps'])}  "
            f"{where}{task['cwd']}")
