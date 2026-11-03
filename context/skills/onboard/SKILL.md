---
name: onboard
description: 'Build a working picture of a codebase before changing it: what it is,
  how it''s laid out, how to build, test and run it, its rules and conventions, and
  what''s in flight. Use when starting work in an unfamiliar or long-unvisited project,
  or when the user asks for an overview, initial context or to get up to speed on
  a repo. Not for planning a change (use plan) or explaining one general concept.'
metadata:
  version: '2'
  status: active
  invocation: model
  requires: read, shell-read
  origin: 2026-11-02-review-puck-core-concepts-and-add
  last_evaluated: never
---
## Procedure
Onboarding only reads. It opens no task and writes no file: the brief lives in this conversation.

1. **Instructions first.** Read the project's instruction files: `AGENTS.md`, `CLAUDE.md` or the equivalent at the root and in the folder you're in, then `README`, `CONTRIBUTING` and any docs index. Rules quoted from these outrank anything you infer.
2. **Shape.** List the top level, then read the manifests and build files (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Makefile`, `justfile`) and the CI config. They give the language, the entry points and the real build, test and lint commands.
3. **State.** Run `git status --short`, `git branch --show-current` and `git log --oneline -n 10`. Run `puck task list` for open tasks here.
4. **Trace one path.** From the main entry point (a CLI's `main`, a server's routes, a library's public module), follow one real command or request through the layers. Name the 3-6 modules that matter and what each owns. Read signatures and docstrings; don't read whole large files.
5. **Budget.** Stop at about 25 file reads. Breadth beats depth here; the user can ask you to go deeper.
6. **Brief.** Reply with about 40 lines under these headings, every claim followed by the path or command it came from:
   - **What it is**: one or two sentences.
   - **Layout**: the key folders and modules, each with its role.
   - **Commands**: build, test, lint and run, each marked *found* (seen in a file) or *verified* (you ran it, read-only and fast).
   - **Rules**: the project's conventions and constraints, quoted.
   - **In flight**: branch, uncommitted work, open tasks, what recent commits were about.
   - **Gaps**: what's missing, unclear or contradictory, such as no documented test command, or docs that disagree with the code. State them; don't fix them.

## Output
A brief in the conversation. No file written.

## Done when
- [ ] Every line of the brief cites a path or a command.
- [ ] Commands are marked found or verified.
- [ ] Nothing in the project was changed.

## If something fails
If the project has no instruction files or manifests, say so under Gaps and infer the layout from the folder tree and file extensions, marking it inferred. If the repository is too large to trace in the budget, brief the part the user is working in and say what you left out.

## Host differences
Read references/host-tools.md if a named capability is unclear.
