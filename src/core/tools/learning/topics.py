"""Study topics: one folder each, holding everything a learning session needs.

The concept table in map.md is the learner state. Its row order is the teaching
order, which the roadmap skill sets. Statuses describe what happened, so no
status can be read as mastery.
"""

import re
from pathlib import Path

from core.common import paths, store
from core.common.errors import PuckError

STATUSES = ("unseen", "introduced", "practised", "recalled-later", "can-explain")
READY = STATUSES.index("practised")  # a prerequisite counts once practised
FOLDERS = ("raw", "wiki", "sessions", "exercises", "visuals")
FILES = {"mission": "mission.md", "map": "map.md", "path": "path.md", "sources": "sources.json",
         "report": "report.md"}
TEMPLATE_MARK = "<!-- template -->"
KINDS = ("learn", "research")
DEPTHS = ("orient", "use", "master")
# Mission sections each kind must fill. Applied to and Bounds are optional.
MISSION = {"learn": ("Subject", "Goal", "Why", "Depth", "Out of scope", "Background"),
           "research": ("Question", "Why", "Areas", "Depth", "Out of scope", "Background")}
ROW = re.compile(r"^\|\s*([a-z0-9][a-z0-9-]*)\s*\|(.*)\|\s*$")


def slug(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not cleaned:
        raise PuckError("A topic name needs at least one letter or digit.")
    return cleaned[:60]


def folder(name: str) -> Path:
    path = paths.topic(slug(name))
    if not path.is_dir():
        raise PuckError(f"No topic '{name}'. Run `puck topic list`, or `puck topic new \"{name}\"`.")
    return path


def new(name: str, kind: str = "learn") -> Path:
    """A topic folder. The kind picks the mission template: learn a subject, or research a question."""
    if kind not in KINDS:
        raise PuckError(f"--kind must be one of {', '.join(KINDS)}")
    path = paths.topic(slug(name))
    with store.locked(f"topic-{slug(name)}"):
        for sub in FOLDERS:
            (path / sub).mkdir(parents=True, exist_ok=True)
        for key, template_name in (("mission", f"mission-{kind}.md"), ("map", FILES["map"])):
            target = path / FILES[key]
            if not target.exists():
                template = (paths.templates() / template_name).read_text()
                store.write_text(target, template.replace("{topic}", name))
        if not (path / FILES["sources"]).exists():
            store.write_json(path / FILES["sources"], {"sources": []})
    return path


def all_topics() -> list[str]:
    root = paths.knowledge()
    return sorted(p.name for p in root.iterdir() if (p / FILES["mission"]).exists()) if root.is_dir() else []


def is_filled(path: Path) -> bool:
    """A file counts once it exists and is no longer an untouched template."""
    return path.exists() and TEMPLATE_MARK not in path.read_text() and path.read_text().strip() != ""


# Concept table -----------------------------------------------------------------

def concepts(name: str) -> list[dict]:
    """Rows of the `## Concepts` table in map.md, in teaching order."""
    text = (folder(name) / FILES["map"]).read_text()
    section = text.split("## Concepts", 1)[1] if "## Concepts" in text else ""
    rows = []
    for line in section.splitlines():
        if line.startswith("## "):
            break
        match = ROW.match(line.strip())
        if not match or match.group(1) == "id":
            continue
        cells = [cell.strip() for cell in match.group(2).split("|")]
        if len(cells) < 3:
            raise PuckError(f"map.md row '{match.group(1)}' needs: id | concept | prerequisites | status")
        concept, prereqs, status = cells[0], cells[1], cells[2]
        if status not in STATUSES:
            raise PuckError(f"map.md: '{match.group(1)}' has status '{status}'; use one of {', '.join(STATUSES)}")
        rows.append({
            "id": match.group(1),
            "concept": concept,
            "prerequisites": [p.strip() for p in prereqs.split(",") if p.strip() not in ("", "-")],
            "status": status,
        })
    return rows


def next_concept(name: str) -> dict | None:
    """The first concept, in teaching order, that is unfinished and whose prerequisites are practised.

    When nothing new is ready, return the practised concept least far along, for recall.
    """
    rows = concepts(name)
    rank = {row["id"]: STATUSES.index(row["status"]) for row in rows}
    for row in rows:
        ready = all(rank.get(p, len(STATUSES)) >= READY for p in row["prerequisites"])
        if rank[row["id"]] < READY and ready:
            return row
    review = [row for row in rows if READY <= rank[row["id"]] < len(STATUSES) - 1]
    return min(review, key=lambda row: rank[row["id"]]) if review else None


def set_status(name: str, concept_id: str, status: str) -> None:
    if status not in STATUSES:
        raise PuckError(f"Status must be one of {', '.join(STATUSES)}")
    path = folder(name) / FILES["map"]
    with store.locked(f"topic-{slug(name)}"):
        lines = path.read_text().splitlines(keepends=True)
        in_table, found = False, False
        for index, line in enumerate(lines):
            if line.startswith("## "):
                in_table = line.startswith("## Concepts")
            match = ROW.match(line.strip()) if in_table else None
            if match and match.group(1) == concept_id:
                cells = [cell.strip() for cell in match.group(2).split("|")]
                cells[2] = status
                lines[index] = f"| {concept_id} | " + " | ".join(cells) + " |\n"
                found = True
        if not found:
            raise PuckError(f"No concept '{concept_id}' in {path}. Ids: {[r['id'] for r in concepts(name)]}")
        store.write_text(path, "".join(lines))


# Sessions ----------------------------------------------------------------------

def sessions(name: str) -> list[Path]:
    return sorted((folder(name) / "sessions").glob("[0-9][0-9][0-9][0-9].md"))


def record(name: str, text: str, statuses: dict[str, str]) -> Path:
    """Write the next session record, then apply its status changes to the map."""
    for concept_id, status in statuses.items():
        set_status(name, concept_id, status)
    with store.locked(f"topic-{slug(name)}-sessions"):
        number = len(sessions(name)) + 1
        path = folder(name) / "sessions" / f"{number:04d}.md"
        changes = "".join(f"- {cid}: {status}\n" for cid, status in statuses.items())
        body = text.rstrip() + "\n"
        if changes:
            body += "\n## Status changes\n" + changes
        store.write_text(path, body)
    return path


def status_report(name: str) -> str:
    path = folder(name)
    rows = concepts(name)
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    lines = [f"Topic: {slug(name)} ({path})"]
    missing = [key for key in ("mission", "map", "path") if not is_filled(path / FILES[key])]
    if missing:
        lines.append("Not written yet: " + ", ".join(f"{k}.md" for k in missing))
    lines.append("Concepts: " + ", ".join(f"{n} {s}" for s, n in counts.items() if n) if rows else "Concepts: none yet")
    upcoming = next_concept(name) if rows else None
    if upcoming:
        lines.append(f"Next: {upcoming['id']} ({upcoming['concept']}), now {upcoming['status']}")
    done = sessions(name)
    if done:
        lines.append(f"Last session: {done[-1]}")
        lines.append(done[-1].read_text().strip())
    else:
        lines.append("No sessions yet: this is a first session, so skip the recall opening.")
    return "\n".join(lines)


def check(name: str, required: list[str]) -> list[str]:
    """What's missing or still a template, for use as a task check."""
    path = folder(name)
    problems = []
    for key in required:
        if key not in FILES:
            raise PuckError(f"--has takes {', '.join(FILES)}")
        target = path / FILES[key]
        if key == "sources":
            ledger = store.read_json(target) or {}
            if not ledger.get("sources"):
                problems.append("sources.json has no sources")
        elif not is_filled(target):
            problems.append(f"{FILES[key]} is missing or still a template")
        elif key == "mission":
            problems += mission_problems(target.read_text())
    if "map" in required and not problems:
        if not concepts(name):
            problems.append("map.md has no rows in its ## Concepts table")
    return problems


def sections(text: str) -> dict[str, str]:
    """Each `## ` heading's text, without HTML comments, which templates use for guidance."""
    found, current = {}, None
    for line in re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            found[current] = ""
        elif current:
            found[current] += line.strip() + "\n"
    return {heading: body.strip() for heading, body in found.items()}


def mission_problems(text: str) -> list[str]:
    """A mission is filled when its kind's sections have text and Depth is one word from DEPTHS."""
    found = sections(text)
    kind = "learn" if "Subject" in found else "research" if "Question" in found else None
    if not kind:
        return ["mission.md needs a ## Subject (learn) or a ## Question (research) section"]
    problems = [f"mission.md: ## {heading} is empty" for heading in MISSION[kind] if not found.get(heading)]
    depth = found.get("Depth", "").split()
    if depth and depth[0].strip(".").lower() not in DEPTHS:
        problems.append(f"mission.md: ## Depth must start with one of {', '.join(DEPTHS)}")
    return problems
