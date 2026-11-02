# Puck

A layer in front of any agent harness that optimises the context an LLM gets and improves its tools. Claude Code and Copilot are the first adapters, not the scope. The design is in `docs/design.md`.

## Commands

- Tests: `uv run pytest`
- Lint primitives: `uv run puck lint`
- Build host packages: `uv run puck build`

## Rules

- `skills/`, `agents/`, `hooks/` and `instructions/` are the source. Never edit `dist/` or installed copies.
- Skill text names capabilities, not host tool names. `puck lint` enforces this.
- Hook logic lives in `cli/`. Hooks fail open and stay silent on success.
- Writes to shared files go through `cli/store.py`, because several sessions can run at once.
- `state/` holds verbatim prompts, so it stays gitignored.
- This repo holds personal data. Any remote must be private.
