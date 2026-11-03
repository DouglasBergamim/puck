# Puck

Puck is the user's layer in front of this harness. It gives you skills, agents and the `puck` command for two jobs: building and planning software, and researching and learning topics. `puck status` shows its state, and `docs/features.md` in Puck's home lists every skill, agent and command.

## Tasks

- Any work beyond a quick question or one-line fix is a task. Load the `task` skill and follow it from start to close.
- You own the whole workflow, including the retro at the end. Don't wait for the user to ask for it.
- Run `puck task start` before anything else, then read what its task pack points to.
- Two exceptions open no task: study sessions, because the `teach` skill keeps its state in the topic folder, and `onboard`, because it only reads.

## Always

- When you learn something non-obvious, run `puck note`.
- To claim something is done, show the command you ran and its output.
- Run `puck task show` to see the plan: what it holds, and what is done or not. After compaction, use it and the task folder to pick up where you left off.
- Never edit `dist/` or installed copies of skills.
