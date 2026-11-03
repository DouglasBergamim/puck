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


def section(body: str, name: str) -> str:
    """The text under one `## name` heading, up to the next one."""
    match = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


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
    if metadata.get("status") == "active":
        errors += [f"{where}: {problem}" for problem in eval_problems(directory)]
    errors += [f"{where}: {problem}" for problem in host_specific(body, tools)]
    return errors


def eval_problems(directory: Path) -> list[str]:
    """An active skill needs a trigger case and a near miss, each with a prompt and a grader."""
    root = directory / "evals"
    cases = sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
    names = [case.name for case in cases]
    problems = []
    if "triggers" not in names or len(names) < 2:
        problems.append("an active skill needs evals/triggers and at least one near-miss case")
    for case in cases:
        graders = case / "graders"
        if not (case / "prompt.md").is_file() or not graders.is_dir() or not any(graders.glob("*.md")):
            problems.append(f"evals/{case.name} needs prompt.md and at least one graders/*.md")
    return problems


def host_specific(body: str, tools: set[str]) -> list[str]:
    problems = []
    if host_variable_pattern().search(body):
        problems.append("host-specific variable")
    for tool in sorted(tools):
        if re.search(rf"`{re.escape(tool)}`|\bthe {re.escape(tool)} tool\b", body):
            problems.append(f"host tool name '{tool}'; name the capability instead")
    return problems


AGENT_SECTIONS = {
    "lead": ("Role", "Context", "Rules", "Workflow", "Boundaries"),
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
    # Any skill folder counts here, drafts too: promoting one would make the names collide.
    if mode == "lead" and (path.stem in skills or (path.parent.parent / "skills" / path.stem).is_dir()):
        errors.append(f"{where}: a lead becomes a skill, so its name can't match the skill '{path.stem}'")
    for field in ("skills", "agents"):
        if not isinstance(meta.get(field, []), list):
            errors.append(f"{where}: {field} must be a list")
    missing = sorted(set(meta.get("skills") or []) - skills)
    if missing:
        errors.append(f"{where}: unknown or inactive skills {missing}; only active skills are built")
    missing = sorted(set(meta.get("agents") or []) - workers)
    if missing:
        errors.append(f"{where}: agents must name worker agents, got {missing}")
    if (meta.get("agents") or []) and "subagents" not in (meta.get("tools") or []):
        errors.append(f"{where}: starting agents needs the subagents capability")
    for name in AGENT_SECTIONS[mode]:
        if name not in headings(body):
            errors.append(f"{where}: missing section '{name}'")
    if mode == "lead":
        errors += [f"{where}: {problem}" for problem in lint_workflow(meta, body)]
    else:
        if meta.get("workflow"):
            errors.append(f"{where}: only a lead has a workflow; a worker's steps go in its body")
        if "Return" in headings(body) and "status:" not in section(body, "Return"):
            errors.append(f"{where}: Return must include 'status: complete | partial | blocked'")
    errors += [f"{where}: {problem}" for problem in host_specific(body, tools)]
    return errors


def lint_workflow(meta: dict, body: str) -> list[str]:
    """A lead's stages: each delivers something, loads a skill it declares, and is described."""
    stages = meta.get("workflow")
    if not isinstance(stages, list) or not stages:
        return ["a lead needs a workflow: a list of stages, each with stage and delivers"]
    problems, seen = [], set()
    declared = {s for s in (meta.get("skills") or []) if isinstance(s, str)}
    prose = section(body, "Workflow").lower()
    for item in stages:
        if not isinstance(item, dict):
            problems.append("each workflow stage must be a mapping")
            continue
        name = str(item.get("stage", ""))
        unknown = sorted(set(item) - {"stage", "skill", "delivers", "check"})
        if unknown:
            problems.append(f"stage '{name}': unknown fields {unknown}")
        if not NAME.match(name):
            problems.append(f"stage '{name}': ids are lowercase words joined by hyphens")
        if name in seen:
            problems.append(f"stage '{name}' appears twice")
        seen.add(name)
        for field in ("delivers", "skill", "check"):
            if field in item and not isinstance(item[field], str):
                problems.append(f"stage '{name}': {field} must be text")
        if not isinstance(item.get("delivers"), str) or not item["delivers"].strip():
            problems.append(f"stage '{name}': needs delivers")
        skill = item.get("skill")
        if isinstance(skill, str) and skill and skill not in declared:
            problems.append(f"stage '{name}': skill '{skill}' isn't in skills")
        if name and not re.search(rf"\*\*{re.escape(name.lower())}\b", prose):
            problems.append(f"stage '{name}' needs a bold entry (**{name.capitalize()}.**) in the Workflow section")
    return problems


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
    skills = set()
    for directory in (p for p in paths.skills(root).iterdir() if p.is_dir()):
        try:
            if (split_frontmatter((directory / "SKILL.md").read_text())[0].get("metadata") or {}).get("status") == "active":
                skills.add(directory.name)
        except (OSError, ValueError, yaml.YAMLError):
            pass  # lint_skill reports it
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
