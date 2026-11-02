# Agent layer on top of multiple harnesses: research notes (as of 2026-11-01)

No files were written, as the override required. These notes are the deliverable.

**Evidence tags used throughout**
- **[P]**: taken from a primary page I fetched.
- **[S]**: search snippet or secondary source, not confirmed against a primary page.
- **[?]**: unknown. Not found, so left unfilled rather than guessed.
- Dates over about 6 months old are flagged as **(stale?)**.

**Major changes since early 2026, which older write-ups will have wrong**
- MCP went stateless and deprecated Sampling (2026-07-28).
- Agent Plugins 1.0 shipped (2026-08-06).
- Gemini CLI was retired for consumers (2026-06-18).
- Pi added MCP (2026-09-29).
- Agent Skills and A2A moved into AAIF.

---

## 1. Which portable standards exist, and what is their status and governance?

### Takeaway
Skills, MCP tool servers, and AGENTS.md are truly portable, and Agent Plugins 1.0 now packages the first two. Hooks, subagents, and commands have no shared standard, and Agent Plugins explicitly leaves them out of v1. ACP can drive almost any harness from the outside, but its proxy mechanism is still a draft.

### Cited Findings

**MCP**
- [P] The current revision is 2026-07-28, and version identifiers mark the last backward-incompatible change. — [Versioning](https://modelcontextprotocol.io/specification/versioning)
- [P] The `initialize` handshake and sessions were removed, and `server/discover` is mandatory for servers. Cross-call state now means server-minted handles passed as tool arguments. — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [P] Multi Round-Trip Requests (MRTR) replace server-initiated `sampling/createMessage`, `elicitation/create`, and `roots/list`. The server returns `resultType: "input_required"` and the client retries with `inputResponses`. — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [P] Roots, Sampling, and Logging are **Deprecated**, removable from the first revision on or after 2027-07-28. Sampling's stated migration is "Integrate directly with LLM provider APIs". — [Deprecated registry](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
- [P] Tasks moved from core into the extension `io.modelcontextprotocol/tasks`, polled via `tasks/get`. — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [P] TypeScript, Python, Go, and C# are Tier 1 SDKs supporting the new spec at release; Rust is in beta. — [Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [P] MCP Apps (`io.modelcontextprotocol/ui`) render sandboxed HTML. The named supporting clients are Claude, Claude Desktop, VS Code Copilot, Microsoft 365 Copilot, Goose, Postman, MCPJam, and Archestra.AI. — [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview)
  - Cursor's docs also list Apps as supported. — [Cursor MCP](https://cursor.com/docs/mcp)
- [P] VS Code marks Apps as Experimental. — [VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [P] **Skills over MCP** (`io.modelcontextprotocol/skills`, SEP-2640) is Final. It defines `skills/list`, `skills/get`, and `skill://` resources with SHA-256 manifests. "SDK and host support is still being implemented." — [Skills extension](https://modelcontextprotocol.io/extensions/skills/overview)
- [P] Tool search is not an MCP spec feature. The closest thing is a Progressive Disclosure Working Group. — [llms.txt](https://modelcontextprotocol.io/llms.txt)
  - Hosts implement it themselves. Claude Code has it on by default. — [Claude MCP](https://code.claude.com/docs/en/mcp)
  - Pi has a built-in `tool_search`. — [Pi 0.99.0](https://pi.dev/changelog/releases/0.99.0)
  - The spec helps by saying servers SHOULD return tools in deterministic order, for caching. — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

**Agentic AI Foundation (AAIF, Linux Foundation)**
- [P] Lists 10 projects: Agent Router, Agent Skills, A2A, AGENTS.md, agentgateway, Goose, MCP, Open Responses, OpenEnv, OpenSandbox. — [aaif.io](https://aaif.io/projects/)
- [S] Founded December 2025 with MCP, goose, and AGENTS.md. — [TechCrunch](https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/)
- [S] Goose moved to the `aaif-goose` GitHub org in April 2026. — [goose blog](https://goose-docs.ai/blog/2026/04/07/goose-moves-to-aaif/)

**Agent Skills**
- [P] Required fields are `name` (max 64 characters, lowercase, must match the directory) and `description` (max 1024). Optional fields are `license`, `compatibility`, `metadata`, and experimental `allowed-tools`. — [Spec](https://agentskills.io/specification)
- [S] Donated to AAIF, announced 2026-10-22, with the name, logo, GitHub org, and domain transferred. Coverage cites about 280M installs and 70+ platforms; I did not verify these figures. — [winbuzzer](https://winbuzzer.com/2026/10/27/anthropics-ai-workflow-standard-joins-the-linux-foundation-xcxwbn/), [fourweekmba](https://fourweekmba.com/ai-anthropic-donates-agent-skills-after-nearly-280m-installs/)
- The agentskills.io overview still describes the format only as originally developed by Anthropic and open to contributions. — [agentskills.io](https://agentskills.io/home)

**AGENTS.md**
- [P] No required fields. The closest file wins, explicit chat prompts override everything, and it is stewarded by AAIF. The site claims 60k+ projects. — [agents.md](https://agents.md/)

**Agent Plugins 1.0 (new, and missing from the suggested list)**
- [P] Published 2026-08-06. Proposed by Vercel and refined with AWS, Anysphere, GitHub, Microsoft, and OpenAI. Launch clients are ChatGPT/Codex, Cursor, GitHub Copilot, Kiro, and VS Code. — [Vercel](https://vercel.com/blog/introducing-agent-plugins)
- [P] v1 defines exactly two component types, `skills/` and `mcp.json`. Commands, hooks, agents, rules, and LSP are out of scope. Client-specific data goes under reverse-domain `extensions`. — [Spec 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)
- [P] `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expand only in stdio `args`, `env` values, and `cwd`. — [Spec 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)
- Anthropic is not named among the refiners or launch clients on the Vercel post.
- A separate "Open Plugins" spec also exists. Goose follows its hooks section. — [goose hooks](https://goose-docs.ai/docs/guides/context-engineering/hooks/)

**ACP**
- [P] Governed jointly by Zed and JetBrains under an interim model, working toward an independent foundation. It is not an AAIF project. — [Governance](https://agentclientprotocol.com/community/governance)
- [P] v2 is a proposal. Its RFD collection went Active on 2026-07-02, with revisions through 2026-10-30. It removes session modes and the Client filesystem/terminal surface. Schemas are planned as opt-in and unstable. — [v2 RFD](https://agentclientprotocol.com/rfds/v2/overview)
- [P] The **proxy chains** RFD is a working draft, implemented in the Rust SDK. A proxy sits between client and agent, can inject context and transform messages, and is managed by a conductor. It cannot edit the agent's system prompt or internal state. — [Proxy chains](https://agentclientprotocol.com/rfds/proxy-chains)

**A2A**
- [P] A Technical Steering Committee from eight companies, Apache 2.0, and the site banner says it joined AAIF. The site links "What's New in v1.0". — [a2a-protocol.org](https://a2a-protocol.org/latest/)
- [S] v1.0 shipped around March 2026, with v1.0.1 in May; accepted as an AAIF Growth Stage project in August 2026. — [rywalker](https://rywalker.com/research/google-a2a)
- [P] Gemini CLI is the only surveyed harness documented as delegating over A2A, via `kind: remote` subagents. — [Gemini subagents](https://geminicli.com/docs/core/subagents/)

**Agent Trace**
- [S] Cursor's RFC, v0.1.0 (January 2026) **(stale?)**, a JSON record of AI versus human code attribution, CC BY 4.0. Listed on the Thoughtworks Radar in April 2026, which notes Cline and OpenCode support. — [Thoughtworks](https://www.thoughtworks.com/radar/platforms/agent-trace)
- A direct fetch of github.com/cursor/agent-trace returned **404**, so its current status is unconfirmed.

### Inferences
- A sensible rule for the layer: treat a feature as portable only if it is defined by Agent Skills, MCP tools, AGENTS.md, or Agent Plugins.
- Hook names are converging on Claude's `PreToolUse` vocabulary through compatibility aliases, not through a standard. See Section 3.

### Gaps
- [?] No MCP extension matrix data: the [matrix page](https://modelcontextprotocol.io/extensions/client-matrix) lost its check marks in extraction, apart from "Partial" links. It lists Claude Code, VS Code, Goose, and Cursor as clients. Per-client extension support must be checked in the rendered page.
- [?] Whether Anthropic will adopt Agent Plugins.
- [?] The operational detail of Agent Skills governance after donation.

---

## 2. Harness-by-harness support matrix

### Takeaway
Skills and MCP tools work in all nine harnesses. Pi joined only in September 2026 for MCP. AGENTS.md is nearly universal but has a Claude Code trap. Two project directories, `.agents/skills` and `.claude/skills`, reach all nine according to their docs. Everything richer differs by host.

### Cited Findings

**Important host changes**
- [P] Gemini CLI stopped serving Google AI Pro/Ultra and free Code Assist individual users on 2026-06-18. Enterprise licences and paid API keys keep access. Antigravity CLI keeps Skills, Hooks, Subagents, and Extensions (as plugins), without 1:1 parity. — [Google](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)
- [S] Antigravity CLI is not open source the way Gemini CLI was. — [letsdatascience citing The Register](https://letsdatascience.com/news/google-replaces-gemini-cli-with-antigravity-cli-574b2056)
- [P] Pi added MCP, tool search, and codemode as built-in extensions in 0.99.0 (2026-09-29). — [Pi changelog](https://pi.dev/changelog/releases/0.99.0)
- [S] Pi 1.0 shipped on 2026-10-01. — [eesel](https://www.eesel.ai/blog/pi-coding-agent)
- [S] VS Code now has a harness picker with Copilot, Claude (on the Claude Agent SDK), and Codex harnesses, using an Agent Host Protocol. — [VS Code 1.140](https://code.visualstudio.com/updates/v1_140)
  - The hooks doc confirms Claude is a separate Session Target with its own hooks. — [VS Code hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)

**Matrix A: instructions, skills, MCP config**

| Harness | Instruction files | AGENTS.md behaviour | Project skills | User skills | MCP config |
|---|---|---|---|---|---|
| Claude Code | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/` | Read **only if no CLAUDE.md or CLAUDE.local.md exists at or above cwd** (v2.1.277+); `@AGENTS.md` import also works | `.claude/skills` | `~/.claude/skills` | `.mcp.json`, `~/.claude.json`; key `mcpServers` |
| VS Code Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (`applyTo`), also `.claude/rules` (`paths`) | Root, cwd, and intermediate dirs in Copilot sessions; nested is off by default in the Local harness | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.claude/skills`, `~/.agents/skills` | `.vscode/mcp.json` (`servers`), or portable `.mcp.json` / `~/.copilot/mcp-config.json` (`mcpServers`) |
| Copilot CLI | Shown by `copilot instruction list` [? paths] | [?] direct CLI docs not retrieved | `.github/skills`, `.claude/skills`, `.agents/skills` [S] | `~/.copilot/skills`, `~/.agents/skills` [S] | `~/.copilot/mcp-config.json`, `.mcp.json`, `.github/mcp.json`; **does not read `.vscode/mcp.json`** |
| Codex CLI | AGENTS.md, plus `AGENTS.override.md` | Native; root-to-cwd concatenation; 32 KiB limit; `project_doc_fallback_filenames` | `.agents/skills`, walking up to the repo root | `~/.agents/skills`, `/etc/codex/skills` | TOML `[mcp_servers.x]` in `config.toml` |
| Cursor | `.cursor/rules/*.mdc` (**plain `.md` is ignored**) | Root and nested | `.agents/skills`, `.cursor/skills`, compat `.claude/skills`, `.codex/skills` | Same four under `~/` | `.cursor/mcp.json`, `~/.cursor/mcp.json` |
| Gemini CLI | GEMINI.md, `contextFileName` | Listed by agents.md [S] | `.gemini/skills`, `.agents/skills` | `~/.gemini/skills`, `~/.agents/skills` | `mcpServers` in `settings.json` |
| Antigravity CLI | GEMINI.md and AGENTS.md both honoured | Yes | `.agents/skills` | `~/.gemini/skills`, `~/.gemini/antigravity-cli/skills` | `~/.gemini/config/mcp_config.json`, `.agents/mcp_config.json`; `serverUrl` key |
| OpenCode | AGENTS.md, `instructions` config | Native; falls back to CLAUDE.md; first match wins; `@refs` are not auto-parsed | `.opencode/skills`, `.claude/skills`, `.agents/skills` | `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills` | [?] OpenCode config; page not fetched |
| Cline | `.clinerules/`, `.cline/rules/`, `.cursorrules`, `.windsurfrules` | `AGENTS.md`, `~/.agents/AGENTS.md`; CLAUDE.md not mentioned | `.cline/skills`, `.clinerules/skills`, `.claude/skills` | `~/.cline/skills` | [?] page not fetched |
| Goose | `.goosehints`, `CONTEXT_FILE_NAMES` | AGENTS.md is checked first by default | `.agents/skills`, compat `.goose/skills`, `.claude/skills` | `~/.agents/skills`, `~/.claude/skills` | [?] extensions model; config path not fetched |
| Pi | AGENTS.md / CLAUDE.md; `SYSTEM.md` **replaces** the system prompt | Both read, walking parents; `AGENTS.override.md` | `.agents/skills` (plus the project skills dir) | `~/.agents/skills` (plus the user dir) | `~/.pi/agent/mcp.json`, `.pi/mcp.json` |

*Sources by harness*
- Claude: [memory](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills), [MCP](https://code.claude.com/docs/en/mcp)
- VS Code: [skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions), [MCP config](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
- Copilot CLI: [MCP](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers), [skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- Codex: [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- Cursor: [rules](https://cursor.com/docs/rules), [skills](https://cursor.com/docs/skills), [MCP](https://cursor.com/docs/mcp)
- Gemini and Antigravity: [skills](https://geminicli.com/docs/cli/skills/), [extensions](https://geminicli.com/docs/extensions/reference/), [migration](https://antigravity.google/docs/cli/gcli-migration)
- OpenCode: [skills](https://opencode.ai/docs/skills/), [rules](https://opencode.ai/docs/rules/)
- Cline: [skills](https://docs.cline.bot/customization/skills), [rules](https://docs.cline.bot/customization/cline-rules)
- Goose: [hints](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints), [skills](https://goose-docs.ai/docs/guides/context-engineering/using-skills)
- Pi: [skills](https://pi.dev/docs/latest/skills), [configuration](https://pi.dev/docs/latest/configuration)

**Matrix B: subagents, commands, plugins, headless, ACP**

| Harness | Custom subagents | Slash commands | Plugins | Headless | ACP |
|---|---|---|---|---|---|
| Claude Code | `.claude/agents/*.md`, up to 3 layers deep | Merged with skills; `.claude/commands` still works | `.claude-plugin/plugin.json` + marketplace | `claude -p`, `--output-format json\|stream-json`, `--json-schema`, `--resume`, `--bare` | Via `claude-agent-acp` adapter |
| VS Code Copilot | `.github/agents/*.agent.md`, `.claude/agents` | Skills and prompt files in the `/` menu; MCP prompts as `/<server>.<prompt>` | Agent Plugins 1.0, Copilot and Claude formats, legacy OpenPlugin | Not applicable | Consumes ACP only via third-party extensions |
| Copilot CLI | `.github/agents`, `~/.copilot/agents`, `--agent=` | [?] | Yes, including marketplaces | `copilot -p`, `-s`, `--allow-tool`, `--no-ask-user` | `copilot --acp` (public preview) |
| Codex CLI | **TOML** in `.codex/agents`, `~/.codex/agents` | `$skill`, `/skills` | Root `plugin.json`, or `.codex-plugin/plugin.json`; reads `.claude-plugin/marketplace.json` | `codex exec --json --output-schema`, `resume` | Via adapter |
| Cursor | `.cursor/agents`, `.claude/agents`, `.codex/agents`; 2 levels | `/skill`; commands via plugins | `.cursor-plugin/plugin.json`, or Agent Plugin | `agent -p --output-format`, `--force` | `agent acp` |
| Gemini CLI | `.gemini/agents/*.md`; **no nesting**; remote via A2A | TOML in `commands/` | `gemini-extension.json` | `-p`; JSON and JSONL output; exit codes 0/1/42/53 | Listed directly |
| Antigravity CLI | Claimed retained; details [?] | Commands convert to skills on import | `agy plugin` | `agy -p` [S] | **Conflicting** (see Gaps) |
| OpenCode | `.opencode/agents`; name comes from the filename; `mode` primary or subagent | `.opencode/commands/*.md` with `$ARGUMENTS`, `$1`, `` !`cmd` ``, `@file` | **JS/TS modules**, npm | `opencode serve` HTTP API; OpenAPI 3.1 | `opencode acp`; `/undo`, `/redo` unsupported |
| Cline | `spawn_agent`, **CLI and Desktop only**; no MCP tools inside subagents | `/` for skills; `workflows` [?] | `cline plugin install`; TS `AgentPlugin` | `cline --json`, stdin | `--acp` |
| Goose | `.agents/agents`, compat `.claude/agents`; recipes; autonomous mode only | [?] recipes instead | `.agents/plugins/<name>/` | [?] not verified | Listed directly; [?] command |
| Pi | **None built in**; `pi-subagents` package or `pi --print` [S] | `.pi/prompts`, `/skill:name` | Pi packages via npm or git | Print, JSON, RPC | Via `pi-acp` adapter |

*Sources by column*
- Subagents: [Claude](https://code.claude.com/docs/en/sub-agents), [VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents), [Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Cursor](https://cursor.com/docs/subagents), [Gemini](https://geminicli.com/docs/core/subagents/), [OpenCode](https://opencode.ai/docs/agents/), [Cline](https://docs.cline.bot/features/subagents), [Goose](https://goose-docs.ai/docs/guides/context-engineering/custom-agents), [Goose subagents](https://goose-docs.ai/docs/guides/subagents), [Pi README](https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/README.md), [eesel](https://www.eesel.ai/blog/pi-coding-agent)
- Plugins: [Claude](https://code.claude.com/docs/en/plugins-reference), [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-plugins), [Codex](https://developers.openai.com/codex/plugins/build), [Cursor](https://cursor.com/docs/plugins), [OpenCode](https://opencode.ai/docs/plugins/), [Cline](https://docs.cline.bot/sdk/plugins)
- Headless: [Claude](https://code.claude.com/docs/en/headless), [Copilot](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [Codex](https://learn.chatgpt.com/docs/non-interactive-mode), [Cursor](https://cursor.com/docs/cli/headless), [Gemini](https://geminicli.com/docs/cli/headless/), [Cline](https://docs.cline.bot/cli/cli-reference), [OpenCode](https://opencode.ai/docs/server/), [Pi](https://pi.dev/docs/latest)
- ACP: [agents list](https://agentclientprotocol.com/get-started/agents), [Copilot](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server), [Cursor](https://cursor.com/docs/cli/acp), [OpenCode](https://opencode.ai/docs/acp/)
- The Copilot ACP preview dates from [2026-01-28](https://github.blog/changelog/2026-01-28-acp-support-in-copilot-cli-is-now-in-public-preview/) **(stale?)**, though the current docs still say preview.

**Matrix C: MCP client features (does a server's request actually work?)**

| Host | Elicitation | Sampling | Roots | Prompts | Resources | Tasks | 2026-07-28 |
|---|---|---|---|---|---|---|---|
| Claude Code | Yes, form and URL | Not in the docs (I searched both fetched parts) [?] | Yes | Yes, as `/server:prompt` | Yes | Public beta, v2.1.304+ | Yes, on the v2 runtime |
| VS Code | [?] | Yes, via `chat.mcp.serverSampling` | [?] | Yes | Yes | [?] | [?] |
| Copilot CLI | [?] | [?] | [?] | [?] | [?] | [?] | [?] |
| Codex | Not on page [?] | Not on page [?] | [?] | [?] | [?] | [?] | [?] |
| Cursor | Yes | Not listed | Yes | Yes | Yes | [?] | [?] |
| OpenCode | Listed in a third-party matrix [S] | [?] | [?] | [?] | [?] | [?] | [?] |
| Cline | No documentation found [?] | Request-stage only [S] | [?] | [?] | [?] | [?] | [?] |
| Goose | Listed [S] | Yes, on by default [S] (Dec 2025 **stale?**) | Listed [S] | Listed [S] | Listed [S] | [?] | [?] |
| Pi | [?] | [?] | [?] | [?] | [?] | [?] | [?] |

*Sources*: [Claude MCP](https://code.claude.com/docs/en/mcp), [VS Code config](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [VS Code MCP](https://code.visualstudio.com/docs/copilot/customization/mcp-servers), [Cursor MCP](https://cursor.com/docs/mcp), [third-party matrix](https://www.developersdigest.tech/mcp-servers/clients), [goose sampling](https://goose-docs.ai/docs/guides/mcp-sampling), [gateway guide](https://zuplo.com/docs/mcp-gateway/connect-clients/other-clients.md)

### Inferences
- Reach: `.agents/skills` plus `.claude/skills` at project level covers all nine harnesses per their docs. Claude Code and Cline need `.claude/skills`; Codex, Gemini, and Pi need `.agents/skills`.
- At user level, three locations are needed: `~/.agents/skills`, `~/.claude/skills`, and `~/.cline/skills`.
- Hosts reading both project directories (VS Code, Copilot CLI, Cursor, OpenCode, Goose) may show duplicates. This needs testing.

### Gaps
- [?] I found no current, authoritative per-host MCP capability table. The old `/clients` page now serves the homepage, so Matrix C has many unknowns.
- [?] No source states whether Copilot, Codex, Cursor, or the others implement MRTR. Only Claude Code documents 2026-07-28 support. The practical effect is that a server cannot assume MRTR works across hosts.
- [?] Antigravity CLI ACP: a [PR](https://github.com/openabdev/openab/pull/863) claims `agy --acp`, while a [Google forum post](https://discuss.ai.google.dev/t/ux-issues-and-lack-of-acp-support-in-antigravity-cli/169445) says there is no ACP support.
- [?] Cline's skill path conflicts: its docs omit `.agents/skills`, while the [Vercel table](https://raw.githubusercontent.com/vercel-labs/skills/main/docs/agents.md) installs there. Trust Cline's docs until tested.
- [?] Cline subagent docs conflict: [docs.cline.bot](https://docs.cline.bot/features/subagents) versus an older [repo file](https://github.com/cline/cline/blob/main/docs/features/subagents.mdx).
- [?] Claude Code's fetched skills docs never mention `.agents/skills`. Absence of mention is not proof of absence.

---

## 3. Hooks: events, names, and payload differences

### Takeaway
Claude's format is the de facto source format: Copilot, Cursor, and Codex accept it or resemble it. Compatibility is still partial, though, and VS Code warns outright that sharing a hook file does not make hooks compatible. Three hosts need code rather than JSON: OpenCode, Pi, and the Cline SDK.

### Cited Findings

| Harness | Events | Payload style | How to deny a tool call | Injecting context | Handler types |
|---|---|---|---|---|---|
| Claude Code | **33** events, including `PreToolUse`, `PostToolBatch`, `PreCompact`, `PostCompact`, `Elicitation` | `session_id`, `tool_name`, `tool_input`, `transcript_path`, `cwd` | `hookSpecificOutput.permissionDecision: "deny"`, or exit 2 | `additionalContext`; 10,000-character cap | command, http, mcp_tool, prompt, agent |
| Copilot CLI | 13 native events (`preToolUse`, `agentStop`, `preCompact`, and others) | **camelCase** native (`toolName`, `toolArgs`); PascalCase alias gives snake_case | Top-level `permissionDecision: "deny"`; exit 2 or any non-zero | `additionalContext` on sessionStart, subagentStart, postToolUse, others | command, exec (CLI only), http |
| VS Code | Copilot-harness subset; **Preview** | Same split | `permissionDecision` | `postToolUse` `additionalContext`; `userPromptSubmitted` output ignored | Command |
| Codex | 12 events, including `Interrupt`, `PreCompact`, `PostCompact` | snake_case, plus `turn_id` and `model` | `hookSpecificOutput`, legacy `decision: "block"`, or exit 2; **`ask` not supported** | `additionalContext` | **command and mcp_tool run; prompt and agent are parsed but skipped** |
| Cursor | 18 agent, 2 Tab, 1 app event | `conversation_id`, `generation_id`, `workspace_roots` | `permission: "deny"` (flat), exit 2 | `additional_context` on postToolUse and sessionStart | Command; prompt on non-cloud |
| Gemini CLI | 11, including `BeforeModel`, `BeforeToolSelection`, `AfterModel`, `PreCompress` | snake_case common fields; `mcp_<server>_<tool>` | `decision`, or exit 2 | `hookSpecificOutput` | **command only** |
| OpenCode | JS events: `tool.execute.before`, `session.idle`, others | JS objects | **Throw an error** | `experimental.session.compacting` context; no general hook verified | Code |
| Cline | `.cline/hooks/`; `PreToolUse` named; SDK: `beforeRun`, `beforeModel`, `beforeTool`, others | [?] file contract undocumented on fetched pages | Can cancel `run_commands` [S] | [?] | File hooks and TS plugins |
| Goose | 12; **plugins only**, `hooks/hooks.json`; no Subagent events | `event`, `session_id`, `matcher_context`, `working_dir` | `{"decision":"block"}` or exit 2 | **None**: only `PreToolUse` and `Stop` can act; the rest only observe | Command |
| Pi | 40+ TS events | JS objects | `tool_call` handler | `before_agent_start` can add a message and change the system prompt; `context` filters messages | Code |

*Sources*: [Claude](https://code.claude.com/docs/en/hooks), [Copilot](https://docs.github.com/en/copilot/reference/hooks-configuration), [VS Code](https://code.visualstudio.com/docs/copilot/customization/hooks), [Codex](https://learn.chatgpt.com/docs/hooks), [Cursor](https://cursor.com/docs/hooks), [Gemini](https://geminicli.com/docs/hooks/reference/), [OpenCode](https://opencode.ai/docs/plugins/), [Cline CLI](https://docs.cline.bot/cli/cli-reference), [Cline SDK](https://docs.cline.bot/sdk/plugins), [Goose](https://goose-docs.ai/docs/guides/context-engineering/hooks/), [Pi](https://pi.dev/docs/latest/extensions)

**Compatibility shims that exist**
- [P] Copilot CLI and VS Code read repo `.claude/settings.json` and `.claude/settings.local.json`. PascalCase events report Claude tool names (`Bash`, `Read`). Native payloads report `bash`, `view`, `create`. — [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration)
- [P] Cursor loads `.claude/settings.local.json`, `.claude/settings.json`, and `~/.claude/settings.json`, with 8 event mappings. It maps `Bash` to `Shell` and `Edit` to `Write`, has no equivalent for `Glob`, and does not support `Notification` or `PermissionRequest`. — [Third-party hooks](https://cursor.com/docs/reference/third-party-hooks)
- [P] Codex sets `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` so Claude-style plugin hooks can run. — [Codex plugins](https://developers.openai.com/codex/plugins/build)

**Traps**
- [P] Goose: a bare `"*"` matcher is an invalid regex and **the whole rule is silently skipped**. Use `".*"`. — [Goose hooks](https://goose-docs.ai/docs/guides/context-engineering/hooks/)
- [P] Failure defaults differ. Copilot timeouts fail open everywhere, but `preToolUse` errors deny. — [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration)
  - Cursor fails open unless `failClosed: true`, but invalid JSON on permission hooks blocks. — [Cursor hooks](https://cursor.com/docs/hooks)
  - Goose fails open unless `on_failure: block`. — [Goose hooks](https://goose-docs.ai/docs/guides/context-engineering/hooks/)
- [P] `ask` varies. Copilot treats it as `deny` in cloud and autopilot, and Cursor ignores it on `preToolUse`. — [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration), [Cursor hooks](https://cursor.com/docs/hooks)
- [P] Exit 2 means block on Claude, Codex, and Cursor. On Copilot it is a warning for most events. — [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration)
- [P] Codex project hooks need a trusted `.codex/` layer and hash-based review through `/hooks`. Hosted tools such as `WebSearch` are not intercepted, and the docs call hooks "a useful guardrail, not a complete enforcement boundary". — [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [P] A `claude -p` session runs a project's hooks and connects its `.mcp.json` servers with no trust dialog. — [Headless](https://code.claude.com/docs/en/headless)

### Inferences
- A hook adapter needs an internal event model of about six events: session start, prompt, pre-tool, post-tool, stop, pre-compact. It also needs per-host tool name maps and fail-open or fail-closed rules.
- Generated Codex hooks need re-approval whenever their content changes, because trust is hash-based. Keep the hook itself stable and put logic in the script or server it calls. Whether a script change alone preserves trust is untested.
- Claude-only hook features (`updatedToolOutput`, `mcp_tool`, `PostToolBatch`) should be treated as optional enhancements.

### Gaps
- [?] Cline's file-hook JSON contract: both [docs stubs](https://docs.cline.bot/customization/hooks) point at the SDK page.
- [?] Antigravity hook location. [Google's plugin docs](https://www.antigravity.google/docs/cli/plugins) reference settings.json, while a [third-party doc](https://docs.rs/crate/agent-config/0.3.0/source/docs/agents/antigravitycli.md) gives `~/.gemini/antigravity-cli/hooks.json` and an [older crate comment](https://docs.rs/crate/agentgear/latest/source/src/agents/antigravity_cli.rs) gives `~/.gemini/config/hooks.json`.

---

## 4. File locations, frontmatter, and what breaks when moving

### Takeaway
A skill limited to `name`, `description`, and body text moves cleanly. Claude-specific frontmatter is mostly ignored silently elsewhere, which is worse than an error because behaviour simply changes. Subagents do not port without conversion, because Codex uses TOML and the permission models differ.

### Cited Findings

**Skill frontmatter beyond the standard**

| Field | Claude | VS Code | Cursor | Pi | Codex | OpenCode |
|---|---|---|---|---|---|---|
| `name` required, matches dir | Optional, defaults to dir | Required; bad names **fail silently** | Required | Mismatch not warned | Required | Required |
| `disable-model-invocation` | Yes | Yes | Yes | Yes | No: use `agents/openai.yaml` `allow_implicit_invocation` | Ignored |
| `user-invocable` | Yes | Yes | [?] | [?] | [?] | Ignored |
| `argument-hint` | Yes | Yes | [?] | [?] | [?] | Ignored |
| `context: fork` | Yes | Experimental, needs a setting | [?] | [?] | [?] | Ignored |
| `paths` | Yes | [?] | Yes | [?] | [?] | Ignored |
| `allowed-tools` | Yes | [?] | [?] | Experimental | [?] | Ignored |
| `hooks`, `model`, `agent`, `effort` | Yes | [?] | [?] | [?] | [?] | Ignored |

*Sources*: [Claude](https://code.claude.com/docs/en/skills), [VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [Cursor](https://cursor.com/docs/skills), [Pi](https://pi.dev/docs/latest/skills), [Codex](https://learn.chatgpt.com/docs/build-skills), [OpenCode](https://opencode.ai/docs/skills/)

**Subagent format**

| Harness | Format | Required | Tool restriction | Notable fields |
|---|---|---|---|---|
| Claude | MD + YAML | `name`, `description` | `tools`, `disallowedTools` | `permissionMode`, `skills`, `mcpServers`, `hooks`, `memory`, `isolation` |
| Copilot | `.agent.md` | [?] | `tools` | `handoffs`, `target`, `hooks` |
| Codex | **TOML** | `name`, `description`, `developer_instructions` | `features.shell_tool` | Inherits parent sandbox and MCP; cannot override |
| Cursor | MD + YAML | None | `readonly` only | `is_background` |
| Gemini | MD + YAML | `name`, `description` | `tools` YAML list | `kind`, `temperature`, `max_turns`, `timeout_mins` |
| OpenCode | MD + YAML | `description` | `permission` map | `mode`, `steps`; name from filename |
| Goose | MD + YAML | `name` | None documented | `model` |

*Sources*: [Claude](https://code.claude.com/docs/en/sub-agents), [Copilot](https://code.visualstudio.com/docs/copilot/customization/custom-agents), [Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Cursor](https://cursor.com/docs/subagents), [Gemini](https://geminicli.com/docs/core/subagents/), [OpenCode](https://opencode.ai/docs/agents/), [Goose](https://goose-docs.ai/docs/guides/context-engineering/custom-agents)

**What breaks**
1. [P] Claude Code silently ignores AGENTS.md when any CLAUDE.md exists at or above cwd, unless the setting is changed or `@AGENTS.md` is imported. — [Memory](https://code.claude.com/docs/en/memory)
2. [P] Claude-only variables such as `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` will not resolve as intended elsewhere. — [Claude skills](https://code.claude.com/docs/en/skills)
   - Cursor uses `${CURSOR_PLUGIN_ROOT}`, and Agent Plugins use `${PLUGIN_ROOT}`. — [Cursor plugins](https://cursor.com/docs/plugins), [Spec](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)
3. [P] Precedence flips across hosts. Claude: personal beats project. Cline: **global beats project**. Gemini and Copilot CLI: project beats user. — [Claude](https://code.claude.com/docs/en/skills), [Cline](https://docs.cline.bot/customization/skills), [Gemini](https://geminicli.com/docs/cli/skills/), [Copilot](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
4. [P] Same-name collisions behave differently. Codex shows both, Pi keeps the first and warns. — [Codex](https://learn.chatgpt.com/docs/build-skills), [Pi](https://pi.dev/docs/latest/skills)
5. [P] Skill listing budgets differ: Claude 1% of the context window, Codex 2% (or 8,000 characters). Claude's combined description cap of 1,536 characters exceeds the standard's 1,024. — [Claude](https://code.claude.com/docs/en/skills), [Codex](https://learn.chatgpt.com/docs/build-skills)
6. [P] Claude compaction can keep only the start of an invoked skill, so put key instructions near the top. — [Claude skills](https://code.claude.com/docs/en/skills)
7. [P] MCP config differs in shape: `mcpServers`, `servers`, TOML tables, `serverUrl`. Transport names also differ (`http`, `local`, `streamable-http`). — [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers), [Antigravity](https://antigravity.google/docs/cli/gcli-migration), [Codex](https://developers.openai.com/codex/plugins/build)
8. [P] Instruction imports are not portable. `@path` works in Claude, and Goose has `@filename`, but OpenCode does not auto-parse references. — [Memory](https://code.claude.com/docs/en/memory), [Goose](https://goose-docs.ai/docs/guides/context-engineering/using-goosehints), [OpenCode](https://opencode.ai/docs/rules/)
9. [P] OpenCode passes unknown agent keys through to the provider as model options. — [OpenCode](https://opencode.ai/docs/agents/)
10. [P] Claude ignores `hooks`, `mcpServers`, and `permissionMode` on plugin subagents. — [Claude](https://code.claude.com/docs/en/sub-agents)
11. [P] Copilot's VS Code picker settings do not reach the CLI, so use native folders. — [VS Code agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
12. [P] Antigravity import skips what it cannot convert; workspace skills must move to `.agents/skills`, or they will not appear as slash commands. — [Migration](https://antigravity.google/docs/cli/gcli-migration)

### Inferences
- The body of each skill also needs adapting. Text like "use the Bash tool" assumes Claude's tool names. gstack and Superpowers both solve this (see Section 5).
- Write skills against the standard plus a small "capabilities needed" note, then let the generator add host-specific frontmatter. Do not start from Claude's rich format and strip it down.
- Cursor lists `.codex/agents` but describes Markdown files, while Codex uses TOML. Whether Cursor parses those files is unknown.

### Gaps
- [?] Many frontmatter cells above; these need a test run per host, because docs omit ignored fields.

---

## 5. Existing cross-harness projects

### Takeaway
Three working patterns exist: compile one source into per-host files, ship per-host packaging around shared skills, and manage dependencies with a lockfile. The more mature projects all concede that parity is impossible and say so openly, using tiers.

### Cited Findings

| Project | Pattern | How adapters work | Strength | Weakness |
|---|---|---|---|---|
| [rulesync](https://github.com/dyoshikawa/rulesync) | Compiler | `.rulesync/` to tool files; `import` and `convert` | Widest scope: rules, ignore, MCP, commands, subagents, skills, hooks, permissions | Per-tool coverage varies; [table](https://rulesync.dyoshikawa.com/reference/supported-tools) omits Gemini CLI |
| [Ruler](https://github.com/intellectronica/ruler) | Compiler | `.ruler/` concatenated; `ruler.toml` for MCP | Simple; about 30 agents | "Beta Research Preview"; same rules for all; no hooks mentioned; subagents experimental |
| [Vercel skills](https://github.com/vercel-labs/skills) | Installer | `npx skills add -a <agent>`; 75+ agents; [paths](https://raw.githubusercontent.com/vercel-labs/skills/main/docs/agents.md) | Largest skill ecosystem; 37.6k stars | Skills only; telemetry on by default |
| [dotagents](https://github.com/getsentry/dotagents) (Sentry) | Dependency manager | `agents.toml`, `agents.lock`, symlinks from `.agents/skills`; writes MCP and hook files | Closest to this brief, with a user-global mode | Small (260 stars); support varies; no Codex hooks entry |
| [APM](https://github.com/microsoft/apm) (Microsoft) | Dependency manager | `apm.yml`, lockfile; `apm compile` | All primitives; targets 9 harnesses | No maturity label; compile documented only for Copilot |
| [Superpowers](https://github.com/obra/superpowers) | Per-host packaging | One skills tree plus `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `.opencode`, `gemini-extension.json`, `.pi/extensions` | 16 harnesses; bootstrap skill injected at session start | Depends on a start hook; Hermes loses bootstrap after compaction |
| [gstack](https://github.com/garrytan/gstack) | Template generator | Typed [`HostConfig`](https://raw.githubusercontent.com/garrytan/gstack/main/docs/ADDING_A_HOST.md): frontmatter allowlist, path rewrites, tool rewrites, capability tiers | **Best-documented adapter model**; honest tiers | Safety hooks enforced only on Claude Code |
| [ECC](https://github.com/affaan-m/everything-claude-code) | Per-host packaging | Per-host dirs; profile-gated hooks | Very broad; v2.2.3 | Self-described "full Claude feature parity is not claimed"; Copilot CLI gets no hooks |
| [Spec Kit](https://github.com/github/spec-kit) | Scaffolder | `--integration <key>`; [formats](https://github.github.com/spec-kit/reference/integrations.html) markdown, skills, toml, yaml | About 40 keys [S]; provenance tracking | Invocation prefix varies (`/speckit-`, `$speckit-`, `/skill:speckit-`) |
| [GSD Core](https://github.com/open-gsd/gsd-core) | Installer | Installer converts per runtime; direct copy warned against | "The installer is required for cross-runtime compatibility" | [Original repo](https://github.com/gsd-build/get-shit-done) archived; conversion details not retrieved |
| [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) | Skills + plugins | v7 alpha uses `npx skills add`, plus Claude and Codex plugins | Moved onto shared skills infrastructure | v7 target mid-November 2026, breaking changes expected |
| [OpenSkills](https://github.com/numman-ali/openskills) | Runtime shim | Writes an XML block into AGENTS.md; agents run `openskills read <name>` | Works on a host with no skill support | Relies on the model following it; largely superseded |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | CLI + skill | CLI as the tool; `skills get` matches the installed version; optional `mcp` mode | Version-locked instructions; no host dependency | Rationale for CLI over MCP is not stated on the page |
| [acpx](https://github.com/openclaw/acpx) | ACP client | One command shape over 30 agent profiles; persistent sessions in `~/.acpx/` | Drives harnesses from outside | Pre-1.0 |

**Other findings**
- [P] Superpowers uses a "Platform Adaptation" section: the skill tells the agent to read a per-harness reference file, such as `codex-tools.md` or `pi-tools.md`. — [SKILL.md](https://raw.githubusercontent.com/obra/superpowers/main/skills/using-superpowers/SKILL.md)
- [S] "Karpathy-style" setups are plain folders rather than infrastructure: a CLAUDE.md or AGENTS.md of behavioural rules plus an LLM-maintained markdown wiki. Sources disagree on which repo is canonical. — [Medium](https://medium.com/neuralnotions/andrej-karpathy-stopped-using-ai-to-write-code-hes-using-it-to-build-a-second-brain-instead-cddceadc5df5), [mindstudio](https://mindstudio.ai/blog/andrej-karpathy-llm-wiki-knowledge-base-claude-code)
- [S] ECC warns that running in both Claude Code and Cursor on one machine needs separate data directories. — [Augment](https://www.augmentcode.com/learn/ecc-224k-stars-cross-harness-agent-config)

### Inferences
- The strongest reusable ideas:
  - gstack's `HostConfig` and tiers.
  - Superpowers' per-host reference files and its session-start bootstrap.
  - dotagents' symlinks and lockfile.
  - agent-browser's CLI that serves its own instructions.
- Common weakness: all of them handle content well, and enforcement poorly. None has a uniform safety hook story outside Claude Code.
- Adopting an existing generator may beat writing one. dotagents or rulesync are the first to evaluate.

### Gaps
- [?] Star counts and activity are point-in-time, and release dates were often not visible on captured pages.
- [?] GSD Core's conversion logic, and BMAD's supported tool list, were not retrieved.
- [?] claude-mem or other cross-host memory servers were not verified. One [issue](https://github.com/thedotmack/claude-mem/issues/1826) shows it affected by the April billing change.

---

## 6. SDK route, licences, and subscription limits

### Takeaway
Embedding gets you full control of the loop, but you own the product surface and are bound to one vendor per SDK. Most vendor SDKs are thin clients around the vendor's CLI, so they do not escape that vendor. For personal use, the safest path is the vendor's unmodified binary signed in with your own account. Google is the clearest prohibition.

### Cited Findings

**SDKs**

| SDK | Model | Status | Licence / terms | Auth |
|---|---|---|---|---|
| [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) | Runs the Claude Code binary; Python and TS | Current | Anthropic Commercial Terms | API key for products; see below |
| [Copilot SDK](https://github.com/github/copilot-sdk) | JSON-RPC to Copilot CLI; 6 official languages | GA | MIT | Subscription or BYOK |
| [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) | TS `@openai/codex-sdk`; Python via app-server JSON-RPC | Python [experimental](https://developers.openai.com/codex/sdk.md) [S] | Open source app-server | Signed-in account; details not stated |
| [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/sandbox_agents/) | Library with sandbox agents, skills, compaction | Current | [?] | [?] |
| [Cursor SDK](https://cursor.com/docs/sdk/typescript) | Local or cloud agents; `@cursor/sdk` | Public beta [S] | [?] | `CURSOR_API_KEY` |
| [Pi SDK](https://pi.dev/docs/latest/sdk) | In-process `createAgentSession`; also RPC | v1.0 line | [MIT](https://www.eesel.ai/blog/pi-coding-agent) [S] | Provider keys and logins |
| [OpenCode server](https://opencode.ai/docs/server/) | HTTP + SSE; OpenAPI 3.1; port 4096 | Current | [?] page does not state it | Provider credentials |
| [Cline](https://github.com/cline/cline) | Offered as SDK, IDE extension, or CLI | [?] | [?] | [?] |

- [P] Codex removed `codex mcp-server`, pointing integrations to the app-server. — [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)
- [P] What SDKs add over config: Pi can filter context, rewrite provider payloads, and replace compaction. — [Pi extensions](https://pi.dev/docs/latest/extensions)
- [P] What they do not add: Copilot SDK's `userPromptSubmitted.modifiedPrompt` is SDK-only, which is a rare case of SDK-only power on a vendor CLI. — [Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-configuration)

**Gateways**
- [P] LiteLLM can front Claude Code through `ANTHROPIC_BASE_URL`, with exact-match model names and Bedrock workarounds labelled temporary. — [LiteLLM](https://docs.litellm.ai/docs/tutorials/claude_responses_api)
- [P] LiteLLM's page says tool search is off with a non-Anthropic base URL, but Claude's own docs say it is on by default for gateways, with retry logic on v2.1.305+. Claude's docs are the more authoritative. — [Claude MCP](https://code.claude.com/docs/en/mcp)
- [S] LiteLLM 1.82.7 and 1.82.8 on PyPI were compromised on 2026-03-24 with credential-stealing code. — [bastion](https://bastion.tech/blog/litellm-pypi-supply-chain-attack), [pypistats](https://pypistats.com/blog/litellm-pypi-supply-chain-compromise-how-a-popular-llm-proxy-became-a-credential-stealing-backdoor-march-24-2026)

**Subscription policy**

*Anthropic*
- [P] OAuth is "intended exclusively for" plan purchasers and supports ordinary use of Claude Code and native Anthropic apps. — [Legal](https://code.claude.com/docs/en/legal-and-compliance)
- [P] Third-party developers may not offer Claude.ai login or route requests through plan credentials on behalf of their users. — [Legal](https://code.claude.com/docs/en/legal-and-compliance)
- [P] It does not prevent an end user signing in to the **unmodified Claude Code binary** with their own subscription. — [Legal](https://code.claude.com/docs/en/legal-and-compliance)
- [P] Anthropic may enforce "without prior notice". — [Legal](https://code.claude.com/docs/en/legal-and-compliance)
- [P] Timeline primary evidence: changes to Agent SDK usage were paused on 2026-06-15, and from 2026-10-07 Max, Ultra, and Team include monthly API credits covering the SDK and `claude -p` **when run with an API key**. Signed-in plan use and third-party app usage still draw from subscription limits. — [Support](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [S] Earlier timeline: terms tightened 2026-02-20, third-party OAuth cut off 2026-04-04, reversal 2026-05-13. The May date rests on one source with no primary link. — [BetterClaw](https://www.betterclaw.io/blog/openclaw-anthropic-subscription-ban)
- [P] OpenCode states "Anthropic explicitly prohibits this" and stopped bundling Claude Pro/Max plugins as of 1.3.0. — [OpenCode providers](https://opencode.ai/docs/providers/)
- [S] Pi's changelog warns Claude subscription use is billed as extra usage. — [eesel](https://www.eesel.ai/blog/pi-coding-agent)
- [S] Users report conflicting results after a June 16 email said third-party usage continued as before. — [Hermes issue](https://github.com/NousResearch/hermes-agent/issues/47260)
- [P] **Trap**: `--bare` never reads OAuth credentials and "will become the default for `-p` in a future release". — [Headless](https://code.claude.com/docs/en/headless)
- The fetched consumer terms (effective 2025-10-08) do not mention OAuth tokens. — [Terms](https://www.anthropic.com/legal/consumer-terms)
  - This conflicts with secondary claims that the terms were updated in February 2026 and quote OAuth wording. The operative text I could verify is on the Claude Code legal page.

*OpenAI*
- [P] OpenCode offers native ChatGPT Plus/Pro login. — [OpenCode](https://opencode.ai/docs/providers/)
  - This contradicts a [Bito FAQ](https://bito.ai/ai-tools/opencode-vs-codex/) saying it needs a community plugin.
- [S] Personal third-party use is tolerated in practice as of August 2026. — [aq.dev](https://aq.dev/guides/coding-harness-ban-risk/)
- [P] OpenAI's auth page contains no third-party restriction, recommends API keys for automation, and documents copying `auth.json` to headless machines. — [Codex auth](https://learn.chatgpt.com/docs/auth)

*Google*
- [S] Terms reportedly name "using OpenClaw with Antigravity OAuth" as a violation that may lead to suspension. On 2026-02-27 **(stale?)** Google reinstated restricted accounts but repeated that third-party use breaks its terms. — [Google forum](https://discuss.ai.google.dev/t/account-disabled-403-tos-after-unknowingly-using-openclaw-new-subscriber-seeking-account-restoration/125862), [VentureBeat](https://venturebeat.com/ai/google-clamps-down-on-antigravity-malicious-usage-cutting-off-openclaw-users)
- [S] Pi removed Gemini CLI and Antigravity logins in 0.71.0 (2026-04-30). — [eesel](https://www.eesel.ai/blog/pi-coding-agent)

*GitHub*
- [P] All plans moved to usage-based AI Credits on 2026-06-01, with Pro and Pro+ including $10 and $39. Third-party sources give different figures; use GitHub's. — [GitHub](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)
- [P] OpenCode supports Copilot login through a device flow. — [OpenCode](https://opencode.ai/docs/providers/)
- [P] Local Codex in VS Code needs a Copilot Pro+ subscription and the Codex extension. — [VS Code third-party agents](https://code.visualstudio.com/learn/agents/4-using-third-party-agents-in-vs-code)

### Inferences
- A personal layer that launches the real `claude`, `codex`, or `copilot` binaries is the lowest-risk route on auth. It stays within the "unmodified binary" language.
- Using the Agent SDK signed in with your own plan seems contemplated by the support article, but the docs steer developers to API keys. Treat this as unclear, not safe. Anything distributed to others should use API keys.
- A layer calling `claude -p` should pin behaviour now, because the `--bare` default change would drop both subscription login and all auto-discovered config.

### Gaps
- [?] No primary Anthropic announcement found for the April or May events.
- [?] No primary OpenAI or GitHub policy text found on third-party harness use of subscriptions. This needs direct review of their terms.
- [?] Current Antigravity terms were not read directly.
- [?] OpenRouter's integration with Claude Code was not verified.
- [?] Legal interpretation here is my reading, not legal advice.

---

## 7. Architecture options

### Takeaway
A hybrid is the best fit: a content layer with an adapter generator, a local MCP server for memory and search, and thin per-host hook shims. Keep an own-loop SDK only for headless jobs. MCP alone cannot do it, and Sampling should not be part of the design.

### Cited Findings

**What an MCP server cannot do alone**
- [P] The ACP RFD states the limit directly: MCP servers sit behind the agent and cannot inject prompts, add persistent global context, transform responses, or coordinate multiple agents. — [Proxy chains](https://agentclientprotocol.com/rfds/proxy-chains)
- [P] Sampling is deprecated, with direct provider integration as the migration. — [Deprecated registry](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
- [P] Roots is also deprecated; the migration is to pass directories via tool parameters, URIs, or server config. — [Deprecated registry](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
- [P] Server state must become explicit handles passed through the model. — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [P] Server instructions are the one always-loaded channel, cut at 4,096 characters by default on Claude Code. — [Claude MCP](https://code.claude.com/docs/en/mcp)
- [P] Claude Code channels allow server push, but they are host-specific and opt-in with `--channels`, and channel servers negotiating 2026-07-28 are not registered as channels on the v2 runtime. — [Claude MCP](https://code.claude.com/docs/en/mcp)

**Features needing host cooperation**

| Capability | Mechanism | Hosts with documented support | MCP alone? |
|---|---|---|---|
| Inject context at session start | Hook | Claude, Copilot, Cursor, Pi; Goose **cannot** (observe only) | No |
| Inject per turn | Hook | Claude, Codex, Pi | No |
| Block or rewrite tool calls | Hook | Claude, Copilot, Codex, Cursor, Pi, OpenCode; Goose block only | Own tools only |
| Rewrite tool output | Hook | Claude, Copilot, Cursor (MCP only), Pi | Own tools only |
| Compaction control | Hook | Full: Pi (cancel or custom summary). Prompt: OpenCode (experimental). Block: Claude. **Cursor cannot block.** | No |
| Re-inject after compaction | Hook | Claude, Codex (`PostCompact`, `SessionStart` compact matcher), Pi | No |
| Spawn host subagents | Host tool | Host only | No; can launch a separate process |
| System prompt | Config or code | Pi `SYSTEM.md`; Claude `--system-prompt` in headless mode | No |
| User questions mid-task | Elicitation | Claude, Cursor; others [?] | Yes, where supported |
| Long-running work | Tasks | Claude beta; others [?] | Partly |
| Skills from server | Skills extension | ChatGPT partial; others [?] | Future path |

*Sources*: [Claude hooks](https://code.claude.com/docs/en/hooks), [Copilot](https://docs.github.com/en/copilot/reference/hooks-configuration), [Codex](https://learn.chatgpt.com/docs/hooks), [Cursor](https://cursor.com/docs/hooks), [Pi](https://pi.dev/docs/latest/extensions), [OpenCode](https://opencode.ai/docs/plugins/), [Goose](https://goose-docs.ai/docs/guides/context-engineering/hooks/), [matrix](https://modelcontextprotocol.io/extensions/client-matrix)

- [P] A useful bridge: Claude and Codex hooks both offer an `mcp_tool` handler that calls an MCP server directly. Claude and Copilot also support `http` hooks. — [Claude](https://code.claude.com/docs/en/hooks), [Codex](https://learn.chatgpt.com/docs/hooks), [Copilot](https://docs.github.com/en/copilot/reference/hooks-configuration)

**Option comparison (my analysis, built on the findings above)**

| Option | You keep | You lose | Effort | Lock-in |
|---|---|---|---|---|
| **(a) Content layer + generator** | Host UX, auth, updates, subagents | Enforcement, memory across hosts, uniform behaviour; skills are advisory | Low | Low |
| **(b) MCP brain** | Shared memory and search across every host | No injection or interception; relies on the model choosing to call tools; sampling unavailable | Medium | Low |
| **(c) Own loop on SDK** | Full control of context, compaction, tools | Host UI and integrations; maintenance; subscription access may be limited; a vendor SDK ties you to one vendor | High | Depends on SDK |
| **(d) Hybrid** | Most of the above | Parity: each host lands in a tier | Medium | Low |

**Recommended hybrid shape**
1. **Canonical source repo**: AGENTS.md, standard-only skills, one MCP registration, and a declarative hook policy.
2. **Generator**: emits per-host files, symlinks `.agents/skills` and `.claude/skills`, and renders tool-name reference files. Consider dotagents or rulesync first. Follow gstack's `HostConfig` model if you build your own.
3. **Local MCP server**: memory and search, with explicit handles, and paths passed as parameters. Avoid Sampling, Roots, and server-initiated requests. Expose the same functions through a CLI, following agent-browser's pattern, so hooks and hosts with a weak MCP story can reach it.
4. **Thin hook shims**: one normalised script per host calling the same local service, for session-start context, pre-tool policy, and pre-compact saving.
5. **Capability tiers**: Full (Claude Code, likely Codex and Copilot CLI, Cursor), Partial (Gemini, Antigravity, OpenCode, Cline), and Content-only or code-adapter hosts as needed. Pi and OpenCode need small TS plugins rather than JSON, but give stronger control.
6. **Optional orchestrator**: use ACP (acpx) or headless CLIs to delegate between harnesses. Use Pi's SDK if you ever need a fully owned loop. Pi is the strongest fit: MIT [S], multi-provider, deep hooks.

Packaging via Agent Plugins 1.0 suits the skills and MCP part. Claude Code still needs its own plugin wrapper, and hooks and agents stay client-specific.

### Inferences
- Start with Claude Code, one of Codex or Copilot CLI, and one more host, instead of all nine. Most of the adapter risk shows up by the second host.
- Memory is the piece that justifies the layer. Skills already travel well without you, so the MCP server is where original work pays off.
- ACP proxies could one day provide portable injection, but the RFD is a draft and proxies only work when a client drives the session. They do not help in a host's own terminal UI.
- Delegating through a separate process loses shared context and bills separately, unlike a host subagent.
- Keep the MCP server on stdio locally. Stateless HTTP changes mostly affect remote deployments, but confirm your SDK version handles both old and new protocol revisions, because hosts will lag.

### Gaps
- [?] Whether each host's hook can inject context after compaction needs testing. Codex's matchers suggest it, but its output fields per event are not fully listed.
- [?] Real-world reliability of "model chooses to call the memory tool" versus hook injection. I found no measured comparison.
- [?] Client adoption of MRTR, Tasks, and Skills over MCP. Re-check the matrix before relying on any of them.
- [?] Generator and hook behaviour on Windows was not researched, beyond gstack's symlink note.

---

## Top sources to re-check first, since they change fastest
- [MCP extension matrix](https://modelcontextprotocol.io/extensions/client-matrix)
- [Claude headless `--bare` note](https://code.claude.com/docs/en/headless)
- [Anthropic Agent SDK plan article](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [Agent Plugins spec repo](https://github.com/agentplugins/agent-plugins-spec)
- [ACP v2 RFD](https://agentclientprotocol.com/rfds/v2/overview)
- [Antigravity CLI migration](https://antigravity.google/docs/cli/gcli-migration)
