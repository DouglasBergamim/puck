---
name: roadmap
description: >-
  Turn a learning topic's verified textbooks, courses and recommendations into a
  roadmap: 3-7 stages from the subject's foundations out to where it's applied,
  each with exact chapters or lectures, time and a checkpoint question, plus the
  concept table the study sessions follow. Use when the user asks what to read
  and in what order, or for a study plan or syllabus for a subject. Not for finding
  sources (use curriculum) or for a study session (use teach).
metadata:
  version: "2"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Read `mission.md` and `puck sources list <topic>`, then the `raw/` text of the `recommendation` and `textbook` sources. If the sources aren't verified, run `puck topic check <topic>` and fix that first; if there are none, use `curriculum`.
2. **Find the order.** Note where the syllabi and textbooks agree on what comes before what. Where they disagree, follow the most recommended textbook and say so.
3. **Stage it.** Group the material into 3-7 stages, from the subject's foundations out to the application. A stage is something the user can finish in one to three sittings. The last stage reaches the mission's Goal.
4. **Fill each stage**: a goal, its concepts, and what to read or watch: textbook chapters or course lectures first, then at most one paper or article. Name exact chapters, sections or lectures only when `raw/` or a syllabus shows them; otherwise say "the chapter on <topic>" rather than inventing numbers. Add a time estimate and one checkpoint question answerable without notes. The last checkpoint is the Goal itself.
5. Let depth decide the reach: `orient` stays with textbooks and courses and gives the application one overview stage; `use` adds the application's classics and practical sources; `master` adds primary papers and graduate texts.
6. Write `path.md` from `$PUCK_HOME/context/templates/path.md`, with the Order line citing the sources the order rests on, a "Skip unless" list for sources left out, and a Mermaid diagram of the stages.
7. Write the concept table in `map.md` from `$PUCK_HOME/context/templates/map.md`: concepts in stage order, ids as lowercase words joined by hyphens, and as prerequisites the earlier concepts each one needs. Statuses start `unseen`; keep any status an existing table already has. Remove the `<!-- template -->` line.
8. **Show it.** Run `puck learn roadmap <topic>`. It checks that `path.md` and the table parse, writes `visuals/roadmap.html` and opens it in the browser. In the conversation, list only the stages with their times, in a few lines, and say the page has the readings and checkpoints. Never paste Mermaid into the conversation: a terminal shows it as raw text.
9. **Agree it.** With the ask capability, ask one question: "Agree and start stage 1", or "Change something". Apply each change to `path.md` and `map.md` (run `curriculum` again only for a missing source), rerun `puck learn roadmap <topic>`, and ask again. If the mission names a deadline, fit the path to it.
10. On the user's yes, set `Agreed: <today, YYYY-MM-DD>` in `path.md`. Until then `puck learn next` refuses, so no study session can start.

## Output
`path.md` agreed by the user, `map.md` with a concept table in the same order, and the roadmap page `visuals/roadmap.html`.

## Done when
- [ ] `puck topic check <topic> --has mission,sources,path,map` passes.
- [ ] Every source on the path is a ledger id, every concept is in some stage, and the last checkpoint tests the mission's Goal.
- [ ] The user saw the roadmap page and said yes, and `path.md` says `Agreed:` with the date.

## If something fails
If a stage has no good source, say so in the path and run `curriculum` again for that stage only. Next step: `teach`.

## Host differences
Read references/host-tools.md if a named capability is unclear.
