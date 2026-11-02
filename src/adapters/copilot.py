"""GitHub Copilot: one class, with the CLI and VS Code as variants.

The CLI uses camelCase events and flat output. VS Code uses PascalCase events and
nested output. Both payloads carry the `cwd` and `stop_hook_active` fields Puck reads.
"""

from pathlib import PurePosixPath

from adapters.base import PluginAdapter, text_file
from core.common.model import Agent, Event, File, HookRule, Result, ToolMap, frontmatter

CLI_EVENTS = {"session-start": "sessionStart", "stop": "agentStop"}
VSCODE_EVENTS = {"session-start": "SessionStart", "stop": "Stop"}


class CopilotAdapter(PluginAdapter):
    tier = "partial"
    variables = ("COPILOT",)
    reference_note = "Not yet tested on a real session."
    # Tool names are from the hooks docs; confirm in the portability test.
    tools = {
        "read": ToolMap(("view",)),
        "search": ToolMap(("bash",), "using `rg`"),
        "shell-read": ToolMap(("bash",)),
        "shell": ToolMap(("bash",)),
        "edit": ToolMap(("edit", "create")),
        "web": ToolMap(("web_fetch",)),
        "subagents": ToolMap(("task",)),
    }

    def __init__(self, variant: str):
        self.variant = variant
        self.name = f"copilot-{variant}"
        self.title = "Copilot CLI" if variant == "cli" else "Copilot in VS Code"
        self.events = CLI_EVENTS if variant == "cli" else VSCODE_EVENTS

    def render_agent(self, agent: Agent) -> list[File]:
        head = {
            "name": agent.name,
            "description": agent.description,
            "tools": self.tool_names(agent.tools),
        }
        return [text_file(f"agents/{agent.name}.agent.md", frontmatter(head, agent.body))]

    def hook_entry(self, rule: HookRule, seconds: int) -> dict:
        return {"type": "command", "bash": self.hook_command(rule), "timeoutSec": seconds}

    def hook_document(self, events: dict) -> dict:
        return {"version": 1, "hooks": events}

    def render_result(self, event: Event, result: Result) -> dict | None:
        output = super().render_result(event, result)
        if self.variant == "cli" and output and "hookSpecificOutput" in output:
            nested = output.pop("hookSpecificOutput")
            output["additionalContext"] = nested["additionalContext"]
        return output

    def launch_command(self, package: PurePosixPath) -> list[str]:
        return ["copilot", "plugin", "install", str(package)]
