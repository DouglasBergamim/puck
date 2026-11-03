---
name: agent-name
description: One line saying when to delegate to this agent.
mode: worker  # worker: a skill or lead starts it; lead: the user talks to it
tools: [read, search]
model: strong
skills: []    # skills it loads
agents: []    # worker agents it starts
max_turns: "20"
---
## Role
One sentence.

## You receive
The exact inputs the caller must provide.

## Rules
Everything it needs, restated. Assume it sees no instruction files.

## Workflow
1. ...

## Boundaries
What it must not do.

## Return
At most 1,500 tokens in this exact format, with details in a file:
- result:
- evidence_path:
