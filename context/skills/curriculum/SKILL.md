---
name: curriculum
description: >-
  Find how a subject is taught and what people recommend for learning it: the
  standard textbooks and their core chapters, university courses and syllabi,
  reading lists and discussions, docs and well-known articles for tech subjects,
  and the classic works of where it's applied. Use when the user wants to learn a
  subject and needs the books and courses to learn it from. Not for surveying the
  research on a question (use literature) or ordering what to read (use roadmap).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell, subagents, web"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Read `mission.md`. Without a learning mission (one with a Subject), use `scope` first.
2. Write one brief per source-finder:
   - **Core:** "How is <Subject> taught? The standard textbooks and their core chapters, university courses and syllabi, and what reading lists and discussions recommend to learners." For a tech subject, add "the official docs and the articles practitioners point to".
   - **Application**, if the mission has Applied to: "<Subject> in <Applied to>: the books, classic papers and articles that courses and practitioners in <Applied to> recommend, for this goal: <Goal>."
3. Spawn one `source-finder` per brief, in parallel. Give each: the topic id, its brief, the mission's subject, application, goal and depth in two lines, a limit of about 12 searches and at most 6 sources. There is no criticism brief: a learner needs the consensus first.
4. Wait until every source-finder is back, saying nothing in between, then read their returns. Rerun a source-finder only for a brief it marked `partial` or `blocked`, once.
5. Run `puck topic check <topic> --has mission,sources`. Fix or remove each failing source with the source-finder's evidence; never edit a quote to make it match.
6. Check the coverage: at least two `textbook` sources (books or courses) for the subject, and at least one `recommendation` behind them. If either is missing, start one more source-finder on that gap.
7. Tell the user, in a short list: the textbooks and courses, the application's classics, and who recommends them.

## Output
A verified `sources.json` of 8-15 sources, mostly textbooks, courses and recommendations, with evidence in `raw/`. No wiki pages: the professor writes those as teaching reaches each stage. `$PUCK_HOME/context/skills/literature/references/source-roles.md` defines the roles.

## Done when
- [ ] `puck topic check <topic> --has mission,sources` passes.
- [ ] The ledger has at least two `textbook` sources for the subject and one `recommendation`.

## If something fails
If no syllabus or discussion can be read, fall back to `puck sources search "<subject>" --kind book` and the textbooks the anchors cite, and say the order rests on less evidence. Next step: `roadmap`.

## Host differences
Read references/host-tools.md if a named capability is unclear. Without subagents, run each brief yourself in turn, following the source-finder agent doc.
