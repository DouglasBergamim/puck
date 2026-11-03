import json
import shutil
from pathlib import Path

from core.common import paths
from core.primitives import build, lint

REPO = Path(__file__).resolve().parent.parent
AGENT = (paths.templates(REPO) / "agent.md").read_text()


def add_skill(home, name, text):
    directory = paths.skills(home) / name
    directory.mkdir()
    (directory / "SKILL.md").write_text(text)


def template(name="draft-one"):
    return (paths.templates(REPO) / "skill.md").read_text().replace("skill-name", name)


def test_real_repo_is_clean():
    assert lint.lint_all(REPO) == []


def test_template_skill_passes(puck_home):
    add_skill(puck_home, "draft-one", template())
    assert lint.lint_all(puck_home) == []


def test_lint_rejects_host_specifics(puck_home):
    add_skill(puck_home, "bad", template("bad") + "\nUse the Bash tool with ${CLAUDE_SKILL_DIR}.\n")
    errors = "\n".join(lint.lint_all(puck_home))
    assert "host-specific variable" in errors and "'Bash'" in errors


def test_lint_rejects_nonstandard_frontmatter(puck_home):
    add_skill(puck_home, "bad", template("bad").replace("metadata:", "model: opus\nmetadata:"))
    assert any("non-standard field 'model'" in e for e in lint.lint_all(puck_home))


def test_lint_requires_procedure_first(puck_home):
    add_skill(puck_home, "bad", template("bad").replace("## Procedure", "## Intro\n\n## Procedure"))
    assert any("Procedure must be the first" in e for e in lint.lint_all(puck_home))


def test_lint_enforces_always_on_budget(puck_home):
    paths.profile(puck_home).write_text("x" * 7000)
    assert any("always-on" in e for e in lint.lint_all(puck_home))


def test_lint_checks_agents(puck_home):
    (paths.agents(puck_home) / "agent-name.md").write_text(AGENT.replace("[read, search]", "[teleport]"))
    assert any("known capabilities" in e for e in lint.lint_all(puck_home))


def test_drafts_and_retired_skills_stay_out_of_builds(puck_home):
    add_skill(puck_home, "draft-one", template())
    build.build_all(puck_home)
    assert (puck_home / "dist/claude/skills/task/SKILL.md").exists()
    assert not (puck_home / "dist/claude/skills/draft-one").exists()


def test_claude_package_shape(puck_home):
    (paths.agents(puck_home) / "agent-name.md").write_text(AGENT)
    build.build_all(puck_home)
    target = puck_home / "dist/claude"
    assert json.loads((target / ".claude-plugin/plugin.json").read_text())["name"] == "puck"
    hooks = json.loads((target / "hooks/hooks.json").read_text())["hooks"]
    assert set(hooks) == {"SessionStart", "Stop"}
    command = hooks["SessionStart"][0]["hooks"][0]["command"]
    assert command == "puck hook resume --event session-start --host claude"
    skill = (target / "skills/task/SKILL.md").read_text()
    assert "metadata" not in skill
    assert (target / "skills/task/references/host-tools.md").exists()
    assert not (target / "instructions.md").exists()
    agent = (target / "agents/agent-name.md").read_text()
    assert "tools: Read, Bash" in agent and "model: opus" in agent and "maxTurns: 20" in agent


def test_copilot_package_shape(puck_home):
    (paths.agents(puck_home) / "agent-name.md").write_text(AGENT)
    build.build_all(puck_home)
    target = puck_home / "dist/copilot-cli"
    assert json.loads((target / "plugin.json").read_text())["name"] == "puck"
    hooks = json.loads((target / "hooks/hooks.json").read_text())
    assert hooks["version"] == 1
    assert set(hooks["hooks"]) == {"sessionStart", "agentStop"}
    assert hooks["hooks"]["agentStop"][0]["bash"].endswith("--host copilot-cli")
    assert (target / "agents/agent-name.agent.md").exists()


def test_user_invocation_maps_to_host_field(puck_home):
    add_skill(puck_home, "manual", template("manual").replace("status: draft", "status: active")
              .replace("invocation: model", "invocation: user"))
    build.build_all(puck_home)
    text = (puck_home / "dist/claude/skills/manual/SKILL.md").read_text()
    assert "disable-model-invocation: true" in text


def test_rebuild_removes_what_left_the_source(puck_home):
    build.build_all(puck_home)
    shutil.rmtree(paths.skills(puck_home) / "task")
    (paths.skills(puck_home) / "other").mkdir()
    (paths.skills(puck_home) / "other/SKILL.md").write_text(template("other"))
    build.build_all(puck_home)
    assert not (puck_home / "dist/claude/skills/task").exists()


def test_install_then_uninstall_leaves_user_settings_as_they_were(puck_home, tmp_path, monkeypatch):
    import adapters
    from core.primitives import install

    monkeypatch.setattr(install.shutil, "which", lambda name: f"/bin/{name}")  # puck already on PATH

    user = tmp_path / "user"
    settings = user / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True)
    before = {"model": "opus", "permissions": {"allow": ["Read(//dev/**)"]}}
    settings.write_text(json.dumps(before))
    claude = adapters.get("claude")

    install.install(claude, puck_home, user, ("puck topic",))
    install.install(claude, puck_home, user, ("puck topic",))  # twice adds nothing new
    link = user / ".claude" / "skills" / "puck"
    assert link.resolve() == (paths.dist(puck_home) / "claude").resolve()
    after = json.loads(settings.read_text())
    assert after["permissions"]["allow"] == ["Read(//dev/**)", "Bash(puck topic)", "Bash(puck topic *)",
                                             f"Edit(/{puck_home}/context/knowledge/**)"]
    assert after["env"] == {"PUCK_HOME": str(puck_home)}

    install.uninstall(claude, puck_home, user, ("puck topic",))
    assert not link.exists() and json.loads(settings.read_text()) == before


def test_install_refuses_to_replace_a_real_folder_or_broken_settings(puck_home, tmp_path):
    import adapters
    import pytest
    from core.common.errors import PuckError
    from core.primitives import install

    user = tmp_path / "user"
    (user / ".claude" / "skills" / "puck").mkdir(parents=True)
    with pytest.raises(PuckError, match="isn't a link Puck made"):
        install.install(adapters.get("claude"), puck_home, user)
    (user / ".claude" / "skills" / "puck").rmdir()
    (user / ".claude" / "settings.json").write_text("{not json")
    with pytest.raises(PuckError, match="left alone"):
        install.install(adapters.get("claude"), puck_home, user)
    assert not (user / ".claude" / "skills" / "puck").exists()


def test_install_puts_puck_on_the_path_only_when_missing(tmp_path, monkeypatch):
    from core.primitives import install

    calls = []
    monkeypatch.setattr(install.subprocess, "run",
                        lambda command, **kw: calls.append(command) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(install.shutil, "which", lambda name: f"/bin/{name}")
    assert install.ensure_command(tmp_path) is None and calls == []
    monkeypatch.setattr(install.shutil, "which", lambda name: None if name == "puck" else f"/bin/{name}")
    assert install.ensure_command(tmp_path)
    assert calls == [["uv", "tool", "install", "--editable", str(tmp_path)]]


LEAD = """---
name: {name}
description: A lead. Use when the user asks for it.
mode: lead
tools: {tools}
model: strong
skills: {skills}
agents: {agents}
---
## Role
R.

## Rules
R.

## Workflow
1. W.

## Boundaries
B.
"""


def test_leads_must_reference_real_skills_and_workers(puck_home):
    from core.common.model import CAPABILITIES
    agents = paths.agents(puck_home)
    (agents / "worker.md").write_text(AGENT.replace("agent-name", "worker"))
    lead = agents / "guide.md"
    lead.write_text(LEAD.format(name="guide", tools="[read, subagents]", skills="[task]", agents="[worker]"))
    assert lint.lint_agent(lead, set(CAPABILITIES), {"task"}, {"worker"}) == []
    lead.write_text(LEAD.format(name="guide", tools="[read]", skills="[nope]", agents="[guide]"))
    joined = "\n".join(lint.lint_agent(lead, set(CAPABILITIES), {"task"}, {"worker"}))
    assert "unknown skills ['nope']" in joined and "must name worker agents" in joined
    assert "needs the subagents capability" in joined
    clash = agents / "task.md"
    clash.write_text(LEAD.format(name="task", tools="[read]", skills="[]", agents="[]"))
    assert any("can't match the skill" in e for e in lint.lint_agent(clash, set(CAPABILITIES), {"task"}, set()))


def test_a_lead_becomes_a_role_skill_not_a_background_agent(puck_home):
    import adapters
    (paths.agents(puck_home) / "guide.md").write_text(
        LEAD.format(name="guide", tools="[read]", skills="[task]", agents="[]"))
    files = {f.path: f for f in build.render(adapters.get("claude"), puck_home)}
    assert "agents/guide.md" not in files
    text = files["skills/guide/SKILL.md"].content.decode()
    assert "Take the role of the Puck guide" in text and "puck:task" in text


def test_only_leads_may_ask_the_user(puck_home):
    from core.common.model import CAPABILITIES
    worker = paths.agents(puck_home) / "agent-name.md"
    worker.write_text(AGENT.replace("[read, search]", "[read, ask]"))
    assert any("can't have the ask capability" in e for e in lint.lint_agent(worker, set(CAPABILITIES)))
