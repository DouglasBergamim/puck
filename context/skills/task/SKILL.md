---
name: task
description: >-
  Carry non-trivial work from start to a verified close. Use for building or
  fixing code, and for a full research run on a topic. Not for quick questions,
  one-line fixes or study sessions (use teach).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell, subagents"
  origin: "milestone-2"
  last_evaluated: "never"
---
## Procedure
You own every step, including the retro. Don't ask the user to run it.

1. **Start.** Run `puck task start "<goal>" --type build|learn|research|plan`. Add `--worktree` when other work may touch the same repository, then continue from the worktree it prints. Keep the task ID and pass `--task <id>` to later commands.
2. **Load context.** Read only what the task pack points to and what the work needs.
3. **Write the plan.** Fill in SPEC.md in the task folder. For anything unclear or design-heavy, use the `plan` skill. Add each thing to do as a step with `puck task step "<what>" --check "<command>"`. `puck task show` lists what's done and what isn't. For learning or research, the check can test that the output exists and is complete.
4. **Work.** Run `puck note "<finding>" --type procedure|topic|project|rule|one-off` as soon as you learn something non-obvious, including approaches that failed.
5. **Experiment in scratch.** For anything uncertain, run `puck scratch new "<name>"` and work in that folder. State a hypothesis and how you'll measure it, run it, then record it with `puck scratch log`. After three failed attempts on one problem, stop and rethink or ask the user. Real code never imports from scratch.
6. **Verify.** Run `puck task check <step>` for every step. For non-trivial changes, use the `review` skill. Fix what fails and check again.
7. **Retro.** If `findings.md` has entries or `scratch/LOG.md` shows failed attempts, spawn the `retro` agent with the task folder. If there are no findings, skip this step.
8. **Close.** Run `puck task close --outcome done|partial|abandoned`.
9. **Report.** Tell the user the outcome with evidence. If the retro raised proposals, list them in one short list, and apply each answer with `puck proposal approve <id>` or `puck proposal reject <id>`.

## Output
A closed task, the requested work, and at most one short list of proposals.

## Done when
- [ ] Every acceptance check ran through `puck task check`.
- [ ] Non-obvious findings were noted, or there were none.
- [ ] The task is closed, and proposals were shown to the user.

## If something fails
If a check can't pass, close with `--outcome partial` and say what's missing. Never edit a check just to make it pass. If the session ends early, the task stays open and `puck task list` shows it.

## Host differences
Read references/host-tools.md if a named capability is unclear. Without subagents, do the retro and review steps yourself, following their agent docs.
