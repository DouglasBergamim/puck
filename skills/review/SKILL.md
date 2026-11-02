---
name: review
description: >-
  Review a change against its SPEC.md and report defects with evidence. Use when
  a non-trivial change is ready. Not for style, planning or trivial edits.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "subagents"
  origin: "milestone-2"
  last_evaluated: "never"
---
## Procedure
1. Find the SPEC.md path, the diff range and the task folder.
2. Spawn the `reviewer` agent with those three inputs. Don't pass your own reasoning, so its view stays independent.
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
