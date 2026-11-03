---
name: practice
description: >-
  Give the user an exercise on a concept, with its answer key or tests written
  before they start, and grade the attempt independently. Use when the user asks
  for exercises, problems, a quiz or practice, or when a study session needs a
  graded check. Not for teaching a concept from scratch (use teach).
metadata:
  version: "1"
  status: active
  invocation: model
  requires: "shell, subagents"
  origin: "milestone-3"
  last_evaluated: "never"
  credits: "Independent 0/1 rubric criteria from anthropics/k12-teacher-skills"
---
## Procedure
1. Pick the concept: the one the user names, or `puck learn next <topic>`. Read its wiki pages.
2. Choose the exercise type for the domain from `references/exercises.md`.
3. Write the exercise folder `exercises/<id>/` in the topic **before** showing the user anything: `exercise.json`, `prompt.md`, and the key (`key.md` and `rubric.md`, or failing tests plus starter files for code). Run `puck learn check <topic> <id>` once on a code exercise: it must fail before the user starts.
4. Give the user only `prompt.md`, and for code, the folder path. End the message there.
5. When the user answers, save the attempt to `exercises/<id>/attempt.md`, or for code, leave their files in the folder.
6. Grade:
   - code: `puck learn check <topic> <id>`; only exit 0 passes;
   - others: spawn the `grader` agent with the attempt, `key.md` and `rubric.md` paths, and nothing from this conversation.
7. Give feedback from the grade: what was right, then each missed criterion with the correction. Then offer one follow-up that targets the miss.
8. Record the result through `teach`'s close step, or `puck learn record` if this was a standalone practice.

## Output
An exercise folder with the key, the attempt and the grade, and feedback to the user.

## Done when
- [ ] The key or tests existed before the user saw the prompt.
- [ ] The grade came from `puck learn check` or the `grader` agent, not from your own judgement.
- [ ] Feedback named every missed criterion.

## If something fails
Without subagents, grade against the rubric yourself, one criterion at a time, and tell the user the grade wasn't independent.

## Host differences
Read references/host-tools.md if a named capability is unclear.
