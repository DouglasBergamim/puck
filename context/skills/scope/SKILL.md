---
name: scope
description: >-
  Pin down what the user wants to learn or research: the question, why, how deep,
  time, and what they already know, then probe their real level. Use when the user
  says they want to learn, study or research a subject, or a topic has no mission
  yet. Not for planning software (use plan) or for a quick factual question.
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Bracketed probe idea from amosblomqvist/learn; mission file idea from mattpocock/skills teach"
---
## Procedure
1. Run `puck topic list`. If the topic exists, run `puck learn status <topic>` and read its `mission.md`; only fill gaps. Otherwise run `puck topic new "<name>"`.
2. For a full research run, start a task first: `puck task start "Research <topic>" --type research`, then follow the task skill around this chain.
3. Interview the user, at most two questions per message, each with your recommended answer so "yes" is enough:
   - the question they want answered, or what they want to be able to do;
   - why, because that decides what to leave out;
   - depth: `orient` (know the map), `use` (apply it) or `master` (derive it and build on it);
   - time per week and any deadline;
   - what they already know, in their words.
4. Write `mission.md` from the answers. Remove the `<!-- template -->` line. Record anything still undecided as a provisional choice, marked as such.
5. If the user wants to learn the topic (not only a reading list), run the probe in `references/probe.md` and add what it found under Background.
6. Run `puck topic check <topic> --has mission`.

## Output
A filled `mission.md`, and when probed, the user's level per strand.

## Done when
- [ ] `puck topic check <topic> --has mission` passes.
- [ ] Depth is one of orient, use or master.
- [ ] The user confirmed the mission, or it is marked provisional.

## If something fails
If the user can't say how deep, recommend `orient` and say they can deepen later. Next step: `field-map`, unless the user only wanted the mission.

## Host differences
Read references/host-tools.md if a named capability is unclear.
