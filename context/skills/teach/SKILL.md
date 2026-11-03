---
name: teach
description: >-
  Run an interactive study session on a topic: recall last time, pick the next
  concept, have the user attempt it before explaining, check understanding, and
  record what happened. Use when the user wants to study, learn, practise or
  continue a topic, or asks to be taught something step by step. Not for a quick
  factual answer or for building a reading list.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Stop-after-question and no-unearned-credit rules adapted from DrCatHicks/learning-opportunities (CC-BY-4.0); recall-first gate and hint ladder ideas from GarethManning/education-agent-skills; learner records idea from mattpocock/skills teach"
---
## Procedure
Study sessions don't open a task: the topic folder holds the state.

1. **Orient.** Run `puck learn status <topic>`. No topic or no mission: use `scope` first. No `path.md` or map: use `curriculum`, then `roadmap`. If `puck learn status` says the roadmap isn't agreed, follow `roadmap`'s show-and-agree steps first: teaching starts only after the user's yes. Read `path.md`, and the profile's `friction` setting (`guided` by default).
2. **Recall**, unless this is the first session. On the first session, read the mission's Background instead: the attempt in step 4 shows the user's real level, and a concept they already know can be marked `introduced` and passed. Otherwise ask the user to rate their confidence (0-100) on the last session's concepts, then to write what they remember without help. Then give a gap map: accurate, missing, misconceived. Don't teach yet.
3. **Choose.** Run `puck learn next <topic>`. Tell the user the concept and why it comes now. A recall gap from step 2 can come first.
4. **Attempt first.** Before explaining, ask one question that makes the user predict, guess or try: "What do you think happens if…?", "How would you…?". First exposure to something entirely new is exempt: give a short orientation, then ask.
5. **Explain** from the topic's wiki and sources, citing ledger ids, and point to the stage's reading in `path.md`. Mark anything not from them `[not in sources]`. Build on the user's attempt, including what was right in it. Use `visualize` when the idea is a structure, a process over time, a parameter that changes something, or a space.
6. **Check.** Ask the user to explain it back or apply it to a new case. Use `practice` for a graded exercise.
7. **Update.** A concept becomes `introduced` once explained, and `practised` only after a correct attempt on a new case. Never mark more than one status step from one answer.
8. **Close.** Write the record from `$PUCK_HOME/context/templates/session.md` and run `puck learn record <topic> --file <record> --status <id>=<status>`. Refresh the progress view with `puck learn roadmap <topic> --no-open`. Tell the user what's next.

## Rules
- End your message right after any question. No hints, options or "for example" after it.
- One question per message.
- Recall, attempts and checks are open questions in plain text. Never turn them into options with the ask capability: picking from a list gives the answer away. Use it only for choices, such as what to do next.
- Never give credit for insight the user didn't express. "Close" is not "right".
- Hint ladder, one rung per request: a question about what they tried, a pointer to the relevant idea, a worked analogous case, then a partial solution. `socratic` friction climbs slower; `guided` may start at rung two.
- If the user asks for the answer outright, give it, then ask them to apply it.

## Output
A session the user worked through, and a record in `sessions/` with updated statuses.

## Done when
- [ ] `puck learn record` ran and printed the new record's path.
- [ ] Every status change came from an attempt in this session.

## If something fails
If the wiki doesn't cover the concept, teach it marked `[not in sources]` and send the user to the stage's reading in `path.md`. If the user brings that reading, file it with `kb`.

## Host differences
Read references/host-tools.md if a named capability is unclear.
