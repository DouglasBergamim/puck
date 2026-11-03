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
from core.common import paths, store
from core.common.model import Event, Result
from core.primitives import build
from core.tools.work import tasks

PAYLOAD_LIMIT = 10_000


def _open_plans(event: Event) -> list[dict]:
    return tasks.open_for(Path(event.cwd)) if event.cwd else []


def resume(event: Event) -> Result:
    """Give the rules and any open plan at session start and after compaction.

    Plugins can't carry instruction files, so this hook is how the rules arrive.
    """
    home = paths.home()
    parts = [build.load_instructions(home), f"Puck's home folder, written `$PUCK_HOME` in skills and agents, is `{home}`."]
    leads = [agent for agent in build.load_agents(home) if agent.mode == "lead"]
    if leads:
        names = ", ".join(f"{agent.name}" for agent in leads)
        parts.append(f"Agents the user can pick and talk to: {names}. Each is a skill of the same name. "
                     "When the user asks for one, load that skill and take its role in this conversation. "
                     "Never start one as a background agent.")
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
                "and show the user any skill drafts it made."))
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
