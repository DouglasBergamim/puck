import json
import shutil
from pathlib import Path

from cli import build, lint

REPO = Path(__file__).resolve().parent.parent
AGENT = (REPO / "templates" / "agent.md").read_text()


def add_skill(home, name, text):
    directory = home / "skills" / name
    directory.mkdir()
    (directory / "SKILL.md").write_text(text)


def template(name="draft-one"):
    return (REPO / "templates" / "skill.md").read_text().replace("skill-name", name)


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
    (puck_home / "profile.md").write_text("x" * 7000)
    assert any("always-on" in e for e in lint.lint_all(puck_home))


def test_lint_checks_agents(puck_home):
    (puck_home / "agents" / "agent-name.md").write_text(AGENT.replace("[read, search]", "[teleport]"))
    assert any("known capabilities" in e for e in lint.lint_all(puck_home))


def test_drafts_and_retired_skills_stay_out_of_builds(puck_home):
    add_skill(puck_home, "draft-one", template())
    build.build_all(puck_home)
    assert (puck_home / "dist/claude/skills/status/SKILL.md").exists()
    assert not (puck_home / "dist/claude/skills/draft-one").exists()


def test_claude_package_shape(puck_home):
    (puck_home / "agents" / "agent-name.md").write_text(AGENT)
    build.build_all(puck_home)
    target = puck_home / "dist/claude"
    assert json.loads((target / ".claude-plugin/plugin.json").read_text())["name"] == "puck"
    hooks = json.loads((target / "hooks/hooks.json").read_text())["hooks"]
    assert set(hooks) == {"SessionStart", "UserPromptSubmit", "PostToolUse", "PreCompact", "Stop"}
    command = hooks["SessionStart"][0]["hooks"][0]["command"]
    assert command == "puck hook resume --event session-start --host claude"
    skill = (target / "skills/status/SKILL.md").read_text()
    assert "metadata" not in skill
    assert (target / "skills/status/references/host-tools.md").exists()
    agent = (target / "agents/agent-name.md").read_text()
    assert "tools: Read, Bash" in agent and "model: opus" in agent and "maxTurns: 20" in agent


def test_copilot_package_shape(puck_home):
    (puck_home / "agents" / "agent-name.md").write_text(AGENT)
    build.build_all(puck_home)
    target = puck_home / "dist/copilot-cli"
    assert json.loads((target / "plugin.json").read_text())["name"] == "puck"
    hooks = json.loads((target / "hooks/hooks.json").read_text())
    assert hooks["version"] == 1
    assert set(hooks["hooks"]) == {"sessionStart", "userPromptSubmitted", "postToolUse", "preCompact", "agentStop"}
    assert hooks["hooks"]["postToolUse"][0]["bash"].endswith("--host copilot-cli")
    assert (target / "agents/agent-name.agent.md").exists()


def test_user_invocation_maps_to_host_field(puck_home):
    add_skill(puck_home, "manual", template("manual").replace("status: draft", "status: active")
              .replace("invocation: model", "invocation: user"))
    build.build_all(puck_home)
    text = (puck_home / "dist/claude/skills/manual/SKILL.md").read_text()
    assert "disable-model-invocation: true" in text


def test_rebuild_removes_what_left_the_source(puck_home):
    build.build_all(puck_home)
    shutil.rmtree(puck_home / "skills/status")
    (puck_home / "skills/other").mkdir()
    (puck_home / "skills/other/SKILL.md").write_text(template("other"))
    build.build_all(puck_home)
    assert not (puck_home / "dist/claude/skills/status").exists()
