"""Skill lifecycle and proposals: how behaviour changes get into Puck."""

import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

from cli import build, lint, store, tasks

KINDS = {"promote", "skill-patch", "instruction", "project"}


def _skill_dir(name: str) -> Path:
    return store.home() / "skills" / name


def new(name: str, description: str, origin: str) -> Path:
    if not lint.NAME.match(name):
        raise tasks.TaskError("Skill names are lowercase words joined by hyphens.")
    template = (store.home() / "templates" / "skill.md").read_text()
    meta, body = lint.split_frontmatter(template)
    meta["name"] = name
    meta["description"] = description
    meta["metadata"]["origin"] = origin
    with store.locked("skills"):
        directory = _skill_dir(name)
        try:
            directory.mkdir(parents=True)
        except FileExistsError:
            raise tasks.TaskError(
                f"Skill '{name}' exists. Propose a skill-patch instead of a new skill.") from None
        (directory / "SKILL.md").write_text(build.frontmatter(meta, body))
    return directory


def set_status(name: str, status: str) -> None:
    path = _skill_dir(name) / "SKILL.md"
    meta, body = lint.split_frontmatter(path.read_text())
    meta["metadata"]["status"] = status
    meta["metadata"]["version"] = str(int(meta["metadata"].get("version", "0")) + 1)
    path.write_text(build.frontmatter(meta, body))


def try_draft(name: str) -> str:
    """Build a throwaway plugin containing this draft, without installing it."""
    root = store.home()
    target = Path(tempfile.mkdtemp(prefix=f"puck-try-{name}-"))
    shutil.copytree(root, target / "home", ignore=shutil.ignore_patterns(
        ".git", ".venv", "state", "dist", "knowledge", "tasks", "proposals", "__pycache__"))
    set_status_in = target / "home" / "skills" / name / "SKILL.md"
    meta, body = lint.split_frontmatter(set_status_in.read_text())
    meta["metadata"]["status"] = "active"
    set_status_in.write_text(build.frontmatter(meta, body))
    build.build_all(target / "home")
    return f"claude --plugin-dir {target / 'home' / 'dist' / 'claude'}"


def promote(name: str, run_evals: bool = True) -> str:
    """Lint, evaluate, activate, rebuild and commit one skill."""
    root = store.home()
    if not (_skill_dir(name) / "SKILL.md").exists():
        raise tasks.TaskError(f"No skill '{name}'.")
    with store.locked("skills"):
        errors = [e for e in lint.lint_all(root) if f"skills/{name}" in e]
        if errors:
            raise tasks.TaskError("Lint failed:\n" + "\n".join(errors))
        cases = _skill_dir(name) / "evals"
        if not cases.exists():
            raise tasks.TaskError(f"Skill '{name}' has no eval cases in {cases}.")
        set_status(name, "active")
        build.build_all(root)
        if run_evals:
            result = subprocess.run(
                ["claude", "plugin", "eval", str(root / "dist" / "claude"), "--runs", "1",
                 "--case", f"{name}-*"], capture_output=True, text=True)
            if result.returncode != 0:
                set_status(name, "draft")
                build.build_all(root)
                raise tasks.TaskError("Evals failed; skill stays a draft:\n" + result.stdout[-1500:])
        subprocess.run(["git", "-C", str(root), "add", f"skills/{name}"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", f"Promote skill {name}"],
                       check=True)
    return name


def _proposal_paths() -> list[Path]:
    return sorted((store.home() / "proposals").glob("*.md"))


def propose(kind: str, task_id: str, target: str, summary: str, body: str) -> Path:
    if kind not in KINDS:
        raise tasks.TaskError(f"--kind must be one of {sorted(KINDS)}")
    slug = "-".join(re.findall(r"[a-z0-9]+", summary.lower())[:5]) or "proposal"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    head = {"kind": kind, "task": task_id, "target": target, "summary": summary}
    text = f"---\n{yaml.safe_dump(head, sort_keys=False)}---\n{body}\n"
    folder = store.home() / "proposals"
    folder.mkdir(exist_ok=True)
    with store.locked("proposals"):
        number = 1
        path = folder / f"{stamp}-{slug}.md"
        while path.exists():
            number += 1
            path = folder / f"{stamp}-{slug}-{number}.md"
        path.write_text(text)
    return path


def list_proposals() -> list[dict]:
    found = []
    for path in _proposal_paths():
        meta, body = lint.split_frontmatter(path.read_text())
        found.append({"id": path.stem, "body": body, **meta})
    return found


def resolve(proposal_id: str, approve: bool, run_evals: bool = True) -> str:
    path = store.home() / "proposals" / f"{store.safe_id(proposal_id)}.md"
    if not path.exists():
        raise tasks.TaskError(f"No proposal '{proposal_id}'. Run `puck proposal list`.")
    meta, body = lint.split_frontmatter(path.read_text())
    message = "Rejected."
    if approve:
        message = _apply(meta, body, run_evals)
    done = path.parent / "done"
    done.mkdir(exist_ok=True)
    path.rename(done / path.name)
    return message


def _apply(meta: dict, body: str, run_evals: bool) -> str:
    root = store.home()
    if meta["kind"] == "promote":
        promote(meta["target"], run_evals)
        return f"Promoted {meta['target']}."
    if meta["kind"] == "skill-patch":
        result = subprocess.run(["git", "-C", str(root), "apply", "-"], input=body.lstrip("\n"),
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise tasks.TaskError(f"Patch doesn't apply; proposal kept:\n{result.stderr}")
        return f"Patched {meta['target']}. It takes effect after the next promote or build."
    if meta["kind"] == "instruction":
        path = root / "instructions" / "global.md"
        original = path.read_text()
        with store.locked("skills"):
            path.write_text(original.rstrip("\n") + "\n" + body.strip() + "\n")
            errors = lint.lint_budget(root)
            if errors:
                path.write_text(original)
                raise tasks.TaskError("Over budget; proposal kept:\n" + "\n".join(errors))
        return "Added to the global instructions."
    return f"Approved. Apply this to {meta['target']}:\n{body.strip()}"
