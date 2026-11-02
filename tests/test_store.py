import json
import multiprocessing

from core import store


def _write_notes(args):
    path, worker = args
    for number in range(200):
        store.append(path, f"{worker}:{number}:{'x' * 500}\n")


def _bump(path):
    from pathlib import Path

    for _ in range(50):
        with store.locked("counter"):
            value = store.read_json(Path(path))["n"]
            store.write_json(Path(path), {"n": value + 1})


def test_parallel_appends_lose_nothing(tmp_path):
    path = tmp_path / "notes.md"
    with multiprocessing.Pool(8) as pool:
        pool.map(_write_notes, [(path, worker) for worker in range(8)])
    lines = path.read_text().splitlines()
    assert len(lines) == 1600
    assert all(line.endswith("x" * 500) for line in lines)


def test_lock_serialises_read_modify_write(puck_home, tmp_path):
    path = tmp_path / "counter.json"
    store.write_json(path, {"n": 0})
    with multiprocessing.Pool(6) as pool:
        pool.map(_bump, [str(path)] * 6)
    assert json.loads(path.read_text())["n"] == 300


def test_ids_cannot_escape_their_folder():
    assert "/" not in store.safe_id("../../etc/passwd")
    assert not store.safe_id("../x").startswith(".")
