---
name: report
description: >-
  Answer a research topic's question from its checked wiki: a cited report of
  what's settled, what's disputed and by whom, what's open, and what to read
  first. Use when a research topic's sources and wiki are verified and the user
  wants the answer, or asks what the literature concludes. Not for finding
  sources (use literature) or for a learning roadmap (use roadmap).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Read `mission.md`, `map.md`, the wiki's `index.md` and the pages it lists, and `puck sources list <topic>`. If `puck topic check <topic>` fails, use `literature` to fix it first.
2. Answer the mission's Question in a few paragraphs, at its Depth, for the reader its Background describes. Lead with the answer, then the evidence.
3. Sort the claims: **settled** (sources agree), **disputed** (name who holds which view, with citations on each side) and **open** (nobody has settled it). A claim backed only by sources in one independence group counts once.
4. Pick 3-5 sources to read first, each with why and which part.
5. Write `report.md` from `$PUCK_HOME/context/templates/report.md`. Every claim cites ledger ids like `[s3]` taken from the wiki pages; mark your own connecting text `[not in sources]`. Copy numbers and quotes exactly from `raw/`. Remove the `<!-- template -->` line.
6. Run `puck topic check <topic> --has mission,map,sources,report`.
7. Show the user the answer in a few lines and point to `report.md`.

## Output
`report.md`: the answer, what's settled, disputed and open, and what to read first.

## Done when
- [ ] `puck topic check <topic> --has mission,map,sources,report` passes.
- [ ] Every claim in the report cites a ledger id or is marked `[not in sources]`.

## If something fails
If the wiki can't answer the question, say what's missing in Open and suggest a narrower `literature` search for it rather than filling the gap from memory.

## Host differences
Read references/host-tools.md if a named capability is unclear.
