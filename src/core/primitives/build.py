"""`puck build`: load the context, run each adapter, write dist/."""

import shutil
import stat
from pathlib import Path

import yaml

import adapters
from adapters.base import Adapter
from core.common import paths, store
from core.common.model import Agent, File, HookRule, Skill, split_frontmatter

VERSION = "0.1.0"


def _file(path: Path, relative: Path) -> File:
    executable = bool(path.stat().st_mode & stat.S_IXUSR)
    return File(relative.as_posix(), path.read_bytes(), executable)


def _tree(root: Path, skip: tuple[str, ...] = ()) -> tuple[File, ...]:
    found = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root)
        if relative.parts[0] not in skip and "__pycache__" not in relative.parts:
            found.append(_file(path, relative))
    return tuple(found)


def load_skills(root: Path) -> list[Skill]:
    skills = []
    for directory in sorted(p for p in paths.skills(root).iterdir() if p.is_dir()):
        meta, body = split_frontmatter((directory / "SKILL.md").read_text())
        metadata = meta.get("metadata", {})
        if metadata.get("status") != "active":
            continue
        evals = _tree(directory / "evals") if (directory / "evals").is_dir() else ()
        skills.append(Skill(
            name=meta["name"], description=meta["description"],
            invocation=metadata.get("invocation", "model"), body=body,
            files=_tree(directory, skip=("SKILL.md", "evals")), evals=evals,
        ))
    return skills


def load_agents(root: Path) -> list[Agent]:
    agents = []
    for path in sorted(paths.agents(root).glob("*.md")):
        meta, body = split_frontmatter(path.read_text())
        turns = meta.get("max_turns")
        agents.append(Agent(
            name=meta["name"], description=meta["description"], tools=tuple(meta["tools"]),
            model=meta["model"], max_turns=int(turns) if turns else None, body=body,
            mode=meta.get("mode", "worker"), skills=tuple(meta.get("skills") or ()),
            agents=tuple(meta.get("agents") or ()),
        ))
    return agents


def load_rules(root: Path) -> list[HookRule]:
    return [HookRule(**rule) for rule in yaml.safe_load(paths.hook_rules(root).read_text()) or []]


def load_instructions(root: Path) -> str:
    text = paths.instructions(root).read_text()
    profile = paths.profile(root)
    return text + "\n" + profile.read_text() if profile.exists() else text


def render(adapter: Adapter, root: Path) -> list[File]:
    files = adapter.render_manifest(VERSION)
    for skill in load_skills(root):
        files += adapter.render_skill(skill)
    for agent in load_agents(root):
        files += adapter.render_lead(agent) if agent.mode == "lead" else adapter.render_agent(agent)
    files += adapter.render_hooks(load_rules(root))
    files += adapter.render_instructions(load_instructions(root))
    return files


def write(files: list[File], target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    for item in files:
        path = target / item.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(item.content)
        if item.executable:
            path.chmod(path.stat().st_mode | stat.S_IXUSR)


def build_adapter(adapter: Adapter, root: Path) -> Path:
    target = paths.dist(root) / adapter.name
    write(render(adapter, root), target)
    return target


def build_all(root: Path | None = None) -> list[Path]:
    root = root or store.home()
    return [build_adapter(adapter, root) for adapter in adapters.ADAPTERS.values()]
