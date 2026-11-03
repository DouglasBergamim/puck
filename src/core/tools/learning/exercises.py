"""Exercises: each one is a folder whose answer key exists before the learner is asked.

exercises/<id>/exercise.json describes it:
  {"concept": "<concept id>", "kind": "code|math|concept|design", "check": "<command>"}
Code exercises have a `check` command, usually their tests, and pass only on exit 0.
The other kinds are graded by the grader agent against key.md and rubric.md.
"""

import json
from pathlib import Path

from core.common import store
from core.common.errors import PuckError
from core.tools.learning import topics
from core.tools.work.tasks import run_command

KINDS = ("code", "math", "concept", "design")
TIMEOUT = 300


def folder(topic: str, exercise_id: str) -> Path:
    path = topics.folder(topic) / "exercises" / exercise_id
    if not (path / "exercise.json").exists():
        raise PuckError(f"No exercise '{exercise_id}' in {topic}: {path}/exercise.json is missing.")
    return path


def spec(topic: str, exercise_id: str) -> dict:
    try:
        data = json.loads((folder(topic, exercise_id) / "exercise.json").read_text())
    except json.JSONDecodeError as error:
        raise PuckError(f"exercise.json for {exercise_id} isn't valid JSON: {error}") from error
    if data.get("kind") not in KINDS:
        raise PuckError(f"exercise.json 'kind' must be one of {', '.join(KINDS)}")
    return data


def check(topic: str, exercise_id: str) -> tuple[bool, str]:
    """Run a code exercise's check. Only a real exit 0 passes."""
    data = spec(topic, exercise_id)
    if not data.get("check"):
        raise PuckError(f"{exercise_id} is a {data['kind']} exercise with no check command; "
                        "the grader agent scores it against key.md and rubric.md.")
    path = folder(topic, exercise_id)
    code, output = run_command(data["check"], path, TIMEOUT)
    store.write_text(path / "last-check.txt", f"$ {data['check']}\nexit {code}\n{output}")
    return code == 0, output[-3000:]
