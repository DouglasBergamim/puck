# Retro: 2026-11-03-add-git-hooks-that-keep-the

Outcome: done (all 8 steps pass and the review's findings are resolved; the task is still open and the work is uncommitted)

## Findings

| Type | Finding | Landed in |
|---|---|---|
| procedure | promote's commit carries all of `docs/features.md`. With the features-coverage lint in pre-commit, a row for an uncommitted agent, or any other uncommitted edit the snapshot can't satisfy, gets the promote commit refused. So commit new agents first. Source: findings.md; review.md finding 1 (reproduced). promote now rolls back cleanly when the commit is refused. | Constructor: already updated in this task (`context/agents/constructor.md`, Write and Activate stages), so not drafted again. The task skill's step 9 also runs promote for retro-drafted skills, but it doesn't say to add the row or to commit other features.md edits first. Draft for the user: `scratch/drafts/task.diff` |
| one-off | A `git worktree` from HEAD can't smoke-test uncommitted hooks, because it has neither `.githooks/` nor the new lint code. `hooks-smoke.sh` copies the working tree into a fresh repo instead. Source: findings.md. | Here only; it applies to this task's smoke test, not to a repeatable procedure |
| one-off | `install` read only `--local core.hooksPath`, so it silently overrode a global hooksPath (for example a secret scanner). Source: review.md finding 2. | Fixed in `src/core/primitives/install.py`, with test `test_install_leaves_a_global_hooks_path_alone` |
| one-off | `git checkout-index -a --prefix` honours `GIT_INDEX_FILE`, so the pre-commit snapshot is right for partial commits (`git commit -- paths`) and for staged deletions. Source: review.md, snapshot correctness. | Here only. No topic matches (`puck topic list` shows only game-theory-for-finance, and `context/knowledge/` is empty) |
| one-off | pre-push runs the tests on the working tree, not on the commits being pushed, so an unstaged fix can let broken commits through. Accepted as specified. Source: review.md finding 6. | Here only; it was noted for the user |
| one-off | Smaller review fixes: the hook's failure line now warns against `--no-verify`, a `tool_used` grader needs `input_match`, `puck agent new` mentions the features row, and a rolled-back promote mentions its row. Source: review.md findings 3-5. | Fixed in code, with tests |

## What failed

`scratch/LOG.md` is empty. From findings.md and review.md:
- The SPEC's step 6 called for a throwaway `git worktree` for the smoke test. That fails for uncommitted hooks and lint code, so the test copies the working tree instead.
- The first version of promote crashed with a raw `CalledProcessError` when the pre-commit hook refused its commit. It left the skill at `status: active` and staged, with nothing committed. The fix was rollback plus a `PuckError`.
