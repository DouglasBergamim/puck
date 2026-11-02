# AI agent harness internals and context management (as of 2026-11-01)

**Evidence labels**
- **[V]**: I fetched the primary source. Most pages came through a summarising fetch tool. I read raw text only for the Claude Code "how it works", "context window" and "prompt caching" pages and the Dreams page, plus PDF pages of three papers (2609.20804 pp. 1-12, 2605.10039 pp. 1-2, 2608.24358 p. 1).
- **[S]**: search-index extract or secondary source, not fetched.
- **[C]**: community claim.
- **[I]**: my inference.
- **[>6mo]**: dated before about 2026-05-01, so it may have changed.

**Fetch failures:** openai.com returned 403 for "Harness engineering" and "Unrolling the Codex agent loop", so neither was read directly. Nothing was saved to disk.

## Part A: How harnesses are built

### A1. General lessons and definitions

#### Takeaway
A harness is a loop, tools, context management and at least one control the model can't override. The strongest recurring lesson is that harness features encode assumptions about model weakness and go stale. Start small and re-test scaffolding on each model upgrade.

#### Cited Findings
- **[V]** Formal definition: an agent loop, a tool interface, active task-dependent context management (size-based truncation doesn't count) and a control that doesn't rely on model cooperation (2026-06-08, revised August) — [de Macedo](https://arxiv.org/html/2606.10106v1)
- **[V]** Taxonomy: "Agent = Model + Harness". Guides are feedforward and sensors are feedback, each either computational or inferential. Behaviour is the hardest category to harness (2026-04-02) [>6mo] — [Böckeler](https://martinfowler.com/articles/harness-engineering.html)
- **[V]** Source-code study of 11 harnesses: Claude Code, Codex CLI, Gemini CLI, Mistral Vibe, OpenHands, Aider, Mini-SWE-Agent, Hermes, Pi, OpenCode, OpenClaw (submitted 2026-07-15):
  - No runtime uses a general agent framework or embedding retrieval.
  - Skills appear in 9 of 11, MCP in 8 of 11, ACP in 6.
  - Rules are moving from prompt text into configuration.
  - It ends with 29 patterns, 18 recommendations and a 90-line scaffold — [Barbaste et al.](https://arxiv.org/abs/2609.00006)
- **[V]** That study did not measure performance, so it doesn't show simpler is better — [notes on the study](https://notesbylex.com/harness-engineering-anatomy-architecture-and-evolution-of-coding-agents)
- **[V]** Anthropic: use the simplest thing that works, show planning steps, and craft the tool interface carefully. Absolute file paths removed a class of errors (2024-12-19) [>6mo] — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- **[V]** Long-running design: an initializer writes `init.sh`, a progress file, a feature list and a first commit. The coding agent does one feature per session, then commits. The feature list was JSON with `passes` flags because the model was less likely to overwrite JSON than Markdown (2025-11-26) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- **[V]** Planner/generator/evaluator harness (2026-03-24) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps):
  - Claude judged its own work poorly and talked itself into approving defects.
  - Context resets were essential on Sonnet 4.5 and dropped on Opus 4.5.
  - Sprints were dropped on Opus 4.6.
  - The planner stayed, because the generator under-scoped without it.
  - Cost was solo $9 / 20 min versus harness $200 / 6 hr.
- **[V]** Managed Agents splits an append-only session log, the harness and the sandbox. Tool access is `execute(name, input) -> string`. Keeping the full log outside the window hedges against irreversible compaction (2026-04-08) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/managed-agents)
- **[V]** Manus (2025-07-18) [>6mo] — [Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus):
  - Cache hit rate is the key metric, with about 100:1 input to output tokens.
  - Mask tools rather than removing them.
  - Treat the file system as context, with restorable compression.
  - Recite goals through `todo.md`, keep errors in context, and vary repetitive patterns.
- **[S]** OpenAI (2026-02-11) [>6mo]: one big AGENTS.md failed. About 100 lines acting as a map into a structured `docs/` directory worked better, with the repo as system of record — [search extract of the post](https://openai.com/index/harness-engineering/)
- **[V]** Practitioner rules: turn each failure into a rule or hook, keep AGENTS.md short, stay silent on success and verbose on failure, and prune scaffolding (2026-04-19) [>6mo] — [Osmani](https://addyosmani.com/blog/agent-harness-engineering/)

#### Inferences
- **[I]** Build each compensating feature so it can be removed. Anthropic and Amp both reversed context-carryover decisions within about a year.
- **[I]** The stable part is the interface (log, loop, sandbox), not the tactics.

#### Gaps
- OpenAI's "Unrolling the Codex agent loop" could not be read, so Codex's prompt layout is not verified here.

### A2. Per-harness comparison

#### Takeaway
Single-loop agents with optional subagents have won. Plan mode is usually a mode, not a separate architecture. Background and cloud agents are now standard in commercial tools. Extension surfaces have converged on skills, hooks, MCP and Markdown agent files.

#### Cited Findings

| Harness | Loop and agents | Core tools | Permissions and sandbox | Extensions | Open source |
|---|---|---|---|---|---|
| **Claude Code** | Gather/act/verify loop. Subagents start in background by default, nest 3 layers, 20 concurrent. Forks, agent teams, `Workflow` tool, cloud sessions. [V] [how it works](https://code.claude.com/docs/en/how-claude-code-works), [subagents](https://code.claude.com/docs/en/sub-agents) | [46 table rows](https://code.claude.com/docs/en/tools-reference) by my count, including one removed and several conditional. Glob and Grep are absent by default on macOS, Linux and WSL. [V] | Rules run deny, then ask, then allow; [first match wins](https://code.claude.com/docs/en/permissions). Auto, Manual, Accept edits and Plan modes. [Seatbelt / bubblewrap](https://code.claude.com/docs/en/sandboxing) with a domain proxy. Auto is the default start mode from v2.1.283. [V] | [33 hook events, 5 handler types](https://code.claude.com/docs/en/hooks), skills, plugins, MCP, subagents. [V] | [Public repo](https://github.com/anthropics/claude-code) lists plugins, examples and docs, no visible core source. [sandbox-runtime](https://code.claude.com/docs/en/sandboxing) is public. Licence not confirmed. |
| **Codex CLI** | Multi-agent tools on by default. Thread cap `agents.max_concurrent_threads_per_session`. [V] [config](https://learn.chatgpt.com/docs/config-file/config-reference). GA in v0.115, about 6 concurrent. [S] [third party](https://www.morphllm.com/comparisons/codex-vs-claude-code) | Not verified | Seatbelt, bwrap + seccomp, MXC on Windows. `workspace-write` default for version-controlled folders, network off. `.git`, `.agents`, `.codex`, `.aws` protected. Optional auto-review fails closed. [V] [docs](https://learn.chatgpt.com/docs/agent-approvals-security) | Hooks (prompt and agent handlers parsed but skipped), skills, memories. [V] [config](https://learn.chatgpt.com/docs/config-file/config-reference) | [Apache-2.0](https://github.com/openai/codex), `codex-rs` directory. [V] |
| **Copilot CLI** | Ask/execute and plan modes. Built-in agents delegated automatically. `--cloud` sessions. ACP host. [V] [docs](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli). Explore, Task, Code Review, Plan agents and autopilot. [S] [changelog](https://github.blog/changelog/2026-01-14-github-copilot-cli-enhanced-agents-context-management-and-new-ways-to-install/) | Not verified | `--allow-tool` / `--deny-tool` with deny winning. Trusted directories described as heuristic. `/sandbox enable`. `/permissions assisted` uses a model as approver. [V] [docs](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli) | Instructions, MCP, hooks, skills, custom agents, Memory. [V] same | [Repo](https://github.com/github/copilot-cli) shows only install, changelog and container files. [V]. Likely a distribution repo. [I] |
| **Cursor** | Agents Window (Cursor 3, 2026-04-02) [S] [docs](https://cursor.com/docs/agent/agents-window). Explore and Browser subagents, one nesting level, background state files, worktree or VM isolation. [V] [docs](https://cursor.com/docs/agent/subagents) | Not verified | Seatbelt, Landlock + seccomp, WSL2. Sandboxed agents stop 40% less. [V] [2026-02-18, >6mo](https://cursor.com/blog/agent-sandboxing) | [Hooks](https://cursor.com/docs/hooks) including `preCompact`. Reads `.cursor`, `.claude` and `.codex` agent directories. Skills, MCP, plugins. [V] | Not established here |
| **Aider** | Architect mode. [S] Latest release [0.86.2, 2026-02-12](https://pypi.org/project/aider-chat/). [V] A July 2026 review claims [development stalled](https://codemyspec.com/blog/aider-review-2026). [C] | Not verified | Not verified | Not verified | [Apache](https://pypi.org/project/aider-chat/) [V] |
| **OpenCode** | Build and Plan primaries, General and Explore subagents, hidden compaction, title and summary agents. [V] [docs](https://opencode.ai/docs/agents/) | [13](https://opencode.ai/docs/tools/), ripgrep-based search [V] | All tools allowed by default. Allow/ask/deny with last match winning, plus a `doom_loop` key. [V] [docs](https://opencode.ai/docs/agents/). No OS sandbox found. | Custom tools, MCP, skill tool. [V] | [MIT, 224k stars](https://github.com/anomalyco/opencode) [V] |
| **Cline** | Plan/Act, `/deep-planning` hands off to a fresh task, read-only [subagents](https://docs.cline.bot/features/subagents). [S] | Not verified | Auto-approve and checkpoints. [S] | Rules, skills, plugins, MCP, hooks, SDK. [S] | Open source [S] |
| **Roo Code** | [Shut down](https://kilo.ai/compare/roo-code-shutdown-roomote): announced 2026-04-21, repo archived 2026-05-15, pivoted to Roomote. Multiple secondary sources. [S] Don't build on it. | | | | |
| **Goose** | Subagents default to 25 turns and 5 min, no nesting. [S] [docs](https://goose-docs.ai/docs/guides/subagents) | Via extensions | Auto, approve, smart_approve, chat modes. [S] [docs](https://goose-docs.ai/docs/guides/goose-permissions). Seatbelt Desktop sandbox via `GOOSE_SANDBOX`. [S] [v1.25](https://goose-docs.ai/blog/2026/02/23/goose-v1-25-0) | MCP extensions and recipes. [S] [AAIF](https://aaif.io/blog/how-goose-is-building-a-distributed-ai-teammate-ecosystem) | Licence not verified |
| **Pi** | Omits subagents, plan mode, permission popups, todos and background bash. Extensions add them. Sessions are branching trees. [V] [pi.dev](https://pi.dev/) | read, write, edit, bash; prompt plus tools under 1,000 tokens. [V] [>6mo](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/) | YOLO by default in 2025. Gates and sandboxes are now extensions. [V] same sources | TypeScript extensions, skills, packages. "MCP is built in", reversing the 2025 stance. [V] [pi.dev](https://pi.dev/) | [MIT](https://pi.dev/) [V] |
| **Hermes Agent** | Subagents, background post-turn review of memory and skills. [V] [memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | 40+ [V] [repo](https://github.com/NousResearch/hermes-agent) | Backends: local, Docker, SSH, Modal, Daytona, Vercel. [V] same | Autonomous skill creation (agentskills.io), memory providers. [V] same | [MIT, about 259k stars](https://github.com/NousResearch/hermes-agent) [V] |
| **Letta Code** | Stateful single agent. General-purpose, forked and recall subagents in background. [V] [repo](https://github.com/letta-ai/letta-code) | Not listed | Configurable auto-approve and auto-deny. [V] same | Skills, hooks, mods; can rewrite its own memory, prompts and harness. [V] same | [Apache-2.0](https://github.com/letta-ai/letta-code) [V] |
| **Amp** | Neo CLI rebuild (2026-05-06). [S] [Latent Space wiki](https://latent.space/wiki/amp-code/) | Not verified | Not verified | Plugin API [S] | Not verified |
| **Antigravity CLI** | Successor to Gemini CLI, dynamic parallel subagents. [S] [tutorial](https://www.datacamp.com/tutorial/antigravity-cli) | Not verified | Not verified | `.agents/rules/`, skills [S] | Not verified |

**Minimal versus large tool sets**
- **[V]** The best evidence is a controlled ablation (2026-09-17). It compared a predefined set of 7 workspace tools plus bash against bash-only, on open-weight models and 128K windows — [Fan et al.](https://arxiv.org/html/2609.20804v1):
  - Weak model (Nemotron-3 30B): predefined tools added 15.0 points on SWE-Bench and 10.1 on Terminal-Bench.
  - Strong model (Nemotron-3 550B): bash-only added 3.6 and 5.6 points, and cut cost 53% and 30%.
  - Mistral Medium 3.5: tools added 23.2 points on SWE-Bench, while bash-only added 6.7 on Terminal-Bench. The best action space depends on task type too.
- **[V]** The minimal case: frontier models already know these tools, and Playwright and Chrome DevTools MCP cost 13.7k and 18k tokens up front [>6mo] — [Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- **[V]** Claude Code resolves the tradeoff with many deferred stubs, so a large catalogue costs little (2026-04-30) [>6mo] — [Shihipar](https://claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/)

**Permissions evidence**
- **[V]** Users accept 93% of manual prompts. Claude's classifier sees only user messages and tool calls, so the agent can't argue past it. False negatives were 17% on real overeager actions (2026-03-25) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)
- **[V]** A default-read sandbox still exposes `~/.ssh` and `~/.aws/credentials` unless denied — [Claude Code docs](https://code.claude.com/docs/en/sandboxing)

#### Inferences
- **[I]** For one user on frontier models, around 6-8 tools plus lazily loaded extras is a defensible base. `read`, `edit`, `bash` and a search tool are the core.
- **[I]** An OS sandbox with network deny-by-default beats approval prompts, given the 93% acceptance rate.
- **[I]** Readable code to study: Codex (Rust), OpenCode, Pi (smallest), Hermes (richest context code), Letta Code (memory).

#### Gaps
- Exact tool lists for Codex, Copilot, Cursor and Cline.
- Copilot agent mode in VS Code, including whether its code is open.
- How the 2609.00006 authors read Claude Code's source, given no visible core source in the repo.
- Factory Droid, OpenHands and Devin were not covered.

## Part B: Context management

### B1. Compaction, summarization and context editing

#### Takeaway
Summaries lose most exact details but can still preserve task progress when model and prompt are good. The best-evidenced policy is staged: cheap elision of old tool output first, LLM summary only under real pressure.

#### Cited Findings

| System | Trigger | What's kept |
|---|---|---|
| Claude Code | Model's limit; about [967K on native-1M models](https://code.claude.com/docs/en/model-config); `/autocompact` 100K-1M [V] | [Re-injects](https://code.claude.com/docs/en/context-window) root CLAUDE.md, auto memory, plan, skill descriptions. Re-reads up to 5 recent files; files over 5,000 tokens become path references. Skills capped at 5K each, 25K total [V] |
| Anthropic API (threshold) | [Default 150K, minimum 50K](https://platform.claude.com/docs/en/build-with-claude/compaction-threshold); `compact_20260112`; always on in Managed Agents [V] | `instructions` replaces the default prompt entirely. Content before the compaction block is dropped [V] |
| Anthropic API (on demand) | [Client-chosen; `compact-2026-09-04`](https://platform.claude.com/docs/en/build-with-claude/compaction) [V] | Can keep recent turns verbatim and run in the background. Preferred where available [V] |
| Context editing | [Default 100K, keep 3 tool uses](https://platform.claude.com/docs/en/build-with-claude/context-editing); `clear_at_least` justifies the cache break [V] | Placeholder replaces the result. With the memory tool, Claude is warned to save first [V] |
| OpenAI API | [`compact_threshold` or stateless `/responses/compact`](https://developers.openai.com/api/docs/guides/compaction) [S] | Encrypted compaction item plus retained items [S] |
| Codex CLI | [`model_auto_compact_token_limit`](https://learn.chatgpt.com/docs/config-file/config-reference); model default [V] | Initial context, recent user messages up to about 20k, summary [C] [>6mo] [gist](https://gist.github.com/badlogic/cd2ef65b0697c4dbe2d13fbecb0a0a5f) |
| Copilot CLI | [About 80% background, about 95% pause](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management). Another page says [95%](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli), so GitHub's docs conflict [V] | Goals, original instructions, plans, todos. Summaries saved as readable checkpoints [V] |
| Goose | [80% or 225K, whichever first](https://goose-docs.ai/docs/guides/sessions/smart-context-management/) [V] | Older tool outputs summarized in the background [V] |
| Pi | [Window minus 16,384 reserve](https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/docs/compaction.md) [V] | Keeps last 20,000 tokens. Goal, Constraints, Progress, Decisions, Next Steps, Critical Context, file lists [V] |
| Hermes | [50%, floored at 75% for windows under 512K](https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching) [V] | Prunes tool output first with no LLM call. Lean mode adds a mechanical anchor index, verbatim user messages and a search pointer [V] |
| OpenCode | Overflow check [C] | Protects last 40K of tool output, skips pruning under 20K, exempts skill output [C] [ports](https://docs.rs/behest-runtime/0.5.9/src/behest_runtime/compaction/prune.rs.html) |
| Amp Neo | [90%](https://latent.space/wiki/amp-code/) [S] | Summary into a fresh window [S] |

**Stale third-party numbers:** blog figures of 75-80% or 95% for Claude Code conflict with [current docs](https://code.claude.com/docs/en/model-config). `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` doesn't appear on that page.

**Measured results**
- **[V]** Fan et al. (176 settings) — [paper](https://arxiv.org/html/2609.20804v1):
  - Thresholds were soft 0.6, hard 0.85, recent window 0.3 of usable budget, tool results cut at 24K characters.
  - The value of managing context shrank as windows grew: 35.7, 15.9, 5.5 and 2.7 points on SWE-Bench at 32K, 64K, 96K and 128K. This tracked a falling overflow rate, 78.7% down to 8.7%.
  - Elide-then-summarize (T4) had the lowest mean cost at every budget, with comparable accuracy.
  - Reversible recall was rarely used. 36 of 64 settings never called it, and it gave no accuracy gain over plain elision (-0.36 points).
  - Planning added 11.6 points for the weak model on SWE-Bench. It cut cost about 30% for stronger models, with 0.4-2.0 points lost on SWE-Bench.
  - Caveat: open-weight models only, windows at or below 128K.
- **[V]** Compact-Bench (v2, 2026-10-28) — [paper](https://arxiv.org/html/2610.31710):
  - Damage to tasks that passed with full history ranged from 5% (Opus 4.8, 1 of 22) to 64% (DeepSeek-Flash, 14 of 22).
  - The best LLM summary kept 16.0% of recurring details, versus 79.1% for mechanical `anchor_index` extraction.
  - Prompts passed 16-19 of 22. Kimi Code led on tasks while Claude Code's prompt retained the most details.
  - Summaries kept target files but lost the progress needed to finish.
  - Caveats: 22 validated cases, literal string matching, and small samples at later boundaries.
- **[S]** SelfCompact (2026-06-22): a model-invoked compaction tool with a rubric matched or beat fixed intervals at 30-70% lower cost. The gain vanished without the rubric. Tested on math and search, not coding — [Apple page](https://machinelearning.apple.com/research/self-compacting-language-agents)
- **[V]** Amp replaced compaction with manual handoff in [2025](https://ampcode.com/news/handoff) [>6mo], then reversed: ["handoff is out. Compaction is in."](https://www.havoptic.com/r/amp-neo) (release notes via mirror) [S]
- **[V]** Switching models mid-task carries a cost. Full-trajectory escalation recovered under half of the quality gap at a substantial premium. Downshifting was favorable (2026-08-25) — [AWS](https://arxiv.org/pdf/2608.24358)

#### Inferences
- **[I]** Don't trust a summary alone. Pair it with a mechanical anchor list (paths, SHAs, errors, URLs), verbatim user messages, explicit progress state, and a pointer to the full log.
- **[I]** Fan's null on recall is about models choosing to fetch elided output. It doesn't rule out keeping the log for you or for recovery.
- **[I]** Thresholds matter less than whether the summarizer is strong. Use a strong model for compaction rather than the cheapest one.

#### Gaps
- No controlled study on frontier models at 1M windows.
- No head-to-head of server-side versus client-side compaction.
- Compaction evaluated on learning or planning work rather than code repair.

### B2. Memory files and hierarchy

#### Takeaway
Keep always-on memory small, human-readable and file-based, with deeper notes loaded on demand. Evidence for instruction files is mixed. Evidence for autonomous consolidation is weak, and verifiable memory looks safer.

#### Cited Findings
- **[V]** CLAUDE.md: managed, user and project scopes, loaded each session; subdirectory files load on access. Imports go 4 hops. Target under 200 lines. Files over 4 MiB are skipped — [memory docs](https://code.claude.com/docs/en/memory)
- **[V]** Auto memory: `MEMORY.md` is a one-line-per-entry index. First 200 lines or 25KB load; topic files load on demand. Four types: user, feedback, project, reference. Derivable facts are skipped deliberately — [memory docs](https://code.claude.com/docs/en/memory)
- **[V]** That page never mentions dreaming or consolidation, so a Claude Code "auto dream" remains unverified. Docs do describe reminders to merge or drop stale entries — [memory docs](https://code.claude.com/docs/en/memory)
- **[V]** Path-scoped rules and nested CLAUDE.md are summarized away by compaction until re-triggered — [context window](https://code.claude.com/docs/en/context-window)
- **[V]** Codex concatenates root to leaf, with `AGENTS.override.md` winning per directory. Combined cap is 32 KiB and it's built once per run — [docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- **[V]** Codex memories are off by default. Defaults: rollouts up to 30 days old, 16 per startup, 6 idle hours, pruned after 30 unused days — [config](https://learn.chatgpt.com/docs/config-file/config-reference). A two-phase pipeline is described only by [third parties](https://codex.danielvaughan.com/2026/04/18/codex-built-in-memory-system-deep-dive/) [S]
- **[V]** Dreams: an async job over a memory store plus 1-100 sessions. It produces a separate output store and never changes the input. Research preview, not ZDR-eligible, runs minutes to hours — [Anthropic](https://platform.claude.com/docs/en/managed-agents/dreams)
- **[V]** Letta MemFS: a git repo of Markdown files with frontmatter. Root files are always in the system prompt. Subdirectories with their own `MEMORY.md` stay out until needed — [MemFS](https://docs.letta.com/concepts/memfs). Dreaming runs in background subagents after N steps or on compaction — [memory](https://docs.letta.com/letta-code/memory)
- **[V]** Hermes: `MEMORY.md` 2,200 chars and `USER.md` 1,375 chars, frozen at session start to preserve the cache. Overflow returns an error that forces the agent to consolidate. SQLite FTS5 session search — [docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- **Conflict:** the [Hermes repo](https://github.com/NousResearch/hermes-agent) says search uses LLM summarization, while the [docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) say results are raw messages.
- **[V]** Copilot memory stores facts with code citations and verifies them at read time. A/B results: PR merge rate 83% to 90%, review feedback 75% to 77%, both p<0.00001 (January 2026) [>6mo] — [GitHub](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/). The vendor reports this about its own feature. A later 28-day TTL is [secondhand](https://agentpatterns.ai/tools/copilot/copilot-memory/) [S]

**Instruction files: measured**
- **[V]** Gloaguen et al.: across 438 tasks, LLM-generated files lowered success slightly (0.5% and 2%; the intro says 3%, so the paper is internally inconsistent) and raised cost 20-23%. Human-written files added about 4%, except on Claude Code per the results section, and raised cost by at most 19%. Authors advise skipping generated files and keeping human files minimal (arXiv 2602) [>6mo] — [paper](https://arxiv.org/html/2602.11988v1)
- **[V]** McMillan: 1,650 Claude Code sessions. File size (25-500 lines), position, architecture and conflicts showed no detectable effect on compliance. Compliance fell about 5.6% in odds per generated function (OR 0.944), median first omission at function 4. Tasks differed by up to 26.2 points. The target was a trivial annotation (arXiv 2605) — [paper](https://arxiv.org/pdf/2605.10039). This cuts against Anthropic's advice that [longer files reduce adherence](https://code.claude.com/docs/en/memory).
- **[S]** Vercel: an 8KB docs index in AGENTS.md reached 100%, versus 79% for skills, which went uninvoked in 56% of cases. Narrow Next.js eval — [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)

**Consolidation: measured (secondhand)**
- **[S]** Reported findings: iterated LLM updates "round off" facts, LLM supersession judgment scored 67.2% versus 94.8% for a deterministic rule, and multi-hop conflict resolution scored about 6%. No shipping system has published before/after numbers — [Arize catalogue](https://arize.com/blog/memory-is-still-a-missing-primitive-cataloguing-what-the-field-is-actually-shipping.md) (updated 2026-10-08). I read this catalogue, not the underlying papers.

#### Inferences
- **[I]** Use a small always-loaded profile plus a one-line index, topic files, git versioning, and a hard size cap that forces curation.
- **[I]** Consolidate into a new version, as Dreams does, so you can diff and reject it. Store provenance for each fact.
- **[I]** For code facts, verify at read time. For learning, cite the source and date.
- **[I]** Don't rely on a long-lived rule staying followed through a session. Enforce with hooks, or re-inject near the point of use.

#### Gaps
- No independent benchmark of Dreams, Letta dreaming or Hermes's learning loop.
- [Letta's 74.0% on LoCoMo](https://arize.com/blog/memory-is-still-a-missing-primitive-cataloguing-what-the-field-is-actually-shipping.md) is secondhand.
- Published Terminal-Bench scores for Letta [conflict](https://rywalker.com/research/letta).

### B3. Progressive disclosure

#### Takeaway
Load names and descriptions eagerly and bodies lazily. This now covers skills, MCP tools, memory and logs. The risk is that the model never pulls what it needs, so anything critical stays always-on.

#### Cited Findings
- **[V]** Skills: listing text capped at 1,536 chars, body loaded on use, `SKILL.md` under 500 lines, `context: fork` runs in a subagent, `paths` scopes activation — [Claude Code docs](https://code.claude.com/docs/en/skills)
- **[V]** Codex skill catalogue budget: 2% of the window, capped at 10,000 tokens — [config](https://learn.chatgpt.com/docs/config-file/config-reference)
- **[V]** Tool search: context fell from about 77K to about 8.7K tokens. Accuracy rose 49% to 74% (Opus 4) and 79.5% to 88.1% (Opus 4.5). Programmatic calling saved 37% (2025-11-24) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- **[V]** MCP tools are deferred by default in Claude Code — [docs](https://code.claude.com/docs/en/how-claude-code-works)
- **[V]** Cursor's file-based approach (2026-01-06) [>6mo] — [Cursor](https://cursor.com/blog/dynamic-context-discovery):
  - Long tool output, chat history and terminal sessions become files.
  - MCP descriptions sync to folders, cutting total tokens 46.9% in A/B runs that called an MCP tool.
- **[V]** Copilot CLI spills tool output over 20 KiB to temp files — [docs](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management)
- **[V]** Claude Code's Read returns at most 25,000 tokens per call by default — [tools reference](https://code.claude.com/docs/en/tools-reference)

#### Inferences
- **[I]** Vercel's skill misses and Fan's unused recall tool point the same way: models under-use optional retrieval. Critical facts belong in the always-on layer or a deterministic trigger.

#### Gaps
- Few independent evals of skill trigger reliability beyond Vercel's.

### B4. Prompt caching and cache-stable layout

#### Takeaway
Caching is a design constraint, not an optimisation. Keep an append-only conversation behind a frozen prefix, and put changing state in messages.

#### Cited Findings
- **[V]** Anthropic — [docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching):
  - Prefix order is tools, then system, then messages; 4 breakpoints; 20-block lookback.
  - TTL is 5 minutes or 1 hour. Writes cost 1.25× or 2×.
  - Reads cost 0.1×, 0.05× on Opus 5.5 and Sonnet 5.5, 0.025× on Fable 5.1.
  - Minimum is 512 tokens on current models.
  - `tool_choice`, images and non-deterministic JSON key order all break hits.
- **[V]** OpenAI: on by default. GPT-5.6+ has a 1,024-token minimum, 30-minute or 12-hour TTL, reads at 0.1× (0.05× on GPT-6.1 Sol and Terra), and writes at 1.25× or 2.5× — [docs](https://developers.openai.com/api/docs/guides/prompt-caching)
- **[V]** Claude Code layers: system plus tools, then project context, then conversation. Changing state goes in `<system-reminder>` messages. Plan mode is a tool pair. Tool stubs stay stable. Compaction reuses the parent's exact prefix, and side computations should fork the parent's prefix too. Treat hit rate like uptime [>6mo] — [Shihipar](https://claude.dev/blog/lessons-from-building-claude-code-prompt-caching-is-everything/)
- **[V]** Cache-safe: file edits, CLAUDE.md edits (which don't apply until reload), permission changes, skills, `/rewind`, and subagents. Cache-breaking: model switches, adding tools, compaction, and removing images. A plain subagent builds its own cache; a fork reads the parent's — [docs](https://code.claude.com/docs/en/prompt-caching)
- **[V]** Hermes marks the system prompt plus the last 3 messages, and freezes memory to protect the cache — [docs](https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching)

#### Inferences
- **[I]** Log the hit rate from day one.
- **[I]** Context editing and compaction both spend cache, so batch them rather than clearing small amounts often.

#### Gaps
- No independent study of cost saved by cache-aware layout in a personal-use pattern, where idle gaps exceed TTLs.

### B5. Retrieval: grep, embeddings and repo maps

#### Takeaway
Open harnesses and CLIs have standardised on agentic search with no vector index. Evidence says this isn't strictly better: agents often miss relevant files, and hybrids score higher on recall. For small to medium repos, grep is a sound default. Add ranking if misses appear.

#### Cited Findings
- **[V]** None of 11 studied harnesses retrieves code with embeddings (Cursor and Copilot weren't in that sample) — [Barbaste et al.](https://arxiv.org/abs/2609.00006)
- **[V]** Anthropic's hybrid: CLAUDE.md up front, glob and grep just in time (2025-09-29) [>6mo] — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **[V]** Cursor reports semantic search added 12.5% accuracy on average (6.5-23.5% by model). Code retention rose 0.3% overall and 2.6% on 1,000+ file repos. It recommends combining with grep. Cursor sells this feature (2025-11-06) [>6mo] — [Cursor](https://cursor.com/blog/semsearch)
- **[V]** Agent Retrieval Bench (427 samples, 25 repos; July 2026) — [paper](https://huggingface.co/papers/2607.24882):
  - Logged agents never touched a gold file on 27-35% of samples.
  - RepoMap led budget-constrained coverage (BCY@8k 0.3788).
  - Embeddings led Recall@20 (0.7029).
  - RRF fusion of RepoMap and embeddings raised MRR from 0.2296 to 0.2713.
  - Oracle context added 0.3115 File F1, versus about 0.075 for lexical or RRF seeding.
- **[V]** CORE-Bench: common embedding models drop steeply in agentic settings, and simple supervised fine-tuning helps (accepted EMNLP 2026) — [abstract](https://arxiv.org/abs/2606.11864)
- **[V]** Aider's repo map: tree-sitter definitions and references, graph ranking, trimmed to `--map-tokens` (default 1k) (2023-10-22) [>6mo] — [Aider](https://aider.chat/2023/10/22/repomap.html)

#### Inferences
- **[I]** Why grep wins in CLIs: no index to keep fresh, exact on identifiers, cheap to ship. That reading is mine, as the studies report the fact rather than the reason.
- **[I]** A compact, ranked repo map injected at start is a cheap middle step before embeddings.
- **[I]** For learning notes, a personal knowledge base differs from code. BM25 plus embeddings may justify itself there. I found no direct evidence either way.

#### Gaps
- No controlled end-to-end comparison on task success across grep, repo map and hybrid.
- Non-code retrieval was not researched.

### B6. Subagents, file offloading and multi-session handoff

#### Takeaway
Subagents are good for isolating noisy reads, at the cost of context transfer. Files are the universal offload layer. Multi-session work relies on a few structured artifacts rather than transcripts.

#### Cited Findings
- **[V]** Claude Code subagents get a fresh window and return only a summary. Explore and Plan skip CLAUDE.md. Rules must be restated in the delegation prompt, and forks inherit everything — [docs](https://code.claude.com/docs/en/sub-agents)
- **[V]** Returns are often 1,000-2,000 tokens [>6mo] — [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **[V]** Cursor: five parallel subagents cost roughly 5× the tokens, and shared checkouts can conflict — [docs](https://cursor.com/docs/agent/subagents)
- **[V]** Counterview: subagents are a "black box within a black box". Gather context in one session, produce an artifact, start fresh [>6mo] — [Zechner](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
- **[V]** Delegation isn't a cure: one fresh worker hit a 2.4M-character load and three compactions, then lost a contract. Single observation — [Xue](https://arxiv.org/html/2607.17937v2)
- **[V]** Handoff artifacts that worked: git log, progress file, JSON feature list, `init.sh`, and a fixed start routine that smoke-tests first [>6mo] — [Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). File-based sprint contracts between agents [>6mo] — [Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- **[S]** Cline's todo list survives compaction — [coverage](https://dev.to/terminalblog/cline-v325-ships-deep-planning-focus-chain-and-auto-compact-three-features-that-fix-long-task-ccl)
- **[V]** Claude Code's plan file is re-injected from disk after compaction — [docs](https://code.claude.com/docs/en/context-window)

#### Inferences
- **[I]** Good first subagent: read-only exploration, because it needs little context and is noisy.
- **[I]** Keep the plan and task state on disk, outside the transcript.

#### Gaps
- No controlled test of subagent use on success versus single-agent runs. [Anthropic flagged this as open](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) in 2025.

### B7. Context window degradation

#### Takeaway
Degradation is real but conditional, and no universal fill threshold is supported. Vendors assert it. Controlled evidence shows reliability loss and dropped obligations, mostly in later steps rather than search.

#### Cited Findings
- **[V]** Anthropic's docs state response quality degrades as a conversation grows — [compaction](https://platform.claude.com/docs/en/build-with-claude/compaction)
- **[V]** Xue (2026-08-01) — [paper](https://arxiv.org/html/2607.17937v2):
  - Passes fell from 8/10 at about 11K characters to 3/10 at about 299K. Not significant at p<0.05 (p=0.0698).
  - Relevant and irrelevant padding hurt equally.
  - The author claims no universal threshold.
  - Agents found the right files, then failed to turn requirements into tasks.
  - A detailed external checklist passed 10/10, versus 5/10 for a generic self-check (p=0.0325).
  - Single author, 10 runs per condition, one main model.
- **[V]** Fan: window size alone mattered mostly by preventing overflow, and the benefit of management faded at 128K — [paper](https://arxiv.org/html/2609.20804v1)
- **[S]** Blog claims of a 60-70% degradation point give [no primary source](https://zylos.ai/research/2026-05-05-ai-agent-context-window-management-compaction-continuity-cost/). Treat them as folklore. [C]

#### Inferences
- **[I]** A verifier with an explicit checklist is the best-supported mitigation. It's also consistent with Anthropic's evaluator findings.
- **[I]** "Compact at X%" is less important than "split at natural task boundaries", which Claude Code's and Hermes's docs also advise.

#### Gaps
- No study isolates fill level as the single variable on frontier models.

### Proposed answer to "how would our context management work?" [I]
This is my synthesis, not sourced fact. Most evidence is from coding, so it may transfer imperfectly to learning and planning.

1. **Frozen prefix:** tools, then system prompt, then small profile, then memory index. Changing state goes in messages, and hit rate gets logged.
2. **Always-on layer:** a size-capped profile and one-line index, human-curated instructions under about 100 lines, no generated overview.
3. **On-demand layer:** skills, topic notes and tool stubs, with file-based lookups through grep and read.
4. **Output offload:** spill large tool output to files with head and tail kept in context.
5. **Staged pressure policy:** elide old tool output first, then summarize at a higher threshold, keeping recent turns and user messages verbatim.
6. **Summary format:** Goal, Constraints, Progress, Decisions, Next Steps, plus a mechanically extracted anchor list and a log pointer.
7. **Durable state outside the transcript:** append-only session log, plan file, task list in JSON, git for code and for memory.
8. **Consolidation:** run offline into a new git branch, with provenance, and review the diff. Never rewrite in place.
9. **Verification:** a concrete checklist run by a separate agent or script, plus hooks for hard rules.
10. **Evals:** replay your own sessions and test continuation after compaction, not just summary quality. Re-test scaffolding on each model change.
