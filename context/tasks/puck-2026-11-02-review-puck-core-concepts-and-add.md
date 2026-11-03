# Retro: 2026-11-02-review-puck-core-concepts-and-add

Outcome: done

All 8 steps pass (evidence in scratch/outputs/check-s1..s8.txt). The work is committed in 44ba12b, 0879ffd and 112eb6e. The review (scratch/outputs/review.md) raised 7 findings and the main session fixed all of them. The task itself is still open.

## Findings

| Type | Finding | Landed in |
|---|---|---|
| one-off | The task pack ranks by raw keyword substring hits (`_score` in src/core/tools/work/pack.py). A goal that contains "concepts" or "skills" pulls in every learning skill and misses task, plan and review. Pack relevance needs better scoring than keyword counts. Source: findings.md, SPEC finding 12. | Here. A follow-up build task for the user. Still present at HEAD. |
| procedure | Lint treats any backticked host tool name as an error. Copilot's subagent tool is `task`, so skill and agent text has to say "the task skill" in plain words. Source: findings.md. | Draft: scratch/drafts/constructor.diff (Rules line in context/agents/constructor.md). Linted on a scratch copy with the diff applied. |
| procedure | `claude plugin eval` sandboxes start in an empty working directory unless a case has a scaffold_script and the run passes `--scaffold`. `puck skill promote` doesn't pass it. Result graders for skills that read a repo (onboard, commit) have to accept correct behaviour in an empty workspace too. Source: findings.md. | Draft: scratch/drafts/constructor.diff (Write stage). |
| one-off | `skills.set_status` bumps the version on every status change. A promote whose evals fail rolls the status back to draft but leaves the version two higher. The version should bump only when a promote succeeds. Source: findings.md, confirmed in src/core/primitives/skills.py. | Here. A follow-up code fix. |
| one-off | `promote` runs the evals but never writes `metadata.last_evaluated`. Every skill still says `never`, including commit and onboard, which passed. Source: findings.md, confirmed in skills.py. | Here. A follow-up code fix, best done together with the version fix. |
| procedure (already fixed) | Step 7 of the commit skill used `git commit -- <paths>`, which commits the working-tree version and undoes a hand-built partial index. Source: findings.md. | Already in context/skills/commit/SKILL.md step 7 (commit 112eb6e). Nothing to draft. |

The two drafted procedure findings go into the constructor lead, the procedure that writes skills, agents and evals. A new skill would duplicate it. The retro worker also drafts skills with evals, so the user may want the same two notes in docs/concepts.md ("Defining a skill / Evals"). That file is a project doc, so it isn't drafted here.

No topic findings. `puck topic list` is empty, and context/knowledge/ is gitignored.

## What failed

scratch/LOG.md is empty, so the session logged no failed approaches. From the review: the first implementation shipped 2 medium and 5 low defects, all fixed before commit. The two medium ones were:
- promote linted the draft before activating it, so it skipped the active-only eval gate.
- `--topic` used `safe_id` instead of the topic slug, so free-text topic names failed.

A lesson for later builds: when a gate depends on status, check it against the target status.
