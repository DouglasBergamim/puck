---
name: review
description: >-
  Review a code change for defects and report them with evidence, judged against
  its SPEC.md or stated requirement. Use when asked to review a change or diff,
  when asked if it's ready to merge, and before closing non-trivial work. Not for
  style opinions or planning.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "subagents"
  origin: "milestone-2"
  last_evaluated: "never"
---
## Procedure
1. Find the change, the requirement it must meet (SPEC.md if there is one, otherwise what the user stated) and any task folder.
2. Spawn the `reviewer` agent with those inputs. Don't pass your own reasoning, so its view stays independent.
3. Read its findings. Fix real defects, and record any you reject with a reason.
4. Rerun the task's checks after any fix.

## Output
Fixed defects, plus the reasons for any rejected finding.

## Done when
- [ ] Every finding was fixed or rejected with a reason.
- [ ] Checks were rerun after the last fix.

## If something fails
Without subagents, start a fresh session for the review if you can. Otherwise follow the reviewer agent doc yourself and say that the review wasn't independent.

## Host differences
Read references/host-tools.md if a named capability is unclear.
