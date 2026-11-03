"""`puck lint`: enforce the primitive specifications."""

import re
from pathlib import Path

import yaml

import adapters
from core.common import paths, store
from core.common.model import CAPABILITIES, EVENTS, split_frontmatter

STANDARD_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
STATUSES = {"draft", "active", "retired"}
INVOCATIONS = {"model", "user"}
MODES = {"observe", "inject", "block"}
SKILL_LINES = 500
INSTRUCTION_LINES = 100
ALWAYS_ON_CHARS = 6_000
DESCRIPTION_CHARS = 1_024
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def headings(body: str) -> list[str]:
    return re.findall(r"^## (.+)$", body, re.MULTILINE)


def tool_names() -> set[str]:
    return {
        tool
        for adapter in adapters.ADAPTERS.values()
        for mapped in adapter.tools.values()
        for tool in mapped.tools
    }


def host_variable_pattern() -> re.Pattern:
    names = sorted({v for a in adapters.ADAPTERS.values() for v in a.variables})
    return re.compile(rf"\$\{{?({'|'.join(names)})_") if names else re.compile(r"(?!)")


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
    if host_variable_pattern().search(body):
        problems.append("host-specific variable")
    for tool in sorted(tools):
        if re.search(rf"`{re.escape(tool)}`|\bthe {re.escape(tool)} tool\b", body):
            problems.append(f"host tool name '{tool}'; name the capability instead")
    return problems


AGENT_SECTIONS = {
    "lead": ("Role", "Rules", "Workflow", "Boundaries"),
    "worker": ("Role", "You receive", "Rules", "Workflow", "Boundaries", "Return"),
}


def lint_agent(path: Path, capabilities: set[str], skills: set[str] = frozenset(),
               workers: set[str] = frozenset(), tools: set[str] = frozenset()) -> list[str]:
    """`skills` and `workers` are the names that exist, so references can be checked."""
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
    mode = meta.get("mode", "worker")
    if mode not in AGENT_SECTIONS:
        errors.append(f"{where}: mode must be lead or worker")
        mode = "worker"
    if mode == "worker" and "ask" in (meta.get("tools") or []):
        errors.append(f"{where}: a worker can't reach the user, so it can't have the ask capability")
    if mode == "lead" and path.stem in skills:
        errors.append(f"{where}: a lead becomes a skill, so its name can't match the skill '{path.stem}'")
    for field in ("skills", "agents"):
        if not isinstance(meta.get(field, []), list):
            errors.append(f"{where}: {field} must be a list")
    missing = sorted(set(meta.get("skills") or []) - skills)
    if missing:
        errors.append(f"{where}: unknown skills {missing}")
    missing = sorted(set(meta.get("agents") or []) - workers)
    if missing:
        errors.append(f"{where}: agents must name worker agents, got {missing}")
    if (meta.get("agents") or []) and "subagents" not in (meta.get("tools") or []):
        errors.append(f"{where}: starting agents needs the subagents capability")
    for section in AGENT_SECTIONS[mode]:
        if section not in headings(body):
            errors.append(f"{where}: missing section '{section}'")
    errors += [f"{where}: {problem}" for problem in host_specific(body, tools)]
    return errors


def lint_hooks(path: Path) -> list[str]:
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
    return errors


def lint_budget(root: Path) -> list[str]:
    errors = []
    text = paths.instructions(root).read_text()
    profile = paths.profile(root).read_text() if paths.profile(root).exists() else ""
    if len(text.splitlines()) > INSTRUCTION_LINES:
        errors.append(f"instructions/global.md: over {INSTRUCTION_LINES} lines")
    if len(text) + len(profile) > ALWAYS_ON_CHARS:
        errors.append(f"always-on content is over {ALWAYS_ON_CHARS} characters")
    return errors


def lint_all(root: Path | None = None) -> list[str]:
    root = root or store.home()
    tools = tool_names()
    errors = lint_budget(root)
    for directory in sorted(p for p in paths.skills(root).iterdir() if p.is_dir()):
        errors += lint_skill(directory, tools)
    skills = {p.name for p in paths.skills(root).iterdir() if p.is_dir()}
    agent_paths = sorted(paths.agents(root).glob("*.md"))
    workers = set()
    for path in agent_paths:
        try:
            if split_frontmatter(path.read_text())[0].get("mode", "worker") == "worker":
                workers.add(path.stem)
        except (OSError, ValueError, yaml.YAMLError):
            pass  # lint_agent reports it
    for path in agent_paths:
        errors += lint_agent(path, set(CAPABILITIES), skills, workers, tools)
    errors += lint_hooks(paths.hook_rules(root))
    return errors
