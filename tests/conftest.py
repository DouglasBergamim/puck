import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def puck_home(tmp_path, monkeypatch):
    """A throwaway Puck home holding a copy of the real behaviour folders."""
    for name in ("hosts", "hooks", "skills", "instructions", "templates"):
        shutil.copytree(REPO / name, tmp_path / name)
    (tmp_path / "agents").mkdir()
    shutil.copy(REPO / "profile.md", tmp_path / "profile.md")
    monkeypatch.setenv("PUCK_HOME", str(tmp_path))
    return tmp_path
