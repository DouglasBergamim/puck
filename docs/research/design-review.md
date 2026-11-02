**Verdict:** the layer decision holds, but Copilot compaction survival and the learning gate can't work as written. I ran nothing on a host. Claims marked verified come from docs or local `--help` and `ls`.

**Ranked changes**

1. **Copilot compaction has no re-injection point (verified).** There's no compact `sessionStart` source or post-compact event, `preCompact` output is ignored, and command `userPromptSubmitted` output is dropped. The skill fallback is the optional retrieval your findings reject. Fix: `preCompact` writes a marker and the next `postToolUse` injects it (CLI support unconfirmed). Otherwise rate Copilot Partial.
2. **`harness learn` can't gate answers.** The model can answer anyway and reports the attempt itself. Fix: record attempts from user-side input, and call this friction, not enforcement.
3. **Post-compact injection can overflow (verified).** Over 10,000 characters, Claude gets a path plus a 2,000-character preview and no instruction to read it. Fix: budget-test the combined payload, not just always-on.
4. **Auto memory bypasses the memory design (verified).** It's on by default, loads up to 200 lines/25KB, and is unreviewed. Plugins can't disable it. Fix: set `autoMemoryEnabled: false` at install. Copilot memory is unchecked.
5. **Static instructions shouldn't depend on hooks.** Project-root CLAUDE.md is re-read after compaction (verified). Content-only hosts get nothing, and a frozen task pointer goes stale. Fix: use host instruction files; hooks carry only pointer and checkpoint.
6. **"Copilot" is two hosts, neither ready (verified).** The shim reports the CLI not found, so "installed" is false. VS Code hooks are Preview and ignore matchers. Fix: install the CLI and test each separately.
7. **Learning is weakly served.** Anchors are code-shaped, tasks assume a project, and parallel sessions share `checkpoint.md`. The vault has no git (verified). Fix: checkpoint attempts and misconceptions, add a non-project home, key checkpoints by session, and init git.
8. **Anchor extraction hides host-specific parsers.** Transcripts likely differ by host, and Claude's may lag (verified). Fix: collect anchors incrementally from prompt and post-tool hooks.
9. **Consolidation has no runtime or milestone.** Core has no model access, and `-p` will default to `--bare`, which ignores OAuth (verified). Fix: make it a manual skill.
10. **Packaging is undecided.** Fix: target a Claude plugin, which carries skills, agents, hooks and MCP (verified). Test whether Copilot's legacy `.claude-plugin/plugin.json` support shrinks the generator. `plugin eval` expects evals below the plugin root and mocks MCP by default (verified), so root `evals/` plus `dist/` conflicts.
11. **The deny hook isn't a boundary.** Timeouts fail open by default on both hosts (verified), and Bash can likely evade path matching. Fix: use native deny rules and shell-less researchers.
12. **Milestones prove plumbing first.** Fix: build `plan`, `review` and checkpointing, then `research` on host search, then `learn`. Proof: one real task survives forced compaction on both hosts, and one topic is studied. Defer the memory inbox, MCP server, Exa/Jina/OpenAlex, `adr` and FSRS CLI. Run evals from the first skill.

**Fine:** Python/uv, grep first, SPEC.md, card approval, capability tiers and the memory/wiki split.

**Other claims:** `--bare` and `plugin eval` are verified. The AGENTS.md row is imprecise: `~/.claude/CLAUDE.md` doesn't suppress it, and a setting loads both. Exa's free credit and research citations are unchecked.

**Sources:** [Claude hooks](https://code.claude.com/docs/en/hooks), [plugins](https://code.claude.com/docs/en/plugins-reference), [memory](https://code.claude.com/docs/en/memory), [headless](https://code.claude.com/docs/en/headless.md), [evals](https://code.claude.com/docs/en/plugin-evals.md), [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-reference), [Copilot plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [VS Code hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)

### Critical Files for Implementation
Only the first exists:
- /Users/doug/.claude/plans/i-want-to-build-majestic-duckling.md
- /Users/doug/coding/harness/src/harness/hooks.py
- /Users/doug/coding/harness/src/harness/core/anchors.py
- /Users/doug/coding/harness/src/harness/core/learn.py
- /Users/doug/coding/harness/content/hosts/copilot.yaml
