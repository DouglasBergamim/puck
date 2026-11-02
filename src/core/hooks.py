"""Hook entry point: `puck hook <id> --event <event> --host <name>`.

An adapter turns the harness payload into an Event, a handler returns a Result,
and the adapter maps it back. Handlers never see harness formats. Failures are
logged and swallowed, because hooks are helpers and must fail open.

History belongs to the harness. Hooks only keep the rules and the open plan in
front of the model. Plans come from the working directory, so worktrees stay apart.
"""

import dataclasses
import json
import sys
import time
import traceback
from pathlib import Path

import adapters
from core import build, paths, store, tasks
from core.model import Event, Result

PAYLOAD_LIMIT = 10_000


def _open_plans(event: Event) -> list[dict]:
    return tasks.open_for(Path(event.cwd)) if event.cwd else []


def resume(event: Event) -> Result:
    """Give the rules and any open plan at session start and after compaction.

    Plugins can't carry instruction files, so this hook is how the rules arrive.
    """
    parts = [build.load_instructions(paths.home())]
    parts += [tasks.checklist(plan) for plan in _open_plans(event)]
    return Result(context="\n\n".join(parts))


def close_guard(event: Event) -> Result:
    """Once per task, nudge an agent that finished its checks but never closed."""
    if event.already_forced:
        return Result()
    for task in _open_plans(event):
        if tasks.ready_to_close(task) and tasks.claim_nudge(task["id"]):
            return Result(decision="block", reason=(
                f"Task {task['id']} passes its checks but is still open. Run the retro agent "
                f"if findings exist, then `puck task close --task {task['id']} --outcome done`, "
                "and list any proposals for the user."))
    return Result()


HANDLERS = {"resume": resume, "close-guard": close_guard}


def run(hook_id: str, event_name: str, host_name: str, payload: str) -> str:
    """Run one hook. Returns stdout text and never raises."""
    try:
        adapter = adapters.get(host_name)
        event = adapter.parse_event(event_name, json.loads(payload or "{}"))
        result = HANDLERS[hook_id](event)
        if result.context:
            result = dataclasses.replace(result, context=result.context[:PAYLOAD_LIMIT])
        output = adapter.render_result(event, result)
        return json.dumps(output) if output else ""
    except Exception:
        store.append(
            store.state_dir() / "hooks.log",
            f"{time.strftime('%FT%T')} {hook_id} {host_name}\n{traceback.format_exc()}\n",
        )
        return ""


def main(hook_id: str, event_name: str, host_name: str) -> int:
    text = run(hook_id, event_name, host_name, sys.stdin.read())
    if text:
        print(text)
    return 0
