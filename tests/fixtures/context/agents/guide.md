---
name: guide
description: A lead the user talks to. Use when the user asks for the guide.
mode: lead
tools: [read, subagents]
model: strong
skills: [sample]
agents: [helper]
workflow:
  - stage: sample
    skill: sample
    delivers: a sample result
    check: test -n sample
---
## Role
Guide.

## Context
The sample folder.

## Rules
Ask first.

## Workflow
1. **Sample.** Load `sample`.

## Boundaries
None.
