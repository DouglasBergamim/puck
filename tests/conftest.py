import shutil
from pathlib import Path

import pytest

from core import paths

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def puck_home(tmp_path, monkeypatch):
    """A throwaway Puck home holding a copy of the real behaviour folders."""
    for name in ("skills", "instructions", "templates"):
        shutil.copytree(paths.context(REPO) / name, paths.context(tmp_path) / name)
    shutil.copy(paths.hook_rules(REPO), paths.hook_rules(tmp_path))
    paths.agents(tmp_path).mkdir(parents=True)
    shutil.copy(paths.profile(REPO), paths.profile(tmp_path))
    monkeypatch.setenv("PUCK_HOME", str(tmp_path))
    return tmp_path
