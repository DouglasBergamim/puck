---
name: field-map
description: >-
  Brainstorm the map of a field: subfields, core concepts, key questions, open
  debates, vocabulary and which ideas depend on which. Use when the user asks what
  a subject consists of, where to start, or before searching for papers on an
  unfamiliar area. Not for finding sources (use literature) or for teaching a
  concept (use teach).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
---
## Procedure
1. Read the topic's `mission.md`. If there is no topic, use the `scope` skill first, or ask the user for the topic and depth.
2. Draft the map from what you know, sized to the depth: about 8-15 concepts for `orient`, 15-30 for `use` or `master`.
   - Group concepts into 2-5 subfields.
   - Draw prerequisite edges only where one idea can't be understood without the other.
   - List open questions and debates, with who holds which view.
   - Mark anything you're unsure of with `?`, so the search can settle it.
3. Write `map.md` from `$PUCK_HOME/context/templates/map.md`: the Mermaid graph, the concept table in teaching order with every status `unseen` unless the probe set it, and the debates. Remove the `<!-- template -->` line. Ids are lowercase words joined by hyphens.
4. Show the user the graph and the subfields, and ask what to cut, add or merge. Apply their changes.
5. Run `puck learn next <topic>` to confirm the table parses and the first concept has no unmet prerequisites.

## Output
`map.md`: a concept graph, a concept table in teaching order, and the debates.

## Done when
- [ ] `puck topic check <topic> --has map` passes.
- [ ] Every prerequisite id exists in the table, and no concept depends on a later one.
- [ ] The user reviewed the map.

## If something fails
If the field is too unfamiliar to map from memory, map only what you're sure of, mark the rest `?`, and let `literature` fill it from surveys. Next step: `literature`.

## Host differences
Read references/host-tools.md if a named capability is unclear.
