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


def write_case(folder, skill="x", fired=1):
    """One eval case in the shape the runner reads: a prompt and a tool_used grader."""
    (folder / "graders").mkdir(parents=True, exist_ok=True)
    (folder / "prompt.md").write_text("---\nmax_turns: 5\nallowed_tools: [Skill]\n---\n\nDo the thing.\n")
    (folder / "graders" / "skill-fired.md").write_text(
        f"---\ntype: tool_used\ntool: Skill\ninput_match: '{skill}'\nmin: {fired}\nmax: {fired or 0}\n---\n")


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
    (paths.agents(puck_home) / "agent-name.md").write_text(AGENT.replace("tools: [read]", "tools: [teleport]"))
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
    assert "tools: Read\n" in agent and "model: opus" in agent and "maxTurns: 20" in agent


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
workflow:
  - stage: work
    delivers: the thing
---
## Role
R.

## Context
C.

## Rules
R.

## Workflow
1. **Work.** W.

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
    assert "inactive skills ['nope']" in joined and "must name worker agents" in joined
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
    worker.write_text(AGENT.replace("tools: [read]", "tools: [read, ask]"))
    assert any("can't have the ask capability" in e for e in lint.lint_agent(worker, set(CAPABILITIES)))


def lead_text(workflow, skills="[task]", body_stages="**Work.**"):
    return LEAD.format(name="guide", tools="[read]", skills=skills, agents="[]").replace(
        "workflow:\n  - stage: work\n    delivers: the thing\n", workflow).replace("**Work.**", body_stages)


def test_lead_workflow_is_checked(puck_home):
    from core.common.model import CAPABILITIES
    lead = paths.agents(puck_home) / "guide.md"
    check = lambda: "\n".join(lint.lint_agent(lead, set(CAPABILITIES), {"task"}, set()))
    lead.write_text(lead_text("workflow:\n  - stage: work\n    skill: task\n    delivers: x\n    check: \"true\"\n"))
    assert check() == ""
    lead.write_text(lead_text(""))
    assert "a lead needs a workflow" in check()
    lead.write_text(lead_text("workflow:\n  - stage: work\n    skill: nope\n    delivers: ''\n"))
    assert "skill 'nope' isn't in skills" in check() and "needs delivers" in check()
    lead.write_text(lead_text("workflow:\n  - stage: work\n    delivers: x\n", body_stages="**Other.** Rework it."))
    assert "needs a bold entry" in check()
    lead.write_text(lead_text("workflow:\n  - stage: work\n    skill: [task]\n    delivers: {a: 1}\n    check: [a, b]\n"))
    joined = check()
    assert "skill must be text" in joined and "check must be text" in joined and "needs delivers" in joined
    lead.write_text(lead_text("workflow:\n  - stage: work\n    delivers: x\n").replace("## Context\nC.\n\n", ""))
    assert "missing section 'Context'" in check()


def test_worker_status_and_no_workflow(puck_home):
    from core.common.model import CAPABILITIES
    worker = paths.agents(puck_home) / "agent-name.md"
    worker.write_text(AGENT)
    assert lint.lint_agent(worker, set(CAPABILITIES)) == []
    worker.write_text(AGENT.replace("- status: complete | partial | blocked\n", ""))
    assert any("Return must include 'status:" in e for e in lint.lint_agent(worker, set(CAPABILITIES)))
    worker.write_text(AGENT.replace("model: strong", "model: strong\nworkflow: [{stage: a, delivers: b}]"))
    assert any("only a lead has a workflow" in e for e in lint.lint_agent(worker, set(CAPABILITIES)))


def test_active_skill_needs_trigger_and_near_miss_evals(puck_home):
    add_skill(puck_home, "live-one", template("live-one").replace("status: draft", "status: active"))
    assert any("needs evals/triggers" in e for e in lint.lint_all(puck_home))
    for case in ("triggers", "ignores-other"):
        (paths.skills(puck_home) / "live-one" / "evals" / case).mkdir(parents=True)
    assert any("evals/triggers needs prompt.md" in e for e in lint.lint_all(puck_home))
    for case, fired in (("triggers", 1), ("ignores-other", 0)):
        write_case(paths.skills(puck_home) / "live-one" / "evals" / case, "live-one", fired)
    assert not any("live-one" in e for e in lint.lint_all(puck_home))


def test_agents_may_name_only_active_skills(puck_home):
    from core.common.model import CAPABILITIES
    add_skill(puck_home, "draft-one", template())
    lead = paths.agents(puck_home) / "guide.md"
    lead.write_text(lead_text("workflow:\n  - stage: work\n    skill: draft-one\n    delivers: x\n", skills="[draft-one]"))
    assert any("inactive skills ['draft-one']" in e for e in lint.lint_all(puck_home))
    clash = paths.agents(puck_home) / "draft-one.md"
    clash.write_text(lead_text("workflow:\n  - stage: work\n    delivers: x\n").replace("name: guide", "name: draft-one"))
    assert any("can't match the skill" in e for e in lint.lint_agent(clash, set(CAPABILITIES)))


def test_workflow_renders_as_a_deliverables_table(puck_home):
    import adapters
    (paths.agents(puck_home) / "guide.md").write_text(lead_text(
        "workflow:\n  - stage: work\n    skill: task\n    delivers: the thing\n    check: make test\n"))
    files = {f.path: f for f in build.render(adapters.get("claude"), puck_home)}
    text = files["skills/guide/SKILL.md"].content.decode()
    assert "## Workflow and deliverables" in text
    assert "| work | puck:task | the thing | `make test` passes |" in text


def test_agent_new_scaffolds_and_refuses_clashes(puck_home):
    import pytest
    from core.common.errors import PuckError
    from core.primitives import agents
    agents.new("helper-one", "worker", "Helps. Use when testing.")
    agents.new("guide-one", "lead", "Guides. Use when testing.")
    assert lint.lint_all(puck_home) == []
    with pytest.raises(PuckError, match="exists"):
        agents.new("helper-one", "worker", "again")
    with pytest.raises(PuckError, match="becomes a skill"):
        agents.new("task", "lead", "clash")
    with pytest.raises(PuckError, match="--mode"):
        agents.new("x", "boss", "bad mode")


def test_lint_root_checks_the_given_copy(puck_home, tmp_path, capsys):
    import argparse
    from cli.commands.primitives import run_lint
    snapshot = tmp_path / "snapshot"
    shutil.copytree(puck_home / "context", snapshot / "context")
    assert run_lint(argparse.Namespace(root=str(snapshot))) == 0
    add_skill(snapshot, "bad", template("bad").replace("## Done when", "## Finished"))
    assert run_lint(argparse.Namespace(root=str(snapshot))) == 1
    assert "skills/bad: needs a 'Done when' section" in capsys.readouterr().err
    assert run_lint(argparse.Namespace(root=None)) == 0  # the real home is untouched


def test_eval_format_catches_malformed_cases(puck_home):
    add_skill(puck_home, "evalled", template("evalled"))
    case = paths.skills(puck_home) / "evalled" / "evals" / "triggers"
    write_case(case, "evalled")
    assert not any("evalled" in e for e in lint.lint_all(puck_home))
    (case / "prompt.md").write_text("---\nmax_turns: zero\nallowed_tools: Skill\n---\n")
    (case / "graders" / "skill-fired.md").write_text("---\ntype: tool_used\ntool: Skill\ninput_match: '('\nmin: 2\nmax: 1\n---\n")
    (case / "graders" / "judge.md").write_text("---\ntype: vibes\n---\n")
    (case / "graders" / "empty.md").write_text("---\ntype: llm\n---\n")
    joined = "\n".join(e for e in lint.lint_all(puck_home) if "evalled" in e)
    for expected in ("max_turns must be a positive", "allowed_tools must be a list", "needs the prompt text",
                     "isn't a valid pattern", "0 <= min <= max", "type must be one of", "needs its PASS and FAIL"):
        assert expected in joined, expected


def test_features_rows_match_what_exists(puck_home):
    rows = lambda *names: "\n".join(f"| `{n}` | x |" for n in names) + "\n| `puck lint` | not a row |\n"
    skills, agents, hooks = {"task", "plan"}, {"reviewer"}, {"resume"}
    assert lint.features_problems(rows("task", "plan", "reviewer", "resume"), skills, agents, hooks) == []
    problems = lint.features_problems(rows("task", "reviewer", "resume", "reading-path"), skills, agents, hooks)
    assert "docs/features.md: no row for skill 'plan'" in problems
    assert "docs/features.md: row for 'reading-path', which isn't an active skill, agent or hook" in problems
    assert lint.lint_features(puck_home, skills, agents, hooks) == []  # no docs/ in a bare home


def test_doc_references_catch_stale_names(puck_home):
    docs = puck_home / "docs"
    docs.mkdir()
    (docs / "design.md").write_text(
        "| Research | The `researcher` lead: `scope` → `field-map` → `reading-path`, as a task of type `research` |\n"
        "Call `/puck:tutor` or `/puck:task`.\n")
    (docs / "research").mkdir()
    (docs / "research" / "notes.md").write_text("`a` → `b` and /puck:elsewhere\n")
    problems = lint.lint_references(puck_home, {"scope", "field-map", "task", "researcher"})
    assert problems == ["docs/design.md:1: `reading-path` isn't a skill or agent",
                        "docs/design.md:2: `tutor` isn't a skill or agent"]


def test_install_sets_hooks_path_and_uninstall_removes_only_its_own(puck_home, tmp_path, monkeypatch):
    import subprocess
    import adapters
    from core.primitives import install
    monkeypatch.setattr(install.shutil, "which", lambda name: f"/bin/{name}")
    git = lambda *a: subprocess.run(["git", "-C", str(puck_home), *a], capture_output=True, text=True).stdout.strip()
    claude, user = adapters.get("claude"), tmp_path / "user"
    assert install.git_hooks(puck_home) is None  # not a repo yet
    git("init", "-q")
    (puck_home / ".githooks").mkdir()
    done = install.install(claude, puck_home, user)
    assert git("config", "--get", "core.hooksPath") == ".githooks" and "Turned on git hooks" in done[-1]
    assert "already on" in install.install(claude, puck_home, user)[-1]
    assert "Turned off" in install.uninstall(claude, puck_home, user)[-1]
    assert git("config", "--get", "core.hooksPath") == ""
    git("config", "core.hooksPath", "my-hooks")
    assert "Left core.hooksPath as my-hooks" in install.install(claude, puck_home, user)[-1]
    install.uninstall(claude, puck_home, user)
    assert git("config", "--get", "core.hooksPath") == "my-hooks"  # never removes what it didn't set


def test_install_leaves_a_global_hooks_path_alone(puck_home, tmp_path, monkeypatch):
    import subprocess
    import adapters
    from core.primitives import install
    monkeypatch.setattr(install.shutil, "which", lambda name: f"/bin/{name}")
    config = tmp_path / "gitconfig"
    config.write_text("[core]\n\thooksPath = /secret-scanner\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    subprocess.run(["git", "-C", str(puck_home), "init", "-q"], check=True)
    (puck_home / ".githooks").mkdir()
    done = install.install(adapters.get("claude"), puck_home, tmp_path / "user")
    assert "Left core.hooksPath as /secret-scanner" in done[-1]
    local = subprocess.run(["git", "-C", str(puck_home), "config", "--local", "--get", "core.hooksPath"],
                           capture_output=True, text=True).stdout
    assert local == ""


def test_eval_format_needs_input_match(puck_home):
    add_skill(puck_home, "evalled", template("evalled"))
    case = paths.skills(puck_home) / "evalled" / "evals" / "triggers"
    write_case(case, "evalled")
    (case / "graders" / "skill-fired.md").write_text("---\ntype: tool_used\ntool: Skill\nmin: 1\nmax: 1\n---\n")
    assert any("needs input_match" in e for e in lint.lint_all(puck_home))
