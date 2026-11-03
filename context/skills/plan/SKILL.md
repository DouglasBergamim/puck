---
name: plan
description: >-
  Interview the user and turn an undecided goal into a one-page SPEC.md. Use when
  the user hasn't settled what to build or how, or asks for help planning or
  designing a system, even before any task exists. Not for small, clear changes.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-2"
  last_evaluated: "never"
---
## Procedure
1. If no task is open here (`puck task show` says so), start one with `puck task start "<goal>" --type plan`, so SPEC.md has a folder. Read the relevant code or notes first, so you only ask what you can't find out yourself.
2. Interview the user on decisions that would change the build, with the ask capability: a few questions at a time, each with two to four options and your recommendation first.
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
