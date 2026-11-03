import filecmp
import json
import os
import re
from pathlib import Path

import pytest

import adapters
from adapters.base import PluginAdapter
from core.common import paths
from core.common.model import Event
from core.primitives import build
from core.tools.work import tasks
from core import hooks

TESTS = Path(__file__).parent
FIXTURES = TESTS / "fixtures"
GOLDEN = TESTS / "golden"
NAMES = sorted(adapters.ADAPTERS)


def rendered(name):
    return {f.path: f for f in build.render(adapters.get(name), FIXTURES)}


@pytest.mark.parametrize("name", NAMES)
def test_output_matches_golden(name):
    """To accept a deliberate change: UPDATE_GOLDEN=1 uv run pytest tests/test_adapters.py"""
    files = rendered(name)
    root = GOLDEN / name
    if os.environ.get("UPDATE_GOLDEN"):
        build.write(list(files.values()), root)
    expected = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    assert set(files) == expected
    for path, item in files.items():
        assert item.content == (root / path).read_bytes(), path


@pytest.mark.parametrize("name", NAMES)
def test_rendering_is_deterministic(name, tmp_path):
    build.write(list(rendered(name).values()), tmp_path / "a")
    build.write(list(rendered(name).values()), tmp_path / "b")
    compared = filecmp.dircmp(tmp_path / "a", tmp_path / "b")
    assert not (compared.diff_files or compared.left_only or compared.right_only)


@pytest.mark.parametrize("name", NAMES)
def test_drafts_stay_out_and_no_absolute_paths_leak(name):
    files = rendered(name)
    assert not any("unfinished" in path for path in files)
    assert not any(str(FIXTURES).encode() in f.content for f in files.values())


def test_scripts_stay_executable():
    assert rendered("claude")["skills/sample/scripts/run.sh"].executable


def test_generic_gives_any_harness_agents_md_and_skills():
    files = rendered("generic")
    assert "AGENTS.md" in files and ".agents/skills/sample/SKILL.md" in files
    assert not any(path.startswith(("hooks", "agents")) for path in files)


def test_core_never_names_a_harness():
    names = re.compile(r"claude|copilot|cursor|codex|gemini", re.IGNORECASE)
    source = TESTS.parent / "src"
    offenders = [str(p) for folder in ("core", "cli") for p in (source / folder).rglob("*.py")
                 if names.search(p.read_text())]
    assert offenders == []


class FakeAdapter(PluginAdapter):
    """A brand-new harness, added with no change to core."""

    name = "fake"
    title = "Fake"
    tier = "partial"
    events = {"session-start": "onStart", "stop": "onStop"}

    def hook_entry(self, rule, seconds):
        return {"run": self.hook_command(rule)}

    def hook_document(self, events):
        return {"on": events}

    def parse_event(self, name, raw):
        return Event(event=name, host=self.name, cwd=raw["dir"])

    def render_result(self, event, result):
        return {"say": result.context} if result.context else None


def test_new_harness_needs_no_core_change(puck_home, monkeypatch):
    fake = FakeAdapter()
    monkeypatch.setitem(adapters.ADAPTERS, "fake", fake)
    target = build.build_adapter(fake, puck_home)
    hook_file = json.loads((target / "hooks/hooks.json").read_text())
    assert set(hook_file["on"]) == {"onStart", "onStop"}
    assert (target / "skills/task/SKILL.md").exists()
    tasks.start("a plan", "build", puck_home)
    payload = json.dumps({"dir": str(puck_home)})
    assert "a plan" in json.loads(hooks.run("resume", "session-start", "fake", payload))["say"]


def test_home_finds_the_repo_without_the_variable(monkeypatch):
    monkeypatch.delenv("PUCK_HOME", raising=False)
    assert paths.home() == TESTS.parent
    assert paths.skills().is_dir()


def test_claude_launch_grants_puck_commands_and_topic_writes():
    from pathlib import PurePosixPath
    command = adapters.get("claude").launch_command(
        PurePosixPath("/h/dist/claude"), PurePosixPath("/h"), ("puck sources",), ("/puck:teach x",))
    assert command[:2] == ["claude", "/puck:teach x"]
    assert command[command.index("--add-dir") + 1] == "/h"
    rules = command[command.index("--allowedTools") + 1].split(",")
    assert "Bash(puck sources *)" in rules and "Edit(//h/context/knowledge/**)" in rules
    assert not any("proposal" in rule for rule in rules)


def test_claude_install_links_the_plugin_and_grants_the_same_rules_as_launch():
    from pathlib import PurePosixPath
    claude = adapters.get("claude")
    plan = claude.install(PurePosixPath("/h"), ("puck sources",))
    assert plan.link == ".claude/skills/puck" and plan.settings == ".claude/settings.json"
    assert list(plan.allow) == claude.allow_rules(PurePosixPath("/h"), ("puck sources",))
    assert plan.directories == ("/h",) and plan.env == (("PUCK_HOME", "/h"),)
    assert adapters.get("generic").install(PurePosixPath("/h")) is None
