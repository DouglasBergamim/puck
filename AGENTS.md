# Puck

A layer in front of any agent harness that optimises the context an LLM gets and improves its tools. Claude Code and Copilot are the first adapters, not the scope. The design is in `docs/design.md`.

## Commands

- Tests: `uv run pytest`
- Lint primitives: `uv run puck lint`
- Build harness packages: `uv run puck build`
- Reinstall after moving code: `uv tool install --editable . --reinstall`

## Rules

- `context/` is the source of truth for everything the LLM sees. Never edit `dist/` or installed copies.
- `src/core/` is layered: `common` ← `primitives` ← `tools/work` ← `tools/learning`, with `hooks.py` on top. Never import upwards; `tests/test_layout.py` enforces it.
- `src/core/` knows no harness by name. Harness differences live only in `src/adapters/`, which stay pure: no files, network, clock, environment or LLM.
- Skill text names capabilities, not host tool names. `puck lint` enforces this.
- Hook logic lives in `src/core/hooks.py`. Hooks fail open and stay silent on success.
- Writes to shared files go through `src/core/store.py`, because several sessions can run at once.
- History belongs to the host. Puck tracks plans and their steps, not sessions.
- This repo holds personal data. Any remote must be private.
