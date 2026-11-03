"""Skill lifecycle: how a drafted skill becomes active.

The retro agent drafts skills. Only the user decides to promote one, and
`promote` refuses a skill that fails lint or its evals.
"""

import subprocess
from pathlib import Path

import adapters
from core.common import paths, store
from core.common.errors import PuckError
from core.common.model import frontmatter, split_frontmatter
from core.primitives import build, lint

def _skill_dir(name: str) -> Path:
    return paths.skills() / name


def new(name: str, description: str, origin: str) -> Path:
    if not lint.NAME.match(name):
        raise PuckError("Skill names are lowercase words joined by hyphens.")
    template = (paths.templates() / "skill.md").read_text()
    meta, body = split_frontmatter(template)
    meta["name"] = name
    meta["description"] = description
    meta["metadata"]["origin"] = origin
    with store.locked("skills"):
        directory = _skill_dir(name)
        try:
            directory.mkdir(parents=True)
        except FileExistsError:
            raise PuckError(
                f"Skill '{name}' exists. Draft a change to it instead of a new skill.") from None
        (directory / "SKILL.md").write_text(frontmatter(meta, body))
    return directory


def set_status(name: str, status: str) -> None:
    path = _skill_dir(name) / "SKILL.md"
    meta, body = split_frontmatter(path.read_text())
    meta["metadata"]["status"] = status
    meta["metadata"]["version"] = str(int(meta["metadata"].get("version", "0")) + 1)
    path.write_text(frontmatter(meta, body))


def promote(name: str, run_evals: bool = True) -> str:
    """Lint, evaluate, activate, rebuild and commit one skill."""
    root = store.home()
    if not (_skill_dir(name) / "SKILL.md").exists():
        raise PuckError(f"No skill '{name}'.")
    with store.locked("skills"):
        errors = [e for e in lint.lint_all(root) if f"skills/{name}" in e]
        # Lint checks evals only for active skills, and this one is still a draft.
        errors += [f"skills/{name}: {p}" for p in lint.eval_problems(_skill_dir(name))]
        if errors:
            raise PuckError("Lint failed:\n" + "\n".join(errors))
        features = root / "docs" / "features.md"
        if features.exists() and name not in lint.ROW.findall(features.read_text()):
            raise PuckError(f"Add a row for '{name}' to docs/features.md first; lint requires one for every active skill.")
        cases = _skill_dir(name) / "evals"
        if not cases.exists():
            raise PuckError(f"Skill '{name}' has no eval cases in {cases}.")
        skill_file = _skill_dir(name) / "SKILL.md"
        original = skill_file.read_text()
        parts = [str(_skill_dir(name))] + ([str(features)] if features.exists() else [])

        def roll_back(reason: str) -> PuckError:
            # Back to exactly the draft it was, version included, and nothing left staged.
            skill_file.write_text(original)
            build.build_all(root)
            subprocess.run(["git", "-C", str(root), "reset", "-q", "--", *parts], capture_output=True)
            row = (" Its row in docs/features.md now fails lint for a draft: remove it, or fix and promote again."
                   if features.exists() else "")
            return PuckError(f"{reason}; '{name}' stays a draft.{row}")

        set_status(name, "active")
        build.build_all(root)
        if run_evals:
            adapter = adapters.primary()
            command = adapter.eval_command(paths.dist(root) / adapter.name, f"{name}-*")
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise roll_back("Evals failed:\n" + result.stdout[-1500:])
        # The skill's row in features.md goes in the same commit, so the pre-commit lint sees both.
        # The pathspec keeps anything else the user has staged out of this commit.
        subprocess.run(["git", "-C", str(root), "add", "--", *parts], check=True)
        commit = subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", f"Promote skill {name}", "--", *parts],
                                capture_output=True, text=True)
        if commit.returncode != 0:
            raise roll_back(
                "The commit was refused, usually by the pre-commit lint. It checks HEAD plus this skill and all of "
                "docs/features.md, so commit any other work that features.md lists first:\n"
                + (commit.stdout + commit.stderr)[-1500:])
    return name
