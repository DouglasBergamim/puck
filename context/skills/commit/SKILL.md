---
name: commit
description: 'Turn the working tree''s changes into well-formed commits: see what
  changed, group it into logical commits, write messages in the project''s style,
  and commit only what belongs. Use when the user asks to commit, make a commit, or
  commit and push. Not for reviewing a change (use review) or for deciding what to
  build (use plan).'
metadata:
  version: '2'
  status: active
  invocation: model
  requires: shell, ask
  origin: 2026-11-02-review-puck-core-concepts-and-add
  last_evaluated: never
---
## Procedure
Commit only because the user asked. Asking to build something is not asking to commit it.

1. **Read the state.** Run `git status`, `git diff --staged` and `git diff`, and `git log -n 8` to see the project's message style. Read the project's `AGENTS.md` (or its equivalent) for rules on branches, remotes, messages and what must never be committed.
2. **Branch if needed.** If you're on the default branch and the project or the user says work goes on branches, create one first, named for the change.
3. **Choose what belongs.** Sort every changed file into: part of this change, unrelated, or must never be committed (secrets, `.env` files, keys, build output, large binaries, personal data the project excludes). Files the user already staged count as theirs: don't unstage them without asking. When a file's place is unclear, ask with the ask capability, one decision per question.
4. **Group.** One commit per logical change, so each one could be reverted on its own. Stage by explicit path, never everything at once.
5. **Check before committing.** If a task is open, run `puck task show` and say which checks don't pass yet. Run the project's fast test or lint command if `AGENTS.md` names one. A failing check doesn't block a commit the user asked for, but say so in your reply.
6. **Write the message.** Subject in the imperative, at most 72 characters, in the style the log shows. Body: why the change was made, and anything a reviewer must know. End with the attribution lines your host gives for commits, if it gives any.
7. **Commit only what you chose.** For whole files, `git commit -m "<message>" -- <paths>` keeps anything else staged out. When you staged only part of a file, check `git diff --cached` and use a plain `git commit`, because a path argument commits the working-tree version of each path and undoes the split. If a pre-commit hook fails, fix the cause and make a new commit. Never bypass hooks, never amend a commit that's already pushed, never force-push.
8. **Push only when asked**, and only to a remote the project's rules allow.
9. **Report.** Show `git log --oneline -n <commits made>` and `git status --short`, and list what you deliberately left out.

## Output
One or more commits holding exactly the intended change, and a short report of what was committed and what was left out.

## Done when
- [ ] `git log` shows each new commit, with a message in the project's style.
- [ ] No secret, build output or unrelated file is in a new commit.
- [ ] Anything the user had staged that wasn't part of the change is still staged and uncommitted.

## If something fails
If a hook keeps failing, stop after two fixes and show the user the hook's output. If the working tree has nothing to commit, say so and stop. If the change mixes unrelated work you can't separate by file, ask whether to commit it together or to split it by hunk.

## Host differences
Read references/host-tools.md if a named capability is unclear.
