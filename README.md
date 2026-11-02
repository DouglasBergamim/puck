# Puck

Puck is a layer in front of any agent harness. It optimises the context an LLM gets and improves its tools. It keeps each plan on disk with what is done and what is not, verifies the work with real checks, and turns what a task taught into reusable skills. History stays with the host.

## Layout

| Folder | What it holds |
|---|---|
| `context/` | The source of truth for everything the LLM sees: skills, agents, instructions, hook rules, knowledge, past retros and proposals |
| `src/core/` | The harness-neutral implementation |
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
