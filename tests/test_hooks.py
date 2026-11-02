import json

import pytest

from cli import anchors, hooks

CLAUDE_TOOL = {
    "session_id": "s1", "cwd": "/w", "tool_name": "Bash",
    "tool_input": {"command": "pytest /w/tests/test_a.py"},
    "tool_response": {"stdout": "ValueError: boom at abc1234"},
}
COPILOT_TOOL = {
    "sessionId": "s2", "cwd": "/w", "toolName": "bash",
    "toolArgs": '{"command": "pytest /w/tests/test_b.py"}',
    "toolResult": {"resultType": "success", "textResultForLlm": "see https://example.com/x"},
}


def call(hook, event, host, payload):
    output = hooks.run(hook, event, host, json.dumps(payload))
    return json.loads(output) if output else None


def test_tools_normalise_to_capabilities(puck_home):
    from cli import hosts

    config = hosts.load()
    assert hooks.normalise(config["claude"], "post-tool", CLAUDE_TOOL)["tool"]["name"] == "search"
    assert hooks.normalise(config["copilot-cli"], "post-tool", COPILOT_TOOL)["session_id"] == "s2"


def test_anchors_are_recorded_from_both_hosts(puck_home):
    call("anchors", "post-tool", "claude", CLAUDE_TOOL)
    call("anchors", "post-tool", "copilot-cli", COPILOT_TOOL)
    claude = anchors.checkpoint_path("s1").read_text()
    copilot = anchors.checkpoint_path("s2").read_text()
    assert "/w/tests/test_a.py" in claude and "abc1234" in claude and "ValueError" in claude
    assert "https://example.com/x" in copilot and "/w/tests/test_b.py" in copilot


def test_uuids_and_path_segments_are_not_shas():
    text = "/tmp/0a302195-795f-46e3-8772-48c23953e87e/notes.txt and id 0a302195-795f-46e3"
    assert not [value for kind, value in anchors.extract(text) if kind == "sha"]
    assert ("sha", "abc1234") in anchors.extract("fixed in abc1234.")


def test_session_start_injects_a_pointer_in_each_format(puck_home):
    claude = call("resume", "session-start", "claude", {"session_id": "s1", "source": "startup"})
    copilot = call("resume", "session-start", "copilot-cli", {"sessionId": "s2", "source": "new"})
    assert claude["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "Puck is active" in claude["hookSpecificOutput"]["additionalContext"]
    assert "Puck is active" in copilot["additionalContext"]


def test_claude_compact_start_reinjects_checkpoint(puck_home):
    call("pack", "prompt", "claude", {"session_id": "s1", "prompt": "fix the login bug"})
    call("compact-mark", "pre-compact", "claude", {"session_id": "s1"})
    output = call("resume", "session-start", "claude", {"session_id": "s1", "source": "compact"})
    assert "fix the login bug" in output["hookSpecificOutput"]["additionalContext"]
    assert call("anchors", "post-tool", "claude", CLAUDE_TOOL) is None


def test_copilot_next_tool_result_carries_checkpoint_once(puck_home):
    call("pack", "prompt", "copilot-cli", {"sessionId": "s2", "prompt": "fix the login bug"})
    call("compact-mark", "pre-compact", "copilot-cli", {"sessionId": "s2"})
    first = call("anchors", "post-tool", "copilot-cli", COPILOT_TOOL)
    second = call("anchors", "post-tool", "copilot-cli", COPILOT_TOOL)
    assert "fix the login bug" in first["additionalContext"]
    assert second is None


def test_payload_stays_under_the_hard_limit(puck_home):
    for number in range(2000):
        anchors.record_anchors("s1", f"/w/file_{number}.py")
    call("compact-mark", "pre-compact", "claude", {"session_id": "s1"})
    output = call("resume", "session-start", "claude", {"session_id": "s1", "source": "compact"})
    assert len(output["hookSpecificOutput"]["additionalContext"]) < hooks.PAYLOAD_LIMIT


@pytest.mark.parametrize("payload", ["not json", "[1, 2]"])
def test_bad_payload_fails_open_and_logs(puck_home, payload):
    assert hooks.run("anchors", "post-tool", "claude", payload) == ""
    assert (puck_home / "state" / "hooks.log").exists()
