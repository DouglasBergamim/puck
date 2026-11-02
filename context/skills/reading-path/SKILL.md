---
name: reading-path
description: >-
  Turn a topic's verified sources and concept map into an ordered reading path:
  stages with exact chapters or sections, why, time and a checkpoint question. Use
  when the user asks what to read, in what order, or for a study plan or syllabus
  for a subject. Not for finding sources (use literature) or for a study session
  (use teach).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Read `mission.md`, `map.md`, `puck sources list <topic>` and the wiki index. If sources aren't verified yet, run `puck sources verify <topic>` and fix that first, or use `literature`.
2. Group the concept table into 3-7 stages, in prerequisite order. A stage is something the user can finish in one to three sittings.
3. For each stage, pick the fewest sources that cover its concepts, preferring anchors and textbooks early and canon and frontier later. Name exact chapters, sections or pages. If you can't name them from `raw/` or the wiki, say "skim the abstract and introduction" rather than inventing chapter numbers.
4. Let depth decide the reach: `orient` stops at anchors and textbooks, `use` adds canon and practical, `master` adds frontier and critique.
5. Write `path.md` from `$PUCK_HOME/context/templates/path.md`: per stage a goal, concept ids, sources by ledger id with why, time, and one checkpoint question answerable without notes. Add a "Skip unless" list for sources left out, and a Mermaid diagram of the stages.
6. Reorder the concept table in `map.md` to match the stages, keeping statuses.
7. Show the user the stages and total time, and adjust to their budget.

## Output
`path.md`, and a concept table in the same order.

## Done when
- [ ] `puck topic check <topic> --has path,map,sources` passes.
- [ ] Every source on the path is a ledger id, and every concept is in some stage.
- [ ] The total time fits the mission, or the user accepted the overrun.

## If something fails
If a stage has no good source, say so in the path and suggest a narrower `literature` search for it. Next step: `teach`.

## Host differences
Read references/host-tools.md if a named capability is unclear.
