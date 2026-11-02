import json

import pytest

from core import hooks, tasks


def call(hook, event, host, payload):
    output = hooks.run(hook, event, host, json.dumps(payload))
    return json.loads(output) if output else None


def plan(cwd, goal="fix the login bug"):
    task = tasks.start(goal, "build", cwd)
    tasks.add_step(task["id"], "Tests pass", "true")
    tasks.add_step(task["id"], "Docs updated", "false")
    tasks.run_check(task["id"], "s1")
    return task


def test_rules_arrive_without_a_plan(puck_home, tmp_path):
    output = call("resume", "session-start", "claude", {"cwd": str(tmp_path)})
    text = output["hookSpecificOutput"]["additionalContext"]
    assert "Load the `task` skill" in text and "Plan " not in text


def test_rules_return_after_compaction(puck_home, tmp_path):
    output = call("resume", "session-start", "claude", {"cwd": str(tmp_path), "source": "compact"})
    assert "Load the `task` skill" in output["hookSpecificOutput"]["additionalContext"]


def test_rules_and_plan_fit_the_payload_limit(puck_home, tmp_path):
    plan(tmp_path)
    output = call("resume", "session-start", "copilot-cli", {"cwd": str(tmp_path)})
    assert len(output["additionalContext"]) < hooks.PAYLOAD_LIMIT


def test_session_start_shows_the_plan_in_each_format(puck_home, tmp_path):
    plan(tmp_path)
    claude = call("resume", "session-start", "claude", {"cwd": str(tmp_path), "source": "compact"})
    text = claude["hookSpecificOutput"]["additionalContext"]
    assert claude["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "[x] s1 Tests pass" in text and "[ ] s2 Docs updated" in text
    copilot = call("resume", "session-start", "copilot-cli", {"cwd": str(tmp_path)})
    assert "1/2 done" in copilot["additionalContext"]


def test_subdirectory_finds_the_plan(puck_home, tmp_path):
    plan(tmp_path)
    inner = tmp_path / "a" / "b"
    inner.mkdir(parents=True)
    assert call("resume", "session-start", "claude", {"cwd": str(inner)}) is not None


@pytest.mark.parametrize("payload", ["not json", "[1, 2]"])
def test_bad_payload_fails_open_and_logs(puck_home, payload):
    assert hooks.run("resume", "session-start", "claude", payload) == ""
    assert (puck_home / "state" / "hooks.log").exists()
