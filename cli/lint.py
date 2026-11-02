"""`puck lint`: enforce the primitive specifications."""

import re
from pathlib import Path

import yaml

from cli import hosts, store

STANDARD_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
STATUSES = {"draft", "active", "retired"}
INVOCATIONS = {"model", "user"}
EVENTS = {"session-start", "prompt", "post-tool", "pre-compact", "stop"}
MODES = {"observe", "inject", "block"}
SKILL_LINES = 500
INSTRUCTION_LINES = 100
ALWAYS_ON_CHARS = 6_000
DESCRIPTION_CHARS = 1_024
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HOST_VARIABLE = re.compile(r"\$\{?(CLAUDE|CURSOR|COPILOT)_")


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    _, head, body = text.split("---\n", 2)
    return yaml.safe_load(head) or {}, body


def headings(body: str) -> list[str]:
    return re.findall(r"^## (.+)$", body, re.MULTILINE)


def tool_names(configs: dict) -> set[str]:
    return {
        tool
        for config in configs.values()
        for tools in config["capabilities"].values()
        for tool in tools
    }


def lint_skill(directory: Path, tools: set[str]) -> list[str]:
    where = f"skills/{directory.name}"
    try:
        meta, body = split_frontmatter((directory / "SKILL.md").read_text())
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"{where}: {error}"]
    errors = []
    name = meta.get("name", "")
    description = meta.get("description", "")
    if name != directory.name or not NAME.match(str(name)) or len(str(name)) > 64:
        errors.append(f"{where}: name must match its directory and be lowercase")
    if not description or len(description) > DESCRIPTION_CHARS:
        errors.append(f"{where}: description must be 1-{DESCRIPTION_CHARS} characters")
    for field in sorted(set(meta) - STANDARD_FIELDS):
        errors.append(f"{where}: non-standard field '{field}' belongs in metadata")
    metadata = meta.get("metadata") or {}
    for key, value in metadata.items():
        if not isinstance(value, str):
            errors.append(f"{where}: metadata.{key} must be a string")
    if metadata.get("status") not in STATUSES:
        errors.append(f"{where}: metadata.status must be one of {sorted(STATUSES)}")
    if metadata.get("invocation") not in INVOCATIONS:
        errors.append(f"{where}: metadata.invocation must be one of {sorted(INVOCATIONS)}")
    if len(body.splitlines()) > SKILL_LINES:
        errors.append(f"{where}: body is over {SKILL_LINES} lines")
    sections = headings(body)
    if not sections or sections[0] != "Procedure":
        errors.append(f"{where}: Procedure must be the first section")
    if "Done when" not in sections:
        errors.append(f"{where}: needs a 'Done when' section")
    errors += [f"{where}: {problem}" for problem in host_specific(body, tools)]
    return errors


def host_specific(body: str, tools: set[str]) -> list[str]:
    problems = []
    if HOST_VARIABLE.search(body):
        problems.append("host-specific variable")
    for tool in sorted(tools):
        if re.search(rf"`{re.escape(tool)}`|\bthe {re.escape(tool)} tool\b", body):
            problems.append(f"host tool name '{tool}'; name the capability instead")
    return problems


def lint_agent(path: Path, capabilities: set[str]) -> list[str]:
    where = f"agents/{path.name}"
    try:
        meta, body = split_frontmatter(path.read_text())
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"{where}: {error}"]
    errors = []
    if meta.get("name") != path.stem:
        errors.append(f"{where}: name must match the file name")
    if not meta.get("description"):
        errors.append(f"{where}: needs a description")
    unknown = set(meta.get("tools") or []) - capabilities
    if unknown or not meta.get("tools"):
        errors.append(f"{where}: tools must be known capabilities, got {sorted(unknown)}")
    if meta.get("model") not in {"fast", "strong"}:
        errors.append(f"{where}: model must be fast or strong")
    for section in ("Role", "You receive", "Rules", "Process", "Boundaries", "Return"):
        if section not in headings(body):
            errors.append(f"{where}: missing section '{section}'")
    return errors


def lint_hooks(path: Path, known_hosts: set[str]) -> list[str]:
    errors = []
    for hook in yaml.safe_load(path.read_text()) or []:
        where = f"hooks/{hook.get('id', '?')}"
        if hook.get("event") not in EVENTS:
            errors.append(f"{where}: unknown event")
        if hook.get("mode") not in MODES:
            errors.append(f"{where}: unknown mode")
        if not str(hook.get("run", "")).startswith("puck hook "):
            errors.append(f"{where}: logic must live in the CLI (run: puck hook ...)")
        if not 0 < hook.get("timeout_ms", 0) <= 5_000:
            errors.append(f"{where}: timeout_ms must be 1-5000")
        if hook.get("on_failure") not in {"open", "closed"}:
            errors.append(f"{where}: on_failure must be open or closed")
        unknown = set(hook.get("hosts") or []) - known_hosts
        if unknown:
            errors.append(f"{where}: unknown hosts {sorted(unknown)}")
    return errors


def lint_budget(root: Path) -> list[str]:
    errors = []
    instructions = root / "instructions" / "global.md"
    text = instructions.read_text()
    profile = (root / "profile.md").read_text() if (root / "profile.md").exists() else ""
    if len(text.splitlines()) > INSTRUCTION_LINES:
        errors.append(f"instructions/global.md: over {INSTRUCTION_LINES} lines")
    if len(text) + len(profile) > ALWAYS_ON_CHARS:
        errors.append(f"always-on content is over {ALWAYS_ON_CHARS} characters")
    return errors


def lint_all(root: Path | None = None) -> list[str]:
    root = root or store.home()
    configs = hosts.load(root)
    capabilities = {key for config in configs.values() for key in config["capabilities"]}
    tools = tool_names(configs)
    errors = lint_budget(root)
    for directory in sorted(p for p in (root / "skills").iterdir() if p.is_dir()):
        errors += lint_skill(directory, tools)
    for path in sorted((root / "agents").glob("*.md")):
        errors += lint_agent(path, capabilities)
    errors += lint_hooks(root / "hooks" / "policy.yaml", set(configs))
    return errors


def listing_chars(root: Path) -> int:
    """What every session pays for: all active skill and agent descriptions."""
    total = 0
    for path in [*(root / "skills").glob("*/SKILL.md"), *(root / "agents").glob("*.md")]:
        meta, _ = split_frontmatter(path.read_text())
        if meta.get("metadata", {}).get("status", "active") == "active":
            total += len(meta.get("description", ""))
    return total
