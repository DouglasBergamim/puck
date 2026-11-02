---
name: plan
description: >-
  Turn a vague goal into a one-page SPEC.md by interviewing the user. Use before
  building something with open design decisions. Not for small, clear changes.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-2"
  last_evaluated: "never"
---
## Procedure
1. Read the relevant code or notes first, so you only ask what you can't find out yourself.
2. Interview the user, a few questions at a time, on decisions that would change the build. Give a recommendation with each question.
3. Write SPEC.md in the task folder: goal, decisions with reasons, non-goals, and acceptance checks.
4. Make every acceptance check a command or an observable result.
5. Keep it to one page. Leave out line-level steps, because they go stale.
6. If the work is large, suggest continuing in a fresh session from SPEC.md.

## Output
A SPEC.md that a fresh session could build from.

## Done when
- [ ] Every decision has a reason.
- [ ] Non-goals are listed.
- [ ] Each acceptance check can be run or observed.

## If something fails
If the user can't decide, record your recommendation as a provisional decision and mark it clearly.

## Host differences
Read references/host-tools.md if a named capability is unclear.
