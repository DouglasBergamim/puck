# Milestone 1 spikes

Status on 2026-11-01, updated after milestone 2. "Tested" means run in a real session on Claude Code 2.1.316. "Docs" means read from vendor docs and not run.

| Question | Status | Result |
|---|---|---|
| Plugin loads on Claude Code | Tested | `--plugin-dir dist/claude` works; the skill appears as `puck:status` |
| Session-start injection on Claude Code | Tested | The model sees the injected line |
| Plan survives compaction on Claude Code | Tested | After `/compact`, compact `SessionStart` restores the open plan checklist |
| Copilot `agentStop` can block | Docs | Yes: `decision: "block"` with `reason`, `stop_hook_active`, capped at 8 consecutive blocks |
| User-level Copilot hooks | Docs | `~/.copilot/hooks/*.json` |
| Copilot legacy plugin format | Docs | Root `plugin.json` plus `skills/`, `agents/`, `hooks/hooks.json`; install with `copilot plugin install <path>` |
| Parallel tasks in worktrees on Claude Code | Tested | Two sessions ran at once and stayed bound to their own tasks |
| Duplicate skills from dual directories | Avoided | Plugins are the install path, so skills aren't copied to both directories |
| Plugin linked into `~/.claude/skills/` loads in every session | Tested | `puck install` links it; `claude plugin list` shows `puck@skills-dir` loaded. A plain `claude` in an empty folder got the session-start intro and home path, listed all 11 skills, and ran `puck topic list` without a prompt. `Write(...)` permission rules are ignored with a warning: `Edit(...)` rules cover every file-editing tool |
| Rebuilt skill reaching a new session | Open | `--plugin-dir` reads `dist/` directly; marketplace install not tested |
| `puck` writing to `PUCK_HOME` from a sandbox | Open | Hooks wrote outside the project in an unsandboxed session; host sandboxes not tested |
| Copilot worker isolation | Open | Not checked |
| Anything on real Copilot CLI or VS Code | Blocked | The Copilot CLI isn't installed |

Copilot's docs don't state how hook payloads are delivered. `puck hook` assumes stdin, so the first Copilot run must confirm that.

Copilot tool names in `src/adapters/copilot.py` are from docs and research, and the VS Code output format is an assumption until tested.
