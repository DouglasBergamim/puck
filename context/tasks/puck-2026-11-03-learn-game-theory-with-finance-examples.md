# Retro: 2026-11-03-learn-game-theory-with-finance-examples

Outcome: done

The professor workflow ran for topic `game-theory-for-finance` (scope, curriculum, roadmap). `puck topic check` passed at every stage (scratch/outputs/check-s1..s3.txt).

## Findings

| Type | Finding | Landed in |
|---|---|---|
| procedure | Running `puck sources add --url ... --quote` creates a new ledger entry instead of attaching the quote to the existing source. When several source-finders ran in parallel, this left duplicates (s2, s5, s18). Root cause: `keys()` in `src/core/tools/learning/sources/record.py` ignores `url`. Web records have no DOI or refs, so matching depends on title plus year, and that misses whenever the second call's title or year differs (findings.md, lead's report). | Draft for the user: `scratch/drafts/record-keys.diff` (code: key on normalised URL) and `scratch/drafts/source-finder.diff` (agent step 5: repeat the exact url/title/year and confirm the id). Neither is applied. |
| procedure | No CLI can remove or merge ledger entries, so the lead edited `sources.json` by hand. That skips `store.py` locking and the ledger checks. | Follow-up for the user: add `puck sources remove/merge <topic> <id>`. This is noted in `record-keys.diff` and is a code change, not a skill. |
| one-off | A source-finder recorded an off-topic entry (s13) from a wrong DOI. The lead removed it by hand. | Here only. If it happens again, step 4 of source-finder could require checking that the resolved title matches before adding. |
| one-off | Open Library, Semantic Scholar and some SSL hosts could not be reached during the run, which limited book lookups and fetches. | Here only (environment/network). |

No topic page was added. These findings are about Puck's tooling, not game theory, so they don't belong in the `game-theory-for-finance` wiki.

## What failed

- `scratch/LOG.md` is empty, so failed approaches come from the lead's report only.
- Parallel source-finders attaching quotes through `--url` produced duplicate ledger entries. The lead cleaned them up by editing `sources.json` by hand.
- Resolving one DOI returned an unrelated work (s13), and it was added without anyone checking the title.
- Fetches to Open Library, Semantic Scholar and some SSL hosts failed.
