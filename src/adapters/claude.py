"""Claude Code: a plugin with nested hook entries and Markdown agents."""

from pathlib import PurePosixPath

from adapters.base import PluginAdapter, text_file
from core.common.model import Agent, File, HookRule, Install, Skill, ToolMap, frontmatter


class ClaudeAdapter(PluginAdapter):
    name = "claude"
    title = "Claude Code"
    tier = "full"
    manifest_path = ".claude-plugin/plugin.json"
    variables = ("CLAUDE",)
    # Grep and Glob are absent by default on macOS, so search goes through the shell.
    tools = {
        "read": ToolMap(("Read",)),
        "search": ToolMap(("Bash",), "using `rg`"),
        "shell-read": ToolMap(("Bash",)),
        "shell": ToolMap(("Bash",)),
        "edit": ToolMap(("Edit", "Write")),
        "web": ToolMap(("WebSearch", "WebFetch")),
        "subagents": ToolMap(("Agent",)),
        "ask": ToolMap(("AskUserQuestion",), "1-4 questions, each with 2-4 options; the user can always type their own answer"),
    }
    models = {"fast": "haiku", "strong": "opus"}
    events = {"session-start": "SessionStart", "stop": "Stop"}

    def qualified(self, name: str) -> str:
        return f"puck:{name}"  # plugin skills and agents are namespaced by the plugin name

    def render_skill(self, skill: Skill) -> list[File]:
        # plugin eval reads evals/ at the plugin root; case names carry the skill.
        evals = [File(f"evals/{skill.name}-{f.path}", f.content, f.executable) for f in skill.evals]
        return super().render_skill(skill) + evals

    def render_agent(self, agent: Agent) -> list[File]:
        head = {
            "name": agent.name,
            "description": agent.description,
            "tools": ", ".join(self.tool_names(agent.tools)),
            "model": self.models[agent.model],
        }
        if agent.max_turns:
            head["maxTurns"] = agent.max_turns
        body = agent.body.rstrip("\n") + "\n\n" + self.agent_reference(agent)
        return [text_file(f"agents/{agent.name}.md", frontmatter(head, body))]

    def hook_entry(self, rule: HookRule, seconds: int) -> dict:
        command = {"type": "command", "command": self.hook_command(rule), "timeout": seconds}
        return {"hooks": [command]}

    def hook_document(self, events: dict) -> dict:
        return {"description": "Puck session hooks", "hooks": events}

    def allow_rules(self, home: PurePosixPath | None, commands: tuple[str, ...]) -> list[str]:
        allowed = [rule for prefix in commands for rule in (f"Bash({prefix})", f"Bash({prefix} *)")]
        if home:
            # A leading // marks an absolute path. Edit rules cover every file-editing tool.
            allowed.append(f"Edit(/{home}/context/knowledge/**)")
        return allowed

    def launch_command(self, package: PurePosixPath, home: PurePosixPath | None = None,
                       commands: tuple[str, ...] = (), extra: tuple[str, ...] = ()) -> list[str]:
        # Extra arguments go first: --allowedTools takes a list and would swallow them.
        command = ["claude", *extra, "--plugin-dir", str(package)]
        if home:
            command += ["--add-dir", str(home)]
        allowed = self.allow_rules(home, commands)
        if allowed:
            command += ["--allowedTools", ",".join(allowed)]
        return command

    def install(self, home: PurePosixPath, commands: tuple[str, ...] = ()) -> Install:
        # A plugin folder under ~/.claude/skills/ loads in every session.
        return Install(link=".claude/skills/puck", settings=".claude/settings.json",
                       allow=tuple(self.allow_rules(home, commands)), directories=(str(home),),
                       env=(("PUCK_HOME", str(home)),))

    def eval_command(self, package: PurePosixPath, case: str) -> list[str]:
        return ["claude", "plugin", "eval", str(package), "--runs", "1", "--case", case]
