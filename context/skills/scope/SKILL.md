---
name: scope
description: >-
  Write a topic's mission: for learning, the subject, what it's applied to, the
  goal and the depth; for research, the question, why, the areas and the depth.
  Use when the user says they want to learn, study or research something, or a
  topic has no mission yet. Not for planning software (use plan) or for a quick
  factual question.
metadata:
  version: "4"
  status: active
  invocation: model
  requires: "shell"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Mission file idea from mattpocock/skills teach"
---
## Procedure
1. **Kind.** `learn` when the user wants to learn or study a subject; `research` when they want to know what's known about a question. The lead that loaded you says which; otherwise take it from the request, and don't ask.
2. **Topic.** Run `puck topic list`. If the user named no subject, or one close to an existing topic, ask whether to continue that topic or start a new one. To continue, read its `mission.md` and only fill gaps. Otherwise run `puck topic new "<name>" --kind <kind>`.
3. **Draft first.** Fill every section of the new `mission.md` from what the user already said; its comments say what each section holds and which later step reads it. Everything the user said counts as answered.
   - In "X applied to Y" or "X for Y", the subject is usually X, taught from its foundations, and Y is where it's applied. Never shrink the subject to the part Y uses, and never put its foundations out of scope.
   - The Goal is something the user could be asked to do at the end: "By the end I can …".
4. **Ask once.** In one call to the ask capability, ask at most two questions: those whose answers would change the mission most. Skip any the user already answered.
   - **What's at the centre**, when a learning request joins two subjects: "X itself, with Y as the examples", or "the Y models built on X". If the user wants current research instead, suggest the researcher.
   - **What it's for**, if unsaid: 3-4 concrete uses, the likeliest first. It sets the goal, the depth and what's out.
   - **Which areas**, for a broad research question: 4-6 areas, with multiple answers allowed. A learning mission has no areas: the curriculum search finds them.
5. Set depth from the purpose: `orient`, `use` or `master`. Ask only if the purpose leaves it open.
6. Write the answers into `mission.md`, delete the comments, and remove the `<!-- template -->` line.
7. Run `puck topic check <topic> --has mission` and fill whatever it reports empty.
8. Show the mission in a few lines and move on. The user can step in to change it.

## Output
A filled `mission.md`.

## Done when
- [ ] `puck topic check <topic> --has mission` passes.
- [ ] A learning mission's subject is taught from its foundations; a research mission's question could be answered in a paragraph.

## If something fails
If the user can't choose, take the likeliest purpose and `orient`, say so in the mission, and tell the user they can widen it later. Next step: `curriculum` for learning, `field-map` for research, unless the user only wanted the mission. The lead that loaded you opens the run's task once the mission is written.

## Host differences
Read references/host-tools.md if a named capability is unclear.
