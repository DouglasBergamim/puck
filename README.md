# Puck

<p align="center">
  <img src="assets/739698be1b8d184623ba906e941bfa84.jpg" alt="Puck" width="180">
</p>

> **Hi! I'm Puck.**
>
> Puck is my personal coding companion, inspired by the tiny elf from Berserk. It may not be able to heal your wounds or defeat demons, but it can help organize your context, guide your tools, and make your development workflow feel a little less like surviving the Eclipse.


## Layout

| Folder | What it holds |
|---|---|
| `context/` | The source of truth for everything the LLM sees: skills, agents, instructions, hook rules, study topics, past retros and proposals |
| `src/core/` | The harness-neutral implementation: `common/`, `primitives/`, `tools/work/`, `tools/learning/` |
| `src/adapters/` | One deterministic transform per harness |
| `src/cli/` | The `puck` command |
| `docs/` | Design, spike results and research |
| `dist/` | Generated per-harness packages. Never edit these |
| `state/` | Task registry and locks, gitignored |

## Setup

```
uv sync
uv tool install --editable .
puck build
claude --plugin-dir "$PWD/dist/claude"
```

`dist/generic` works with any harness that reads `AGENTS.md` and `.agents/skills/`.

## Adding a harness

1. Add `src/adapters/<harness>.py` with a subclass of `Adapter` or `PluginAdapter`, overriding only what differs.
2. Register it in `src/adapters/__init__.py`.
3. Run `UPDATE_GOLDEN=1 uv run pytest tests/test_adapters.py`, then review the new files in `tests/golden/<harness>/`.

Adapters are pure, so core never changes. If adding one needs a core change, the neutral model is missing something, and that should be fixed there rather than with a harness branch.

## Development

```
uv run pytest
uv run puck lint
uv run puck build
```

This repo holds personal data, so any remote must be private.
