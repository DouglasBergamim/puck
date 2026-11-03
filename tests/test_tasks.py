import json
import subprocess
import time
from pathlib import Path

import pytest

from core.common import paths, store
from core.common.errors import PuckError
from core.primitives import skills
from core.tools.work import pack, scratch, tasks
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


def test_non_project_task_lives_in_state(puck_home, tmp_path):
    outside = tmp_path / "plain"
    outside.mkdir()
    task = tasks.start("study graphs", "learn", outside)
    assert task["folder"].startswith(str(store.state_dir() / "tasks"))


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
    assert archive.parent == paths.retros()


def test_ambiguous_task_asks_for_id(puck_home, repo):
    tasks.start("one", "build", repo)
    tasks.start("two", "build", repo)
    with pytest.raises(tasks.TaskError, match="Several open tasks"):
        tasks.resolve(None, repo)


def test_worktree_plan_beats_its_repo(puck_home, repo):
    main = tasks.start("main work", "build", repo)
    side = tasks.start("side work", "build", repo, worktree=True)
    assert [t["id"] for t in tasks.open_for(repo)] == [main["id"]]
    assert [t["id"] for t in tasks.open_for(Path(side["cwd"]))] == [side["id"]]


def test_checklist_shows_done_and_not_done(puck_home, repo):
    task = tasks.start("x", "build", repo)
    tasks.add_step(task["id"], "first", "true")
    tasks.add_step(task["id"], "second", "false")
    tasks.run_check(task["id"], "s1")
    text = tasks.checklist(tasks.load(task["id"]))
    assert "1/2 done" in text and "[x] s1 first" in text and "[ ] s2 second" in text


def test_close_guard_blocks_once_only_when_checks_pass(puck_home, repo):
    task = tasks.start("x", "build", repo)
    stop = {"cwd": str(repo), "stop_hook_active": False}
    assert call("close-guard", "stop", "claude", stop) is None
    tasks.add_step(task["id"], "ok", "true")
    assert call("close-guard", "stop", "claude", stop) is None
    tasks.run_check(task["id"], "s1")
    assert call("close-guard", "stop", "claude", stop)["decision"] == "block"
    assert call("close-guard", "stop", "claude", stop) is None


def test_close_guard_ignores_ordinary_chats_and_active_stop(puck_home, repo):
    assert call("close-guard", "stop", "claude", {"cwd": str(repo)}) is None
    task = tasks.start("x", "build", repo)
    tasks.add_step(task["id"], "ok", "true")
    tasks.run_check(task["id"], "s1")
    assert call("close-guard", "stop", "claude", {"cwd": str(repo), "stop_hook_active": True}) is None


def test_close_guard_blocks_for_copilot(puck_home, repo):
    task = tasks.start("x", "build", repo)
    tasks.add_step(task["id"], "ok", "true")
    tasks.run_check(task["id"], "s1")
    output = call("close-guard", "stop", "copilot-cli", {"cwd": str(repo)})
    assert output["decision"] == "block" and "reason" in output


def test_pack_is_capped_paths_only_and_ranked(puck_home):
    add_skill(puck_home, "login-debug", template("login-debug").replace("status: draft", "status: active")
              .replace("What it does.", "Debug login failures."))
    paths.retros().mkdir(parents=True)
    for number in range(100):
        (paths.retros() / f"login-{number}.md").write_text("# Login retro\n\nFixed a login thing\n")
    text = pack.pack("fix the login bug")
    assert len(text) <= pack.PACK_LIMIT
    assert "login-debug" in text and "[retro]" in text


def test_pack_excludes_drafts(puck_home):
    add_skill(puck_home, "login-debug", template("login-debug"))
    assert "login-debug" not in pack.pack("login")


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
    path = skills.new("deploy-steps", "Deploy things. Use when deploying. Not for builds.", "t1")
    assert "status: draft" in (path / "SKILL.md").read_text()
    with pytest.raises(PuckError, match="Draft a change"):
        skills.new("deploy-steps", "again", "t2")
