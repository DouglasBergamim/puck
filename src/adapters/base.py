"""The adapter contract. Its defaults are the generic harness.

Adapters are pure: no files, network, clock, environment or LLM. The same input
gives byte-identical output. core/build.py does all reading and writing.
"""

import json
import math
from pathlib import PurePosixPath

from core.common.model import CAPABILITIES, DESCRIPTION, Agent, Event, File, HookRule, Result, Skill, ToolMap, frontmatter


def text_file(path: str, text: str) -> File:
    return File(path, text.encode())


def json_file(path: str, value: dict) -> File:
    return text_file(path, json.dumps(value, indent=2) + "\n")


class Adapter:
    """Content tier: AGENTS.md plus Agent Skills, for any harness reading those."""

    name = "generic"
    title = "any harness"
    tier = "content"
    tools: dict[str, ToolMap] = {}
    models: dict[str, str] = {}
    events: dict[str, str] = {}
    variables: tuple[str, ...] = ()
    skills_root = ".agents/skills"
    instructions_path = "AGENTS.md"
    reference_note = ""

    def tool_names(self, capabilities: tuple[str, ...]) -> list[str]:
        names = [t for capability in capabilities for t in self.tools[capability].tools]
        return list(dict.fromkeys(names))

    def tools_reference(self) -> str:
        lines = [f"# Capabilities on {self.title}", ""]
        if self.reference_note:
            lines += [self.reference_note, ""]
        lines += ["| Capability | Tool |", "|---|---|"]
        for capability in CAPABILITIES:
            mapped = self.tools.get(capability)
            used = ", ".join(mapped.tools) if mapped else "your harness's equivalent"
            note = f", {mapped.note}" if mapped and mapped.note else ""
            lines.append(f"| {capability} | {used}{note} |")
        return "\n".join(lines) + "\n"

    # Build time.

    def render_skill(self, skill: Skill) -> list[File]:
        root = f"{self.skills_root}/{skill.name}"
        head = {"name": skill.name, "description": skill.description}
        if skill.invocation == "user":
            head["disable-model-invocation"] = True
        files = [text_file(f"{root}/SKILL.md", frontmatter(head, skill.body))]
        files += [File(f"{root}/{f.path}", f.content, f.executable) for f in skill.files]
        files.append(text_file(f"{root}/references/host-tools.md", self.tools_reference()))
        return files

    def render_agent(self, agent: Agent) -> list[File]:
        return []

    def render_hooks(self, rules: list[HookRule]) -> list[File]:
        return []

    def render_instructions(self, text: str) -> list[File]:
        return [text_file(self.instructions_path, text)]

    def render_manifest(self, version: str) -> list[File]:
        return []

    # Run time.

    def parse_event(self, name: str, raw: dict) -> Event:
        return Event(event=name, host=self.name, cwd=raw.get("cwd"),
                     already_forced=bool(raw.get("stop_hook_active")))

    def render_result(self, event: Event, result: Result) -> dict | None:
        output: dict = {}
        if result.decision == "block":
            output.update(decision="block", reason=result.reason or "")
        if result.context:
            output["hookSpecificOutput"] = {
                "hookEventName": self.events[event.event],
                "additionalContext": result.context,
            }
        return output or None

    # Commands.

    def launch_command(self, package: PurePosixPath) -> list[str] | None:
        return None

    def eval_command(self, package: PurePosixPath, case: str) -> list[str] | None:
        return None


class PluginAdapter(Adapter):
    """Shared shape for harnesses that load a plugin folder."""

    skills_root = "skills"
    manifest_path = "plugin.json"

    def render_instructions(self, text: str) -> list[File]:
        # Plugins can't carry instruction files; the session-start hook injects them.
        return []

    def render_manifest(self, version: str) -> list[File]:
        return [json_file(self.manifest_path,
                          {"name": "puck", "version": version, "description": DESCRIPTION})]

    def hook_command(self, rule: HookRule) -> str:
        return f"{rule.run} --event {rule.event} --host {self.name}"

    def hook_entry(self, rule: HookRule, seconds: int) -> dict:
        raise NotImplementedError

    def hook_document(self, events: dict) -> dict:
        raise NotImplementedError

    def render_hooks(self, rules: list[HookRule]) -> list[File]:
        events: dict[str, list] = {}
        for rule in rules:
            if rule.event in self.events:
                entry = self.hook_entry(rule, math.ceil(rule.timeout_ms / 1000))
                events.setdefault(self.events[rule.event], []).append(entry)
        return [json_file("hooks/hooks.json", self.hook_document(events))]
