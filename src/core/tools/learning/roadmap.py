"""The roadmap page: path.md, the concept table and the ledger, as one offline HTML file.

The page is computed, never written by the model, so it always matches the files.
It doubles as the progress view: each concept shows its status in shape, word and colour.
"""

import html
import re
from pathlib import Path

from core.common import store
from core.common.errors import PuckError
from core.tools.learning import topics
from core.tools.learning.sources import ledger

PAGE = "visuals/roadmap.html"
STAGE = re.compile(r"^## Stage (\d+):\s*(.+)$")
FIELD = re.compile(r"^- ([A-Za-z][^:]*?):\s*(.*)$")
SHAPES = {"unseen": "○", "introduced": "◔", "practised": "◑", "recalled-later": "◕", "can-explain": "●"}


def parse(text: str) -> dict:
    """The header lines, the stages with their fields, and the Skip-unless list."""
    path = {"title": "", "header": {}, "stages": [], "skip": []}
    section = "header"
    for line in text.splitlines():
        stage = STAGE.match(line)
        if line.startswith("# ") and not path["title"]:
            path["title"] = line[2:].split(":", 1)[-1].strip()
        elif stage:
            path["stages"].append({"number": stage.group(1), "name": stage.group(2).strip(), "fields": {}})
            section = "stage"
        elif line.startswith("## "):
            section = "skip" if line[3:].strip().lower().startswith("skip unless") else "other"
        elif section == "header" and ":" in line and not line.startswith(("#", "`", " ")):
            key, _, value = line.partition(":")
            path["header"][key.strip().lower()] = value.strip()
        elif section == "stage" and (field := FIELD.match(line)):
            key = field.group(1).split("(")[0].strip().lower()
            path["stages"][-1]["fields"][key] = field.group(2).strip()
            if key in ("concepts", "time"):
                path["stages"][-1]["fields"][key] = field.group(2).strip().rstrip(".")
        elif section == "skip" and line.startswith("- "):
            path["skip"].append(line[2:].strip())
    return path


def render(name: str) -> Path:
    """Write the topic's roadmap page and return its path."""
    folder = topics.folder(name)
    path_file = folder / topics.FILES["path"]
    if not topics.is_filled(path_file):
        raise PuckError("path.md is missing or still a template: run the roadmap skill first.")
    text = path_file.read_text()
    path = parse(text)
    if not path["stages"]:
        raise PuckError("path.md has no `## Stage N: name` sections.")
    mission = topics.sections((folder / topics.FILES["mission"]).read_text())
    rows = {row["id"]: row for row in topics.concepts(name)}
    sources = {source["id"]: source for source in ledger.load(name)}
    target = folder / PAGE
    store.write_text(target, _page(name, mission, path, rows, sources, bool(topics.agreed(name))))
    return target


# HTML ---------------------------------------------------------------------------

def _inline(text: str, sources: dict) -> str:
    """Escape, then link ledger ids like [s3] and keep **bold**."""
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)

    def cite(match: re.Match) -> str:
        source = sources.get(match.group(1))
        if not source:
            return match.group(0)
        label = html.escape(f"{source['title']} ({source.get('year') or 'n.d.'})", quote=True)
        url = source.get("url") or (f"https://doi.org/{source['doi']}" if source.get("doi") else "")
        if url:
            return f'<a class="cite" href="{html.escape(url, quote=True)}" title="{label}">[{match.group(1)}]</a>'
        return f'<abbr class="cite" title="{label}">[{match.group(1)}]</abbr>'

    return re.sub(r"\[(s\d+)\]", cite, out)


def _chip(concept_id: str, rows: dict) -> str:
    row = rows.get(concept_id)
    if not row:
        return f'<li class="chip missing">{html.escape(concept_id)} <small>(not in map.md)</small></li>'
    needs = ", ".join(row["prerequisites"]) or "nothing"
    status = row["status"]
    return (f'<li class="chip {status}" title="Needs: {html.escape(needs, quote=True)}">'
            f'<span aria-hidden="true">{SHAPES[status]}</span> {html.escape(row["concept"])} '
            f'<span class="status">{status}</span></li>')


def _stage_progress(ids: list[str], rows: dict) -> tuple[int, int]:
    done = sum(1 for i in ids if i in rows and topics.STATUSES.index(rows[i]["status"]) >= topics.READY)
    return done, len(ids)


def _page(name: str, mission: dict, path: dict, rows: dict, sources: dict, is_agreed: bool) -> str:
    counts = {status: 0 for status in topics.STATUSES}
    for row in rows.values():
        counts[row["status"]] += 1
    total = max(len(rows), 1)
    done = sum(counts[s] for s in topics.STATUSES[topics.READY:])
    current = None
    stages_html = []
    for stage in path["stages"]:
        fields = stage["fields"]
        ids = [i.strip(" .;`") for i in fields.get("concepts", "").split(",") if i.strip(" .;`")]
        finished, size = _stage_progress(ids, rows)
        is_current = current is None and finished < size
        current = stage["number"] if is_current else current
        parts = [f'<li class="stage{" current" if is_current else ""}">',
                 f'<h2><span class="num">{stage["number"]}</span> {html.escape(stage["name"])}</h2>',
                 f'<p class="meta">{html.escape(fields.get("time", ""))} · {finished} of {size} concepts practised'
                 f'{" · <strong>you are here</strong>" if is_current else ""}</p>']
        if fields.get("goal"):
            parts.append(f'<p><strong>Goal:</strong> {_inline(fields["goal"], sources)}</p>')
        parts.append('<ul class="chips">' + "".join(_chip(i, rows) for i in ids) + "</ul>")
        if fields.get("read"):
            parts.append(f'<p><strong>Read:</strong> {_inline(fields["read"], sources)}</p>')
        if fields.get("checkpoint"):
            parts.append(f'<p class="checkpoint"><strong>Checkpoint:</strong> {_inline(fields["checkpoint"], sources)}</p>')
        parts.append("</li>")
        stages_html.append("".join(parts))
    legend = "".join(f'<li class="chip {s}"><span aria-hidden="true">{SHAPES[s]}</span> {s} '
                     f'<span class="count">{counts[s]}</span></li>' for s in topics.STATUSES)
    skip = "".join(f"<li>{_inline(item, sources)}</li>" for item in path["skip"])
    ledger_items = "".join(
        f'<li><span class="cite">[{html.escape(i)}]</span> {html.escape(s["title"])} '
        f'({s.get("year") or "n.d."}) <small>{html.escape(s.get("role") or "")} · {html.escape(s.get("kind") or "")}</small></li>'
        for i, s in sources.items())
    banner = ("" if is_agreed else
              '<p class="banner" role="status">Draft roadmap: not agreed yet. Study starts once you say yes.</p>')
    title = path["title"] or name
    depth = (mission.get("Depth") or "").split()[0].rstrip(".") if mission.get("Depth") else ""
    time_match = re.search(r"Total time:\s*([^.\n]+)", path["header"].get("depth", ""))
    total_time = time_match.group(1).strip() if time_match else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Roadmap: {html.escape(title)}</title>
<style>
:root {{ --bg:#fff; --fg:#1b1b1f; --muted:#5d5d66; --card:#f6f6f8; --line:#d9d9e0; --accent:#3557c9;
  --unseen:#e9e9ee; --introduced:#dbe6ff; --practised:#ffe9c7; --recalled-later:#d6f2ec; --can-explain:#d5f0d1; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141418; --fg:#ececf1; --muted:#a3a3ad; --card:#1e1e24;
  --line:#33333c; --accent:#8fa8ff; --unseen:#2a2a31; --introduced:#24324f; --practised:#4a3a1f;
  --recalled-later:#1d3f39; --can-explain:#22401f; }} }}
body {{ font: 16px/1.5 system-ui, sans-serif; background:var(--bg); color:var(--fg); max-width:60rem; margin:0 auto; padding:1.5rem; }}
h1 {{ margin:0 0 .25rem; }} h2 {{ font-size:1.15rem; margin:0; }}
.meta, small, .status, .count {{ color:var(--muted); }}
.banner {{ border:2px dashed var(--accent); padding:.5rem .75rem; border-radius:.5rem; }}
.bar {{ height:.6rem; background:var(--unseen); border-radius:1rem; overflow:hidden; }}
.bar span {{ display:block; height:100%; background:var(--accent); }}
ol.stages {{ list-style:none; padding:0; border-left:3px solid var(--line); margin-left:.75rem; }}
.stage {{ background:var(--card); border-radius:.6rem; padding:.9rem 1rem; margin:0 0 1rem 1.25rem; position:relative; }}
.stage::before {{ content:""; position:absolute; left:-1.95rem; top:1.1rem; width:.9rem; height:.9rem;
  border-radius:50%; background:var(--bg); border:3px solid var(--line); }}
.stage.current {{ outline:2px solid var(--accent); }} .stage.current::before {{ border-color:var(--accent); }}
.num {{ display:inline-block; min-width:1.6rem; text-align:center; border-radius:.4rem; background:var(--accent); color:var(--bg); }}
ul.chips {{ list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:.4rem; }}
.chip {{ border-radius:1rem; padding:.15rem .7rem; border:1px solid var(--line); }}
.chip .status {{ font-size:.8rem; }}
.unseen {{ background:var(--unseen); }} .introduced {{ background:var(--introduced); }}
.practised {{ background:var(--practised); }} .recalled-later {{ background:var(--recalled-later); }}
.can-explain {{ background:var(--can-explain); }} .missing {{ border-style:dashed; }}
.checkpoint {{ border-left:4px solid var(--accent); padding-left:.6rem; }}
a {{ color:var(--accent); }} a:focus, summary:focus {{ outline:3px solid var(--accent); outline-offset:2px; }}
</style></head><body>
<header>
<h1>Roadmap: {html.escape(title)}</h1>
<p>{_inline(mission.get("Goal", ""), sources)}</p>
<p class="meta">Depth: {html.escape(depth)} · {html.escape(total_time)} · {done} of {len(rows)} concepts practised</p>
<div class="bar" role="img" aria-label="{done} of {len(rows)} concepts practised"><span style="width:{100 * done // total}%"></span></div>
{banner}
</header>
<section aria-label="Concept statuses"><ul class="chips">{legend}</ul></section>
<p><strong>Why this order:</strong> {_inline(path["header"].get("order", ""), sources)}</p>
<ol class="stages">{"".join(stages_html)}</ol>
{f'<section><h2>Skip unless</h2><ul>{skip}</ul></section>' if skip else ""}
<details><summary>All sources ({len(sources)})</summary><ul>{ledger_items}</ul></details>
<footer><p class="meta">Generated by <code>puck learn roadmap {html.escape(name)}</code> from path.md, map.md and sources.json.</p></footer>
</body></html>
"""
