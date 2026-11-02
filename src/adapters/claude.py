"""Claude Code: a plugin with nested hook entries and Markdown agents."""

from pathlib import PurePosixPath

from adapters.base import PluginAdapter, text_file
from core.model import Agent, File, HookRule, Skill, ToolMap, frontmatter


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
    }
    models = {"fast": "haiku", "strong": "opus"}
    events = {"session-start": "SessionStart", "stop": "Stop"}

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
        return [text_file(f"agents/{agent.name}.md", frontmatter(head, agent.body))]

    def hook_entry(self, rule: HookRule, seconds: int) -> dict:
        command = {"type": "command", "command": self.hook_command(rule), "timeout": seconds}
        return {"hooks": [command]}

    def hook_document(self, events: dict) -> dict:
        return {"description": "Puck session hooks", "hooks": events}

    def launch_command(self, package: PurePosixPath) -> list[str]:
        return ["claude", "--plugin-dir", str(package)]

    def eval_command(self, package: PurePosixPath, case: str) -> list[str]:
        return ["claude", "plugin", "eval", str(package), "--runs", "1", "--case", case]
