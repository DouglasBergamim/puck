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
    errors += [f"{where}: {problem}" for problem in eval_format(directory)]
    errors += [f"{where}: {problem}" for problem in host_specific(body, tools)]
    return errors


GRADER_TYPES = {"tool_used", "llm", "regex", "file_exists", "baseline"}


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


def eval_format(directory: Path) -> list[str]:
    """Each eval file is in the shape the eval runner reads, so a bad case fails here, not at promote."""
    problems = []
    for prompt in sorted((directory / "evals").glob("*/prompt.md")):
        where = f"evals/{prompt.parent.name}/prompt.md"
        try:
            meta, body = split_frontmatter(prompt.read_text())
        except (ValueError, yaml.YAMLError) as error:
            problems.append(f"{where}: {error}")
            continue
        turns = meta.get("max_turns")
        if not isinstance(turns, int) or isinstance(turns, bool) or turns < 1:
            problems.append(f"{where}: max_turns must be a positive whole number")
        tools = meta.get("allowed_tools")
        if tools is not None and not (isinstance(tools, list) and all(isinstance(t, str) for t in tools)):
            problems.append(f"{where}: allowed_tools must be a list of tool names")
        if not body.strip():
            problems.append(f"{where}: needs the prompt text after the frontmatter")
    for grader in sorted((directory / "evals").glob("*/graders/*.md")):
        where = f"evals/{grader.parent.parent.name}/graders/{grader.name}"
        try:
            meta, body = split_frontmatter(grader.read_text())
        except (ValueError, yaml.YAMLError) as error:
            problems.append(f"{where}: {error}")
            continue
        kind = meta.get("type")
        if kind not in GRADER_TYPES:
            problems.append(f"{where}: type must be one of {sorted(GRADER_TYPES)}")
        elif kind == "tool_used":
            bounds = [meta.get("min"), meta.get("max")]
            if not isinstance(meta.get("tool"), str) or not meta["tool"]:
                problems.append(f"{where}: a tool_used grader names its tool")
            if not all(isinstance(b, int) and not isinstance(b, bool) for b in bounds) or not 0 <= bounds[0] <= bounds[1]:
                problems.append(f"{where}: min and max must be whole numbers with 0 <= min <= max")
            pattern = meta.get("input_match")
            if not isinstance(pattern, str) or not pattern:
                problems.append(f"{where}: a tool_used grader needs input_match, the pattern its call must match")
            else:
                try:
                    re.compile(pattern)
                except re.error as error:
                    problems.append(f"{where}: input_match isn't a valid pattern: {error}")
        elif kind == "llm" and not body.strip():
            problems.append(f"{where}: an llm grader needs its PASS and FAIL criteria in the body")
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
    agents = {path.stem for path in agent_paths}
    errors += lint_features(root, skills, agents, hook_ids(paths.hook_rules(root)))
    errors += lint_references(root, skills | agents | all_skill_names(root))
    return errors


ROW = re.compile(r"^\| `([a-z0-9]+(?:-[a-z0-9]+)*)` \|", re.MULTILINE)
SLASH = re.compile(r"/puck:([a-z0-9-]+)")
CHAINED = re.compile(r"`([a-z0-9-]+)`(?=\s*→)|(?<=→)\s*`([a-z0-9-]+)`")


def hook_ids(path: Path) -> set[str]:
    try:
        return {str(rule.get("id")) for rule in yaml.safe_load(path.read_text()) or [] if isinstance(rule, dict)}
    except (OSError, yaml.YAMLError):
        return set()  # lint_hooks reports it


def all_skill_names(root: Path) -> set[str]:
    return {p.name for p in paths.skills(root).iterdir() if p.is_dir()}


def features_problems(text: str, skills: set[str], agents: set[str], hooks: set[str]) -> list[str]:
    """docs/features.md lists every active skill, agent and hook, and nothing else."""
    rows = set(ROW.findall(text))
    problems = [f"docs/features.md: no row for {kind} '{name}'"
                for kind, names in (("skill", skills), ("agent", agents), ("hook", hooks))
                for name in sorted(names - rows)]
    problems += [f"docs/features.md: row for '{name}', which isn't an active skill, agent or hook"
                 for name in sorted(rows - skills - agents - hooks)]
    return problems


def lint_features(root: Path, skills: set[str], agents: set[str], hooks: set[str]) -> list[str]:
    path = root / "docs" / "features.md"
    return features_problems(path.read_text(), skills, agents, hooks) if path.exists() else []


def reference_files(root: Path) -> list[Path]:
    """Docs and context that name skills and agents. docs/research/ cites other projects' skills."""
    found = [root / name for name in ("AGENTS.md", "README.md")]
    found += sorted((root / "docs").glob("*.md"))
    found += sorted(p for p in paths.context(root).rglob("*.md") if "knowledge" not in p.relative_to(paths.context(root)).parts)
    return [p for p in found if p.is_file()]


def lint_references(root: Path, known: set[str]) -> list[str]:
    """`/puck:<name>` and backticked names next to a → must be a real skill or agent."""
    problems = []
    for path in reference_files(root):
        where = path.relative_to(root).as_posix()
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            names = SLASH.findall(line)
            if "→" in line:
                names += [a or b for a, b in CHAINED.findall(line)]
            problems += [f"{where}:{number}: `{name}` isn't a skill or agent"
                         for name in dict.fromkeys(names) if name not in known]
    return problems
