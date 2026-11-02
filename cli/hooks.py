"""Normalised hook entry point: `puck hook <id> --host <name>`.

Shims convert a host payload to one event shape, handlers return one result
shape, and the shim maps it back. Handlers never touch host formats. Failures
are logged and swallowed, because hooks are helpers and must fail open.
"""

import json
import re
import sys
import time
import traceback

from cli import anchors, hosts, store, tasks

PAYLOAD_LIMIT = 10_000


def normalise(host: dict, event: str, raw: dict) -> dict:
    if host["payload"] == "camel":
        tool_name = raw.get("toolName")
        tool_input = raw.get("toolArgs")
        result = raw.get("toolResult") or {}
        output = result.get("textResultForLlm") if isinstance(result, dict) else result
        session = raw.get("sessionId")
    else:
        tool_name = raw.get("tool_name")
        tool_input = raw.get("tool_input")
        output = raw.get("tool_response")
        session = raw.get("session_id")
    return {
        "event": event,
        "host": host["name"],
        "session_id": store.safe_id(session or ""),
        "cwd": raw.get("cwd"),
        "tool": {
            "name": hosts.canonical_tool(host, tool_name),
            "input": tool_input,
            "output": output,
        } if tool_name else None,
        "prompt": raw.get("prompt"),
        "source": raw.get("source"),
        "stop_hook_active": bool(raw.get("stop_hook_active")),
    }


def _session_path(session_id: str):
    return store.state_dir() / "sessions" / f"{session_id}.json"


def _session(event: dict) -> dict:
    path = _session_path(event["session_id"])
    with store.locked(f"session-{event['session_id']}"):
        session = store.read_json(path)
        if session is None:
            session = {
                "session_id": event["session_id"],
                "host": event["host"],
                "cwd": event["cwd"],
                "started": int(time.time()),
                "task": None,
                "compacted": False,
            }
            store.write_json(path, session)
    return session


def _set_compacted(session_id: str, value: bool) -> None:
    path = _session_path(session_id)
    with store.locked(f"session-{session_id}"):
        session = store.read_json(path) or {"session_id": session_id, "task": None}
        session["compacted"] = value
        store.write_json(path, session)


def _resume_context(event: dict) -> str:
    return (_task_pointer(event) + "\n" + anchors.render(event["session_id"])).strip()


def _task_pointer(event: dict) -> str:
    session = store.read_json(_session_path(event["session_id"])) or {}
    if not session.get("task"):
        return ""
    task = tasks.load(session["task"])
    return f"Open task {task['id']}: {task['goal']}. Folder: {task['folder']}."


def _bind_task(event: dict, tool_input: str, tool_output: str) -> None:
    """Bind only from a real start command, so file or web text can't do it."""
    match = re.search(rf"{tasks.MARKER} ([\w.-]+)", tool_output)
    if not match or "puck task start" not in tool_input:
        return
    tasks.bind_session(match.group(1), event["session_id"], event["host"])
    path = _session_path(event["session_id"])
    with store.locked(f"session-{event['session_id']}"):
        session = store.read_json(path) or {"session_id": event["session_id"]}
        session["task"] = match.group(1)
        store.write_json(path, session)


def _metric(event: dict, **values) -> None:
    record = {"ts": int(time.time()), "session": event["session_id"], "host": event["host"], **values}
    store.append(store.state_dir() / "metrics.jsonl", json.dumps(record) + "\n")


def resume(event: dict) -> dict:
    _session(event)
    if event["source"] == "compact":
        _set_compacted(event["session_id"], False)
        context = _resume_context(event)
        _metric(event, kind="inject", chars=len(context))
        return {"context": context}
    return {"context": f"Puck is active. Home: {store.home()}. Run `puck status` for details."}


def pack(event: dict) -> dict:
    _session(event)
    anchors.record_prompt(event["session_id"], event["prompt"] or "")
    return {}


def anchor(event: dict) -> dict:
    session = _session(event)
    tool = event["tool"] or {}
    tool_input, tool_output = _text(tool.get("input")), _text(tool.get("output"))
    anchors.record_anchors(event["session_id"], tool_input + "\n" + tool_output)
    _bind_task(event, tool_input, tool_output)
    _metric(event, kind="tool", tool=tool.get("name"), chars=len(tool_output))
    if session.get("compacted"):
        # Copilot has no post-compact event, so the next tool result carries it.
        _set_compacted(event["session_id"], False)
        context = _resume_context(event)
        _metric(event, kind="inject", chars=len(context))
        return {"context": context}
    return {}


def compact_mark(event: dict) -> dict:
    _session(event)
    _set_compacted(event["session_id"], True)
    return {}


def close_guard(event: dict) -> dict:
    """Once per task, nudge an agent that finished its checks but never closed."""
    session = _session(event)
    if event["stop_hook_active"] or not session.get("task"):
        return {}
    task = tasks.load(session["task"])
    if not tasks.ready_to_close(task):
        return {}
    guard = store.state_dir() / "close-guard" / store.safe_id(task["id"])
    try:
        guard.parent.mkdir(parents=True, exist_ok=True)
        guard.touch(exist_ok=False)
    except FileExistsError:
        return {}
    return {"decision": "block", "reason": (
        f"Task {task['id']} passes its checks but is still open. Run the retro agent if "
        f"findings exist, then `puck task close --task {task['id']} --outcome done`, "
        "and list any proposals for the user.")}


def _text(value) -> str:
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value)


HANDLERS = {
    "resume": resume, "pack": pack, "anchors": anchor,
    "compact-mark": compact_mark, "close-guard": close_guard,
}


def render(host: dict, event: dict, result: dict) -> dict | None:
    """Map a result back to the host's output format."""
    output: dict = {}
    if result.get("decision") == "block":
        output.update(decision="block", reason=result.get("reason", ""))
    context = result.get("context")
    if context:
        context = context[:PAYLOAD_LIMIT]
        if host["output"] == "flat":
            output["additionalContext"] = context
        else:
            output["hookSpecificOutput"] = {
                "hookEventName": host["hook_events"][event["event"]],
                "additionalContext": context,
            }
    return output or None


def run(hook_id: str, event_name: str, host_name: str, payload: str) -> str:
    """Run one hook. Returns stdout text and never raises."""
    try:
        host = hosts.load()[host_name]
        event = normalise(host, event_name, json.loads(payload or "{}"))
        output = render(host, event, HANDLERS[hook_id](event))
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
