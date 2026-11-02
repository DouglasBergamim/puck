"""Paths and concurrency-safe file writes. Every shared write goes through here."""

import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path


def home() -> Path:
    override = os.environ.get("PUCK_HOME")
    return Path(override) if override else Path(__file__).resolve().parent.parent


def state_dir() -> Path:
    return home() / "state"


def safe_id(value: str) -> str:
    """Session IDs come from hosts, so they must not be able to escape state/."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", value or "unknown").lstrip(".")
    return cleaned[:128] or "unknown"


@contextmanager
def locked(name: str):
    """Hold an exclusive lock shared by every puck process using this name."""
    path = state_dir() / "locks" / f"{safe_id(name)}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.write(text)
        handle.flush()


def write_json(path: Path, value: dict) -> None:
    """Replace atomically, so a reader never sees a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
    os.replace(tmp, path)


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
