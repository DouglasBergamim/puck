"""`puck build`: turn the behaviour folders into per-host packages under dist/."""

import json
import math
import shutil
from pathlib import Path

import yaml

from cli import hosts, lint, store

VERSION = "0.1.0"
DESCRIPTION = "A layer in front of any agent harness that optimises LLM context and improves its tools"


def active_skills(root: Path) -> list[tuple[Path, dict, str]]:
    found = []
    for directory in sorted(p for p in (root / "skills").iterdir() if p.is_dir()):
        meta, body = lint.split_frontmatter((directory / "SKILL.md").read_text())
        if meta.get("metadata", {}).get("status") == "active":
            found.append((directory, meta, body))
    return found


def frontmatter(meta: dict, body: str) -> str:
    return f"---\n{yaml.safe_dump(meta, sort_keys=False)}---\n{body}"


def write_skill(directory: Path, meta: dict, body: str, target: Path, host: dict, root: Path) -> None:
    out = target / "skills" / directory.name
    shutil.copytree(directory, out, ignore=shutil.ignore_patterns("evals", "__pycache__"))
    head = {key: meta[key] for key in ("name", "description") if key in meta}
    if meta.get("metadata", {}).get("invocation") == "user":
        head["disable-model-invocation"] = True
    (out / "SKILL.md").write_text(frontmatter(head, body))
    reference = root / "hosts" / "refs" / f"{host['name']}-tools.md"
    (out / "references").mkdir(exist_ok=True)
    shutil.copy(reference, out / "references" / "host-tools.md")


def copy_evals(directory: Path, target: Path) -> None:
    """Claude's plugin eval reads evals/ at the plugin root; case names carry the skill."""
    for case in sorted((directory / "evals").glob("*")):
        if case.is_dir():
            shutil.copytree(case, target / "evals" / f"{directory.name}-{case.name}")


def write_agent(path: Path, target: Path, host: dict) -> None:
    meta, body = lint.split_frontmatter(path.read_text())
    tools = [t for capability in meta["tools"] for t in host["capabilities"][capability]]
    tools = list(dict.fromkeys(tools))
    head = {"name": meta["name"], "description": meta["description"]}
    if host["agent_format"] == "claude":
        head |= {"tools": ", ".join(tools), "model": host["models"][meta["model"]]}
        if meta.get("max_turns"):
            head["maxTurns"] = int(meta["max_turns"])
        name = f"{meta['name']}.md"
    else:
        head["tools"] = tools
        name = f"{meta['name']}.agent.md"
    out = target / "agents" / name
    out.parent.mkdir(exist_ok=True)
    out.write_text(frontmatter(head, body))


def hook_file(policy: list[dict], host: dict) -> dict:
    events: dict[str, list] = {}
    for hook in policy:
        if host["name"] not in hook["hosts"]:
            continue
        native = host["hook_events"][hook["event"]]
        command = f"{hook['run']} --event {hook['event']} --host {host['name']}"
        seconds = math.ceil(hook["timeout_ms"] / 1000)
        if host["hook_format"] == "claude":
            entry = {"hooks": [{"type": "command", "command": command, "timeout": seconds}]}
        else:
            entry = {"type": "command", "bash": command, "timeoutSec": seconds}
        events.setdefault(native, []).append(entry)
    if host["hook_format"] == "claude":
        return {"description": "Puck session hooks", "hooks": events}
    return {"version": 1, "hooks": events}


def build_host(root: Path, host: dict, policy: list[dict]) -> Path:
    target = root / "dist" / host["name"]
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    manifest = target / host["manifest"]
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(
        {"name": "puck", "version": VERSION, "description": DESCRIPTION}, indent=2) + "\n")
    for directory, meta, body in active_skills(root):
        write_skill(directory, meta, body, target, host, root)
        if host["hook_format"] == "claude":
            copy_evals(directory, target)
    for path in sorted((root / "agents").glob("*.md")):
        write_agent(path, target, host)
    hooks_path = target / "hooks" / "hooks.json"
    hooks_path.parent.mkdir()
    hooks_path.write_text(json.dumps(hook_file(policy, host), indent=2) + "\n")
    instructions = (root / "instructions" / "global.md").read_text()
    profile = root / "profile.md"
    if profile.exists():
        instructions += "\n" + profile.read_text()
    (target / "instructions.md").write_text(instructions)
    return target


def build_all(root: Path | None = None) -> list[Path]:
    root = root or store.home()
    policy = yaml.safe_load((root / "hooks" / "policy.yaml").read_text()) or []
    return [build_host(root, host, policy) for host in hosts.load(root).values()]
