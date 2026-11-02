import json
import os
import subprocess
import time

import pytest

from cli import context, hooks, scratch, skills, store, tasks
from tests.test_hooks import call
from tests.test_build_and_lint import template, add_skill


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "proj"
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
    return path


def test_start_creates_task_excluded_from_git(puck_home, repo):
    task = tasks.start("fix the login bug", "build", repo)
    folder = repo / ".puck" / "tasks" / task["id"]
    assert (folder / "SPEC.md").exists() and (folder / "scratch" / "LOG.md").exists()
    assert json.loads((folder / "progress.json").read_text())["status"] == "open"
    assert subprocess.run(["git", "-C", str(repo), "status", "--short"], capture_output=True,
                          text=True).stdout == ""


def test_non_project_task_lives_in_puck_home(puck_home, tmp_path):
    outside = tmp_path / "plain"
    outside.mkdir()
    task = tasks.start("study graphs", "learn", outside)
    assert task["folder"].startswith(str(puck_home / "tasks"))


def test_same_goal_gets_unique_ids(puck_home, repo):
    assert tasks.start("same", "build", repo)["id"] != tasks.start("same", "build", repo)["id"]


def test_worktree_task_is_isolated(puck_home, repo):
    task = tasks.start("parallel work", "build", repo, worktree=True)
    assert task["cwd"] != str(repo) and task["folder"].startswith(task["cwd"])
    listed = subprocess.run(["git", "-C", str(repo), "worktree", "list"], capture_output=True, text=True)
    assert task["id"] in listed.stdout


def test_check_marks_pass_only_on_real_exit_zero(puck_home, repo):
    task = tasks.start("x", "build", repo)
    good = tasks.add_step(task["id"], "ok", "true")
    bad = tasks.add_step(task["id"], "bad", "echo nope; exit 3")
    assert tasks.run_check(task["id"], good)[0] is True
    passed, output = tasks.run_check(task["id"], bad)
    assert passed is False and "nope" in output
    with pytest.raises(tasks.TaskError, match="not passing"):
        tasks.close(task["id"], "done")


def test_done_needs_at_least_one_check(puck_home, repo):
    task = tasks.start("x", "build", repo)
    with pytest.raises(tasks.TaskError, match="no acceptance checks"):
        tasks.close(task["id"], "done")


def test_findings_require_a_retro_before_close(puck_home, repo):
    task = tasks.start("x", "build", repo)
    tasks.add_step(task["id"], "ok", "true")
    tasks.run_check(task["id"], "s1")
    tasks.note(task, "procedure", "run migrations first")
    with pytest.raises(tasks.TaskError, match="retro.md is missing"):
        tasks.close(task["id"], "done")
    (repo / ".puck" / "tasks" / task["id"] / "retro.md").write_text("# Retro\n")
    assert tasks.close(task["id"], "done").exists()


def test_no_findings_closes_with_one_line_retro(puck_home, repo):
    task = tasks.start("x", "build", repo)
    archive = tasks.close(task["id"], "partial")
    assert "No findings" in archive.read_text()
    assert archive.parent == puck_home / "tasks" / "retros"


def test_ambiguous_task_asks_for_id(puck_home, repo):
    tasks.start("one", "build", repo)
    tasks.start("two", "build", repo)
    with pytest.raises(tasks.TaskError, match="Several open tasks"):
        tasks.resolve(None, repo)


def test_session_binds_from_start_output_and_stays_separate(puck_home, repo):
    first = tasks.start("one", "build", repo)
    second = tasks.start("two", "build", repo)
    for session, task in (("a", first), ("b", second)):
        call("anchors", "post-tool", "claude", {
            "session_id": session, "tool_name": "Bash", "tool_input": {"command": "puck task start x"},
            "tool_response": {"stdout": f"{tasks.MARKER} {task['id']}"}})
    assert store.read_json(store.state_dir() / "sessions/a.json")["task"] == first["id"]
    assert store.read_json(store.state_dir() / "sessions/b.json")["task"] == second["id"]
    assert tasks.load(first["id"])["sessions"] == ["a"]


def test_marker_in_other_output_does_not_bind(puck_home, repo):
    task = tasks.start("x", "build", repo)
    call("anchors", "post-tool", "claude", {
        "session_id": "s", "tool_name": "Read", "tool_input": {"file_path": "/a.md"},
        "tool_response": f"{tasks.MARKER} {task['id']}"})
    assert store.read_json(store.state_dir() / "sessions/s.json")["task"] is None


def bind(session, task, host="claude"):
    payload = {"session_id": session, "tool_name": "Bash", "tool_input": {"command": "puck task start x"},
               "tool_response": {"stdout": f"{tasks.MARKER} {task['id']}"}}
    call("anchors", "post-tool", host, payload)


def test_close_guard_blocks_once_only_when_checks_pass(puck_home, repo):
    task = tasks.start("x", "build", repo)
    bind("s", task)
    stop = {"session_id": "s", "stop_hook_active": False}
    assert call("close-guard", "stop", "claude", stop) is None
    tasks.add_step(task["id"], "ok", "true")
    assert call("close-guard", "stop", "claude", stop) is None
    tasks.run_check(task["id"], "s1")
    assert call("close-guard", "stop", "claude", stop)["decision"] == "block"
    assert call("close-guard", "stop", "claude", stop) is None


def test_close_guard_ignores_ordinary_chats_and_active_stop(puck_home, repo):
    assert call("close-guard", "stop", "claude", {"session_id": "chat"}) is None
    task = tasks.start("x", "build", repo)
    bind("s", task)
    tasks.add_step(task["id"], "ok", "true")
    tasks.run_check(task["id"], "s1")
    assert call("close-guard", "stop", "claude", {"session_id": "s", "stop_hook_active": True}) is None


def test_close_guard_blocks_for_copilot(puck_home, repo):
    task = tasks.start("x", "build", repo)
    call("anchors", "post-tool", "copilot-cli", {
        "sessionId": "c", "toolName": "bash", "toolArgs": "puck task start x",
        "toolResult": {"textResultForLlm": f"{tasks.MARKER} {task['id']}"}})
    tasks.add_step(task["id"], "ok", "true")
    tasks.run_check(task["id"], "s1")
    output = call("close-guard", "stop", "copilot-cli", {"sessionId": "c"})
    assert output["decision"] == "block" and "reason" in output


def test_pack_is_capped_paths_only_and_ranked(puck_home):
    add_skill(puck_home, "login-debug", template("login-debug").replace("status: draft", "status: active")
              .replace("What it does.", "Debug login failures."))
    (puck_home / "tasks" / "retros").mkdir(parents=True)
    for number in range(100):
        (puck_home / "tasks/retros" / f"login-{number}.md").write_text("# Login retro\n\nFixed a login thing\n")
    text = context.pack("fix the login bug")
    assert len(text) <= context.PACK_LIMIT
    assert "login-debug" in text and "[retro]" in text


def test_pack_excludes_drafts_and_mentions_proposals(puck_home):
    add_skill(puck_home, "login-debug", template("login-debug"))
    skills.propose("rule" if False else "instruction", "t", "global", "Be brief", "Be brief.")
    text = context.pack("login")
    assert "login-debug" not in text and "1 proposal" in text


def test_scratch_numbers_experiments_and_gc_keeps_recent(puck_home, repo):
    task = tasks.start("x", "build", repo)
    assert scratch.new_experiment(task, "Try FTS5").name == "001-try-fts5"
    assert scratch.new_experiment(task, "again").name == "002-again"
    scratch.log(task, "h", "cmd", "r", "discard")
    tasks.close(task["id"], "partial")
    assert scratch.collect_garbage(14) == []
    closed = tasks.load(task["id"])
    closed["closed"] = int(time.time()) - 15 * 86_400
    tasks.save(closed)
    assert len(scratch.collect_garbage(14)) == 1


def test_new_skill_is_a_draft_and_refuses_duplicates(puck_home):
    (puck_home / "templates").exists()
    path = skills.new("deploy-steps", "Deploy things. Use when deploying. Not for builds.", "t1")
    assert "status: draft" in (path / "SKILL.md").read_text()
    with pytest.raises(tasks.TaskError, match="skill-patch"):
        skills.new("deploy-steps", "again", "t2")


def test_parallel_proposals_stay_separate(puck_home):
    paths = {skills.propose("instruction", "t", "global", "same", f"body {n}") for n in range(5)}
    assert len(paths) == 5


def test_instruction_proposal_respects_budget(puck_home):
    good = skills.propose("instruction", "t", "global", "Short rule", "- Short rule.")
    skills.resolve(good.stem, approve=True)
    assert "Short rule" in (puck_home / "instructions/global.md").read_text()
    assert not good.exists() and (puck_home / "proposals/done" / good.name).exists()
    bad = skills.propose("instruction", "t", "global", "Huge", "x" * 7000)
    with pytest.raises(tasks.TaskError, match="Over budget"):
        skills.resolve(bad.stem, approve=True)
    assert bad.exists() and "xxxx" not in (puck_home / "instructions/global.md").read_text()


def test_reject_changes_nothing(puck_home):
    before = (puck_home / "instructions/global.md").read_text()
    proposal = skills.propose("instruction", "t", "global", "No", "- No.")
    skills.resolve(proposal.stem, approve=False)
    assert (puck_home / "instructions/global.md").read_text() == before


def test_promote_activates_commits_and_reverts_cleanly(puck_home):
    git(puck_home, "init", "-q", "-b", "main")
    git(puck_home, "config", "user.name", "t")
    git(puck_home, "config", "user.email", "t@t")
    git(puck_home, "add", "-A")
    git(puck_home, "commit", "-q", "-m", "base")
    path = skills.new("deploy-steps", "Deploy things. Use when deploying. Not for builds.", "t1")
    (path / "evals" / "triggers").mkdir(parents=True)
    (path / "evals" / "triggers" / "prompt.md").write_text("hi\n")
    skills.promote("deploy-steps", run_evals=False)
    assert (puck_home / "dist/claude/skills/deploy-steps/SKILL.md").exists()
    assert (puck_home / "dist/claude/evals/deploy-steps-triggers/prompt.md").exists()
    git(puck_home, "revert", "--no-edit", "HEAD")
    from cli import build
    build.build_all(puck_home)
    assert not (puck_home / "dist/claude/skills/deploy-steps").exists()


def test_promote_needs_evals(puck_home):
    skills.new("deploy-steps", "Deploy things. Use when deploying. Not for builds.", "t1")
    with pytest.raises(tasks.TaskError, match="no eval cases"):
        skills.promote("deploy-steps", run_evals=False)
