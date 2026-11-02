"""Scratch space: disposable experiments that stay out of the real code."""

import re
import shutil
import time
from pathlib import Path

from cli import store, tasks

RETENTION_DAYS = 14


def new_experiment(task: dict, name: str) -> Path:
    root = Path(task["folder"]) / "scratch" / "experiments"
    slug = "-".join(re.findall(r"[a-z0-9]+", name.lower())) or "experiment"
    with store.locked(f"scratch-{task['id']}"):
        number = len(list(root.iterdir())) + 1
        path = root / f"{number:03d}-{slug}"
        path.mkdir(parents=True)
    return path


def log(task: dict, hypothesis: str, command: str, result: str, verdict: str) -> None:
    if verdict not in {"keep", "discard"}:
        raise tasks.TaskError("--verdict must be keep or discard")
    entry = f"- {hypothesis} | `{command}` | {result} | {verdict}\n"
    store.append(Path(task["folder"]) / "scratch" / "LOG.md", entry)


def collect_garbage(days: int = RETENTION_DAYS) -> list[Path]:
    """Delete scratch from tasks closed more than `days` ago."""
    cutoff = time.time() - days * 86_400
    removed = []
    for task in tasks.all_tasks():
        scratch = Path(task["folder"]) / "scratch"
        if task["status"] == "closed" and task["closed"] < cutoff and scratch.exists():
            shutil.rmtree(scratch)
            removed.append(scratch)
    return removed
