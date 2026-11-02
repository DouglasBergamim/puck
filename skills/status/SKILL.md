---
name: status
description: >-
  Report whether Puck is working in this session. Use when asked about Puck's
  status or setup. Not for project or git status.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-1"
  last_evaluated: "never"
---
## Procedure
1. Run `puck status`.
2. Report the home folder, the hosts and any error.

## Output
Two or three lines, quoting the command output.

## Done when
- [ ] The answer quotes real output from `puck status`.

## If something fails
If `puck` isn't found, say so and don't guess at its state.

## Host differences
Read references/host-tools.md if a named capability is unclear.
