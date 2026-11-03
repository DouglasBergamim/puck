---
name: kb
description: >-
  Add a source the user gives you to a topic's notes, or answer from those notes
  with citations. Use when the user shares a paper, chapter, article or link to
  file under a topic, or asks what their notes say about something. Not for
  searching for new sources (use curriculum for a subject to learn, literature for a research question).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Grounding invariant and ingest triage from Astro-Han/karpathy-llm-wiki"
---
## Procedure
**Add a source:**
1. Find the topic with `puck topic list`. Create one with `puck topic new` only if the user agrees.
2. Record it: `puck sources add <topic> <ref>` for a paper or book (find the ref with `puck sources search`), or `--url <url> --title "<title>"` for a page. Give a `--role` and a `--why`.
3. Save its text: `puck sources fetch <topic> <id>`. For a PDF or text the user pasted, save the passages you use with `puck sources fetch <topic> <id> --file <file> --origin "<where>"`.
4. Triage against the existing wiki, per claim: new, updates a page, disputes a page, or adds nothing. Write or edit pages accordingly, citing `[sN]`. Never delete a disputed claim: add the new view beside it with both citations, and a `Disputed:` line.
5. Run `puck topic check <topic>` until it passes.

**Answer from the notes:**
1. Read the topic's `wiki/index.md`, then only the pages that match.
2. Answer with the pages' citations. Say plainly what the notes don't cover, rather than filling the gap from memory.

## Output
A ledger entry, its evidence in `raw/`, and wiki pages that pass lint; or an answer citing the notes.

## Done when
- [ ] `puck topic check <topic>` passes after any change.
- [ ] Every number and quote in a changed page appears in `raw/`.

## If something fails
If lint flags a number or quote, correct it from `raw/`; never change `raw/` to match the page.

## Host differences
Read references/host-tools.md if a named capability is unclear.
