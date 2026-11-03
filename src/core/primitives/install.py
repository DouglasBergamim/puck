"""Load Puck in every session of a harness, and take it out again.

The adapter says what to change; this module changes it. It links the built
package where the harness looks for plugins, so a later `puck build` reaches new
sessions without reinstalling, and merges permissions into the harness's user
settings. Uninstall removes only what install added.
"""

import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from adapters.base import Adapter
from core.common import paths, store
from core.common.errors import PuckError
from core.common.model import Install
from core.primitives import build


def _plan(adapter: Adapter, home: Path, commands: tuple[str, ...]) -> Install:
    plan = adapter.install(PurePosixPath(home), commands)
    if plan is None:
        raise PuckError(f"{adapter.name} has no installer yet. Point it at {paths.dist(home) / adapter.name}.")
    return plan


def _read_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PuckError(f"{path} isn't valid JSON ({error}), so it was left alone. Fix it and run this again.")
    if not isinstance(settings, dict):
        raise PuckError(f"{path} isn't a JSON object, so it was left alone.")
    return settings


def _write_settings(path: Path, settings: dict) -> None:
    store.write_text(path, json.dumps(settings, indent=2) + "\n")


def ensure_command(home: Path) -> str | None:
    """Put `puck` on the PATH, since the host's hooks call it. None if it already is."""
    if shutil.which("puck"):
        return None
    if not shutil.which("uv"):
        raise PuckError("Installing the puck command needs uv: https://docs.astral.sh/uv/")
    result = subprocess.run(["uv", "tool", "install", "--editable", str(home)], capture_output=True, text=True)
    if result.returncode != 0:
        raise PuckError(f"uv couldn't install the puck command:\n{result.stderr.strip()}")
    return "Installed the puck command with uv"


def install(adapter: Adapter, home: Path, user_home: Path, commands: tuple[str, ...] = ()) -> list[str]:
    plan = _plan(adapter, home, commands)
    path = user_home / plan.settings if plan.settings else None
    settings = _read_settings(path) if path else {}  # fail before changing anything
    link = user_home / plan.link
    if link.exists() and not link.is_symlink():
        raise PuckError(f"{link} already exists and isn't a link Puck made. Move it away and run this again.")
    installed = ensure_command(home)
    package = build.build_adapter(adapter, home)
    done = [installed] if installed else []

    if link.is_symlink():
        link.unlink()
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(package, target_is_directory=True)
    done.append(f"Linked {link} -> {package}")

    if path:
        permissions = settings.setdefault("permissions", {})
        for key, values in (("allow", plan.allow), ("additionalDirectories", plan.directories)):
            if values:
                current = permissions.setdefault(key, [])
                current += [v for v in values if v not in current]
        if plan.env:
            settings.setdefault("env", {}).update(dict(plan.env))
        _write_settings(path, settings)
        done.append(f"Updated {path}: {len(plan.allow)} permission rules, "
                    f"{len(plan.directories)} directory, {len(plan.env)} environment variable")
    return done


def uninstall(adapter: Adapter, home: Path, user_home: Path, commands: tuple[str, ...] = ()) -> list[str]:
    plan = _plan(adapter, home, commands)
    done = []

    link = user_home / plan.link
    if link.is_symlink():
        link.unlink()
        done.append(f"Removed {link}")
    elif link.exists():
        done.append(f"Left {link} alone: it isn't a link Puck made.")

    path = user_home / plan.settings if plan.settings else None
    if path and path.exists():
        settings = _read_settings(path)
        permissions = settings.get("permissions", {})
        for key, values in (("allow", plan.allow), ("additionalDirectories", plan.directories)):
            if key in permissions:
                permissions[key] = [v for v in permissions[key] if v not in values]
                if not permissions[key]:
                    del permissions[key]
        if "permissions" in settings and not permissions:
            del settings["permissions"]
        env = settings.get("env", {})
        for name, value in plan.env:
            if env.get(name) == value:
                del env[name]
        if "env" in settings and not env:
            del settings["env"]
        _write_settings(path, settings)
        done.append(f"Removed Puck's entries from {path}")
    return done or ["Nothing to remove."]
