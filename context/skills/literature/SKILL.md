---
name: literature
description: >-
  Find, record and verify the main papers, books and surveys on a topic: anchors,
  the canon they cite, the frontier that builds on them, and the critics. Use when
  the user asks for key papers, books, references or a literature review on a
  subject. Not for summarising one paper the user already has (use kb) or for
  ordering what to read (use reading-path).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell, subagents, web"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Subtopic split and stop limits from tavily-ai/skills; ledger ids and exact-quote gate from NousResearch hermes-agent grounded-citations"
---
## Procedure
1. Read `mission.md` and `map.md`. Without an approved mission, use `scope` first: never search for a subject the user only named. Without a map, use `field-map` first, or proceed from the mission and say the split is rough.
2. Split the search into 3-5 subtopics, one per distinct question the map raises. Add one subtopic for criticism: failures, failed replications and competing schools.
3. Spawn one `source-finder` agent per subtopic, in parallel. Give each: the topic id, its subtopic, the mission's goal and depth in one or two lines, and a limit of about 12 searches. Don't pass your own conclusions.
4. Read their returns. Rerun a source-finder only for a subtopic it marked `partial` or `blocked`, once.
5. Run `puck topic check <topic>`. Fix or remove each failing source with the source-finder's evidence; never edit a quote to make it match.
6. Write one short wiki page per anchor or canon source, and one per core concept the sources explain, in the topic's `wiki/` folder. Every paragraph and list item cites ledger ids like `[s3]`. Mark your own connecting text `[not in sources]`. Copy numbers and quotes exactly from `raw/`.
7. Spawn the `claim-checker` agent with the wiki pages and the matching `raw/` files. Remove or fix every claim it rates unsupported, and soften partial ones.
8. Run `puck topic check <topic>` until it passes.
9. Tell the user what was found per role, in a short list, and what is still thin.

## Output
A verified `sources.json`, evidence in `raw/`, and wiki pages that pass lint. `references/source-roles.md` defines the roles.

## Done when
- [ ] `puck topic check <topic>` passes.
- [ ] Every source has a role, and the critique subtopic was searched.

## If something fails
If a provider is rate-limited, continue with the others and say which one was missing. If a source's text is only in a PDF, read it and save the passage with `puck sources fetch --file`; verify will mark it as weaker evidence. Next step: `reading-path`.

## Host differences
Read references/host-tools.md if a named capability is unclear. Without subagents, run each subtopic yourself in turn, following the source-finder agent doc, and do the claim check last with fresh eyes.
