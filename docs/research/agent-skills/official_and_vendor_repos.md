# Official and vendor agent skill repositories, and the Agent Skills format

Retrieval: all star counts, licences and dates come from live `gh api` calls on 2026-11-01 local time (first call 2026-11-02T01:50Z). Stars moved slightly during the session (anthropics/skills went from 186,381 to 186,386). "SKILL.md count" means files named SKILL.md in the default branch tree, so it can include templates, fixtures and duplicates. Repository content was read through the API only. Nothing was cloned or run.

## Which official and vendor repositories exist, and what state are they in?

### Takeaway
The first-party landscape has moved since most blog posts were written. Anthropic's plugins now live in `anthropics/claude-plugins-official`, `anthropics/claude-code/plugins` holds only a README, and `openai/skills` is deprecated in favour of `openai/plugins`. The sources most useful to Puck are `anthropics/skills`, `anthropics/k12-teacher-skills`, `anthropics/knowledge-work-plugins`, `anthropics/claude-plugins-official`, `getsentry/skills` and the agentskills.io docs. Most other vendor repos only teach their own product.

### Cited Findings

Repos with a full tree inspected. "Last commit" is the latest commit on the default branch. "Licence" is GitHub's `license.spdx_id`.

| Repo | Stars | Licence | Last commit | SKILL.md count | Contents |
|---|---|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 186,381 | none at root (per-skill) | 2026-10-28 | 20 (19 skills + `template/`) | Example skills, document skills, skill-creator; `spec/agent-skills-spec.md` is now only a pointer to agentskills.io |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 45,725 | Apache-2.0 | 2026-10-30 | 33 | 40 internal plugins plus 14 external; much of the value is in agents and commands rather than SKILL.md files |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 154,176 | none reported | 2026-10-31 | 0 | `plugins/` now contains only `README.md` |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 34,371 | Apache-2.0 | 2026-10-28 | 252 | Role plugins for Cowork: engineering, product, enterprise search, productivity, and partner-built |
| [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) | 609 | Apache-2.0 | 2026-10-14 | 4 | Teacher skills and LLM-judge rubrics, co-developed with Learning Commons |
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | 4,809 | Apache-2.0 | 2026-10-13 | 32 | Read-only mirror of the community marketplace; not Anthropic-authored |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 40,681 | MIT | 2026-11-02 | 473 (455 top-level skills) | Also 223 agents, 195 instructions, 109 plugins. Community-contributed under a GitHub-owned repo |
| [github/copilot-plugins](https://github.com/github/copilot-plugins) | 380 | MIT | 2026-10-14 | 2 | build-perf-cpp, spark |
| [openai/skills](https://github.com/openai/skills) | 28,449 | none at root (per-skill) | 2026-06-24 | 44 (39 curated, 5 system) | Deprecated. `pushed_at` shows 2026-10-28, but main has not moved since June |
| [openai/plugins](https://github.com/openai/plugins) | 7,705 | none at root (per-plugin) | 2026-10-08 | 536 | 62 Codex plugin directories, many vendor-supplied |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | 26,852 | Apache-2.0 | 2026-08-09 | 0 | Specification, docs, `skills-ref` |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 33,357 | none detected | 2026-10-27 | 9 | React, Next.js, deploy, web design, writing guidelines |
| [cloudflare/skills](https://github.com/cloudflare/skills) | 3,247 | Apache-2.0 | 2026-10-31 | 19 | Workers, Durable Objects, Wrangler, web-perf |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 56,421 | MIT | 2026-09-14 | 1 | Multi-phase security audit |
| [supabase/agent-skills](https://github.com/supabase/agent-skills) | 2,980 | MIT | 2026-10-02 | 2 | supabase, Postgres best practices |
| [microsoft/skills](https://github.com/microsoft/skills) | 3,165 | MIT | 2026-10-30 | 213 | Mostly Azure SDK plugins, plus deep-wiki and 13 repo-level skills. `microsoft/agent-skills` redirects here |
| [google/skills](https://github.com/google/skills) | 21,774 | Apache-2.0 | 2026-11-01 | 184 | 158 under `skills/cloud`, plus ads, analytics, identity, developers |
| [google-gemini/gemini-skills](https://github.com/google-gemini/gemini-skills) | 4,370 | Apache-2.0 | 2026-10-30 | 3 | Gemini API only |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 8,656 | Apache-2.0 | 2026-08-17 | 16 | Stitch MCP design workflows |
| [huggingface/skills](https://github.com/huggingface/skills) | 11,251 | Apache-2.0 | 2026-10-29 | 26 | Hub, training, papers, community evals |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7,938 | CC-BY-SA-4.0 | 2026-10-28 | 97 | Security review, testing handbook, code-improver |
| [getsentry/skills](https://github.com/getsentry/skills) | 1,108 | Apache-2.0 | 2026-10-23 | 30 | Engineering workflow skills used by the Sentry team |
| [hashicorp/agent-skills](https://github.com/hashicorp/agent-skills) | 911 | MPL-2.0 | 2026-10-28 | 20 | Terraform, Packer |
| [expo/skills](https://github.com/expo/skills) | 4,011 | MIT | 2026-11-01 | 25 | Expo and EAS |
| [stripe/ai](https://github.com/stripe/ai) | 2,027 | MIT | 2026-11-02 | 60 (10 unique names) | Same skills copied per provider |
| [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | 23,871 | Apache-2.0 | 2026-10-31 | 33 (32 are test fixtures) | Security scanner for skills |
| [tavily-ai/skills](https://github.com/tavily-ai/skills) | 491 | MIT | 2026-10-30 | 6 | Search, research, monitor |
| [brave/brave-search-skills](https://github.com/brave/brave-search-skills) | 193 | MIT | 2026-08-12 | 13 | Brave Search API, including `llm-context` |
| [firecrawl/skills](https://github.com/firecrawl/skills) | 142 | ISC | 2026-10-22 | 37 | Search, scrape, research workflows |
| [upstash/context7](https://github.com/upstash/context7) | 64,051 | MIT | 2026-10-30 | 10 | `find-docs` and per-host copies of `context7-mcp` |

Repos checked for metadata only. "Pushed" is GitHub's `pushed_at`, which counts any branch. Skill counts were not measured.

| Repo | Stars | Licence | Pushed |
|---|---|---|---|
| [anthropics/financial-services](https://github.com/anthropics/financial-services) (`financial-services-plugins` redirects here) | 40,975 | Apache-2.0 | 2026-10-28 |
| [anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal) | 9,865 | Apache-2.0 | 2026-10-29 |
| [anthropics/defending-code-reference-harness](https://github.com/anthropics/defending-code-reference-harness) | 7,690 | NOASSERTION | 2026-08-06 |
| [anthropics/launch-your-agent](https://github.com/anthropics/launch-your-agent) | 1,106 | Apache-2.0 | 2026-09-23 |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) (the `npx skills` installer) | 37,632 | MIT | 2026-10-30 |
| [dotnet/skills](https://github.com/dotnet/skills) | 5,788 | MIT | 2026-11-02 |
| [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) | 3,367 | Apache-2.0 | 2026-10-30 |
| [awslabs/agent-plugins](https://github.com/awslabs/agent-plugins) | 933 | Apache-2.0 | 2026-11-02 |
| [flutter/agent-plugins](https://github.com/flutter/agent-plugins) | 3,136 | BSD-3-Clause | 2026-11-01 |
| [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills) | 1,321 | MIT | 2026-10-29 |
| [angular/skills](https://github.com/angular/skills) | 708 | none | 2026-10-31 |
| [duckdb/duckdb-skills](https://github.com/duckdb/duckdb-skills) | 614 | MIT | 2026-04-23 |
| [posit-dev/skills](https://github.com/posit-dev/skills) | 551 | MIT | 2026-10-28 |
| [elevenlabs/skills](https://github.com/elevenlabs/skills) | 528 | MIT | 2026-10-28 |
| [astral-sh/claude-code-plugins](https://github.com/astral-sh/claude-code-plugins) | 318 | Apache-2.0 | 2026-02-27 |
| [resend/resend-skills](https://github.com/resend/resend-skills) | 208 | MIT | 2026-10-28 |
| [denoland/skills](https://github.com/denoland/skills) | 102 | MIT | 2026-07-29 |
| [mastra-ai/skills](https://github.com/mastra-ai/skills) | 101 | NOASSERTION | 2026-10-31 |
| [ngrok/skills](https://github.com/ngrok/skills) | 15 | MIT | 2026-11-01 |

State changes worth knowing:

- The `plugins/README.md` in anthropics/claude-code says Anthropic's plugins are developed in claude-plugins-official. Commits on 2026-10-26 moved installs across, and one calls the local copies "stale" — [claude-code plugins README](https://github.com/anthropics/claude-code/blob/main/plugins/README.md), [commit history](https://github.com/anthropics/claude-code/commits/main/plugins).
- The `openai/skills` README opens with "This repository is deprecated" and points to `openai/plugins`. It still describes a `.experimental` folder, but the tree has only `.curated` and `.system` — [openai/skills README](https://github.com/openai/skills/blob/main/README.md).
- `anthropics/claude-plugins-community` is a read-only mirror, synced nightly. Its plugins passed automated security scanning but are community-submitted — [README](https://github.com/anthropics/claude-plugins-community/blob/main/README.md).
- Not found under these names: `cloudflare/agent-skills`, `google-gemini/skills`, `supabase/supabase-agent-skills`, `exa-labs/exa-skills`, `postmanlabs/postman-skills`, `github/skills` (404 from `gh api`).
- `openrouterteam/agent-skills` resolves to `OpenRouterArchived/agent-skills`, which is archived (`gh api`).
- `gh skill` is a GitHub CLI command in preview for installing skills from GitHub repositories (local `gh skill --help`).

### Inferences
- `pushed_at` overstates freshness, as the `gh api` one-liner in the brief would show for `openai/skills`. Use the last commit on the default branch when judging whether a repo is maintained.
- "Owned by a vendor" and "written by a vendor" differ. `github/awesome-copilot` is the main example: the skills below were first committed by individual contributors, not GitHub staff.
- A repo name is not provenance. [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) carries Anthropic's name but sits outside the `anthropics` org.

### Gaps
- The list of vendors is not exhaustive. It covers the named repos, `gh` search and vendor names I probed.
- `anthropics/claude-cookbooks` was not inspected for skill material.
- The `LICENSE.md` in anthropics/claude-code was not read, so "none reported" means only that GitHub detected no SPDX licence.

## What licences apply, per repo and per skill?

### Takeaway
Licence must be checked per skill. In `anthropics/skills`, 14 skills are Apache-2.0, 4 are proprietary and must not be imported, and `doc-coauthoring` has no licence at all. `openai/plugins` and `vercel-labs/agent-skills` also have no root licence file.

### Cited Findings

**anthropics/skills** (comparing `LICENSE.txt` blob hashes, then reading each variant):
- Apache-2.0: academy-guide, algorithmic-art, brand-guidelines, canvas-design, claude-api, discernment-nudge, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, webapp-testing, frontend-design — [skills tree](https://github.com/anthropics/skills/tree/main/skills).
- `docx`, `pdf`, `pptx`, `xlsx` are proprietary. Their licence bars extracting or retaining copies outside the Services, copying, derivative works and distribution — [skills/docx/LICENSE.txt](https://github.com/anthropics/skills/blob/main/skills/docx/LICENSE.txt). The README calls them "source-available, not open source" — [README](https://github.com/anthropics/skills/blob/main/README.md).
- `doc-coauthoring` has no `LICENSE.txt` and no `license` frontmatter, and the repo has no root licence — [skill](https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring). The README says only that "many" skills are Apache 2.0 — [README](https://github.com/anthropics/skills/blob/main/README.md).
- `getsentry/skills` has a differing copy of `doc-coauthoring` (15,967 vs 15,815 characters) under its Apache-2.0 root — [Sentry copy](https://github.com/getsentry/skills/tree/main/skills/doc-coauthoring).

**openai/skills:** per-skill files are mixed. `aspnet-core`, `chatgpt-apps`, `playwright`, `gh-fix-ci`, `define-goal`, `skill-creator` and `plugin-creator` are Apache-2.0. `vercel-deploy` is MIT. The Notion skills carry a permissive notice from Notion Labs. The Figma skills are governed by Figma Developer Terms, not an open licence — [notion LICENSE](https://github.com/openai/skills/blob/main/skills/.curated/notion-research-documentation/LICENSE.txt), [figma-use LICENSE](https://github.com/openai/skills/blob/main/skills/.curated/figma-use/LICENSE.TXT).

**openai/plugins:** no root licence. Licence is declared per plugin. `plugin-eval` declares MIT in `plugin.json`, and `superpowers` is MIT by Jesse Vincent — [plugin-eval manifest](https://github.com/openai/plugins/blob/main/plugins/plugin-eval/.codex-plugin/plugin.json), [superpowers manifest](https://github.com/openai/plugins/blob/main/plugins/superpowers/.codex-plugin/plugin.json).

**vercel-labs/agent-skills:** no `LICENSE` file anywhere in the tree, though the README says "MIT". Some skills declare `license: MIT` in frontmatter and `writing-guidelines` does not — [README](https://github.com/vercel-labs/agent-skills/blob/main/README.md).

**github/awesome-copilot:** MIT at root, with a few per-skill licence files (for example `skills/quality-playbook/LICENSE.txt`, `skills/agent-architecture/LICENSE.txt`) — [repo](https://github.com/github/awesome-copilot).

**anthropics/claude-plugins-official:** each plugin has its own `LICENSE`. I read `plugin-dev`'s, which is Apache-2.0, and did not read the others — [plugin-dev LICENSE](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/LICENSE).

**anthropics/k12-teacher-skills:** Apache-2.0, jointly copyrighted by Anthropic and Learning Commons, with `LICENSE` and `NOTICE` files in skill folders — [k12-check-for-understanding](https://github.com/anthropics/k12-teacher-skills/tree/main/plugin/skills/k12-check-for-understanding).

**trailofbits/skills:** CC-BY-SA-4.0 across the repo — [repo](https://github.com/trailofbits/skills).

### Inferences
- Treat `doc-coauthoring` as unlicensed. Sentry's Apache-2.0 root does not clearly relicense Anthropic's text, so reuse the idea (its Reader Testing stage), not the words.
- Do not copy `docx`, `pdf`, `pptx` or `xlsx` into `context/`, even for private use. The restriction covers retaining copies, not just distribution.
- CC-BY-SA matters less while Puck stays private, but anything adapted from Trail of Bits would carry attribution and share-alike duties if it were ever shared. This is a reading of the licence, not legal advice.
- Apache-2.0 and MIT imports should record origin and keep notices. `NOTICE` files in the k12 skills need to travel with any adapted text. `src/core/skills.py` `new()` already takes an `origin` argument, which looks like the natural place to record this.

### Gaps
- Licence files in the remaining 39 claude-plugins-official plugins were listed but not read.
- Per-skill licences in `microsoft/skills` and `google/skills` were not audited beyond the repo root.

## Which individual skills are relevant to Puck, and at what exact paths?

### Takeaway
Very little imports cleanly. Puck's lint requires `metadata.status`, `metadata.invocation`, `Procedure` as the first section and a `Done when` section, so every upstream skill needs rewriting, and the shortlist is really "what to adapt". The best picks are the skill-creator eval method, the k12 check-for-understanding design and rubrics, Sentry's `agents-md`, Anthropic's `skill-reviewer` agent, and a claim-verification skill. No official source covers spaced repetition or tutoring, so Puck's learning loop has to be original work.

### Cited Findings

**Import constraints, from Puck's own code**
- Lint allows only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`, and requires string metadata values, `metadata.status`, `metadata.invocation`, a first section called `Procedure`, a `Done when` section, and a body under 500 lines — [src/core/lint.py](/Users/doug/coding/puck/src/core/lint.py).
- Lint flags a host tool name only in backticks or in the form "the X tool", so plain prose is not caught — [src/core/lint.py](/Users/doug/coding/puck/src/core/lint.py).
- Running that regex over about 50 candidates with the tool names in Puck's adapters gave these hits: `create-implementation-plan` (`bash`), `claude-md-improver` (`Edit`), Sentry `skill-writer` (`create`), and Microsoft `skill-creator` (`create`). The other candidates had no hits from those names, although `create` may be a false positive on ordinary English in backticks — [src/adapters/claude.py](/Users/doug/coding/puck/src/adapters/claude.py), [src/adapters/copilot.py](/Users/doug/coding/puck/src/adapters/copilot.py).
- `~tok` below is characters divided by 4, a rough estimate.

**Learning**

| Skill | Path | Lines / ~tok | Licence | Verdict |
|---|---|---|---|---|
| k12-check-for-understanding | [anthropics/k12-teacher-skills `plugin/skills/k12-check-for-understanding`](https://github.com/anthropics/k12-teacher-skills/tree/main/plugin/skills/k12-check-for-understanding) | 166 / not measured | Apache-2.0 | Adapt the design. 1-3 formative items, distractors drawn from documented misconceptions, and a guide saying what each response reveals. Math and teacher-facing, so it needs reshaping for self-study |
| k12 rubrics | [anthropics/k12-teacher-skills `evals/`](https://github.com/anthropics/k12-teacher-skills/tree/main/evals) | CSV | Apache-2.0 | Adapt. Independent 0/1 criteria built for LLM-as-judge, with per-criterion pass rates recommended over an aggregate score. Includes `evals/k12-check-for-understanding/rubrics/math.csv` |
| exam-ready | [github/awesome-copilot `skills/exam-ready`](https://github.com/github/awesome-copilot/tree/main/skills/exam-ready) | 100 / 983 | MIT (root) | Borrow ideas. Refuses to use outside knowledge and adds time-based triage. Written for last-minute cramming with ready-to-write answers, which runs against attempt-first. Contributor: `ayushsaklani-min`, 2026-04-20 |
| mentoring-juniors | [github/awesome-copilot `skills/mentoring-juniors`](https://github.com/github/awesome-copilot/tree/main/skills/mentoring-juniors) | 310 / 3,475 | MIT | Mine only. Only skill in the corpus that mentions Socratic method, but it carries a "Sensei" persona, emoji catchphrases and a junior audience. Contributors: `fdescamps`, Thomas Chmara |
| mentor, critical-thinking agents | [`agents/mentor.agent.md`](https://github.com/github/awesome-copilot/blob/main/agents/mentor.agent.md), [`agents/critical-thinking.agent.md`](https://github.com/github/awesome-copilot/blob/main/agents/critical-thinking.agent.md) | short | MIT (root) | Mine. No-edit challenge modes, with Copilot tool lists to drop |
| learning-output-style | [anthropics/claude-plugins-official `plugins/learning-output-style`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/learning-output-style) | plugin | per-plugin LICENSE (not read) | Adapt the pattern. SessionStart hook injects an interactive mode where the user writes 5-10 meaningful lines at decision points. Its README warns of the token cost |
| discernment-nudge | [anthropics/skills `skills/discernment-nudge`](https://github.com/anthropics/skills/tree/main/skills/discernment-nudge) | 209 / 2,623 | Apache-2.0 | Consider for planning. Appends 2-3 specific follow-ups on facts, reasoning and missing context, at most once per conversation. Explicitly skips purely educational explanations and code the user will run |
| huggingface-papers | [huggingface/skills `skills/huggingface-papers`](https://github.com/huggingface/skills/tree/main/skills/huggingface-papers) | 239 / 2,337 | Apache-2.0 (root) | Adapt if paper reading matters. Covers arXiv and HF paper pages in markdown; focused on AI and CS |

**Research and verification**

| Skill | Path | Lines / ~tok | Licence | Verdict |
|---|---|---|---|---|
| doublecheck | [github/awesome-copilot `skills/doublecheck`](https://github.com/github/awesome-copilot/tree/main/skills/doublecheck) | 277 / 3,972 | MIT (root) | Adapt. Claim-level ratings (VERIFIED, PLAUSIBLE, DISPUTED, FABRICATION RISK) with source links and a full report mode. Trim heavily. Contributor: `dvelton` |
| build-evidence-map | [github/awesome-copilot `skills/build-evidence-map`](https://github.com/github/awesome-copilot/tree/main/skills/build-evidence-map) | 107 / 1,270 | MIT (root) | Adapt. Keeps supporting, contradicting, qualifying and missing evidence for contested choices. Contributor: `alsoleg89`, 2026-08-05 |
| tavily-research | [tavily-ai/skills `skills/tasks/tavily-research`](https://github.com/tavily-ai/skills/tree/main/skills/tasks/tavily-research) | 58 / not measured | MIT (root) | Take the procedure, drop the vendor. Splits a question into non-overlapping subtopics and scales their number to the shape of the question. Bound to the `tvly` CLI as shipped |
| search-strategy, knowledge-synthesis | [knowledge-work-plugins `enterprise-search/skills/search-strategy`](https://github.com/anthropics/knowledge-work-plugins/tree/main/enterprise-search/skills/search-strategy), [`knowledge-synthesis`](https://github.com/anthropics/knowledge-work-plugins/tree/main/enterprise-search/skills/knowledge-synthesis) | 222 / 1,793; 258 / 2,115 | Apache-2.0 | Mine. Query decomposition, dedup, confidence by freshness and authority. Tied to workplace connectors |
| wiki-researcher | [microsoft/skills `.github/plugins/deep-wiki/skills/wiki-researcher`](https://github.com/microsoft/skills/tree/main/.github/plugins/deep-wiki/skills/wiki-researcher) | 82 / 1,117 | MIT | Adapt for code questions. Multi-turn codebase research that grounds claims in traced code |
| firecrawl-research-papers | [firecrawl/skills `skills/workflows/firecrawl-research-papers`](https://github.com/firecrawl/skills/tree/main/skills/workflows/firecrawl-research-papers) | not measured | ISC | Optional. Its index is described as largely biomedical, and it needs Firecrawl |
| llm-context, find-docs | [brave `skills/llm-context`](https://github.com/brave/brave-search-skills/tree/main/skills/llm-context), [upstash `skills/find-docs`](https://github.com/upstash/context7/tree/main/skills/find-docs) | 300 / not measured; not measured | MIT | Tool choices, not skills to import. Brave needs an API key |

**Planning**

| Skill | Path | Lines / ~tok | Licence | Verdict |
|---|---|---|---|---|
| write-spec | [knowledge-work-plugins `product-management/skills/write-spec`](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management/skills/write-spec) | 250 / 3,074 | Apache-2.0 | Mine for Puck's `plan`. Goals, non-goals, success metrics, acceptance criteria, phasing. PM-oriented and longer than a one-page SPEC.md needs |
| define-goal | [openai/skills `skills/.curated/define-goal`](https://github.com/openai/skills/tree/main/skills/.curated/define-goal) | 99 / 1,411 | Apache-2.0 | Mine. Prefers measurable outcomes, explicit evidence and bounded scope. Repo is deprecated, so copy rather than track it |
| system-design, testing-strategy, tech-debt, debug | [knowledge-work-plugins `engineering/skills/`](https://github.com/anthropics/knowledge-work-plugins/tree/main/engineering/skills) | 42 / 327; 33 / 319; 32 / 364; 95 / 890 | Apache-2.0 | Skip the first three: generic checklists. `debug` was not read past its header |
| writing-plans, systematic-debugging, verification-before-completion | [openai/plugins `plugins/superpowers/skills/`](https://github.com/openai/plugins/tree/main/plugins/superpowers/skills) | 171 / 1,757; 283 / 2,360; 120 / 899 | MIT (Jesse Vincent) | Community work vendored by OpenAI, not first-party. Assess at the source, [obra/superpowers](https://github.com/obra/superpowers) |
| create-implementation-plan, structured-autonomy-plan | [github/awesome-copilot `skills/`](https://github.com/github/awesome-copilot/tree/main/skills) | 185 / 2,091; 81 / 758 | MIT (root) | Reject. The first says instructions are for AI-to-AI use and uses `${input:PlanPurpose}`. The second hard-codes `#tool:runSubagent` |

**Coding and review**

| Skill or agent | Path | Lines / ~tok | Licence | Verdict |
|---|---|---|---|---|
| agents-md | [getsentry/skills `skills/agents-md`](https://github.com/getsentry/skills/tree/main/skills/agents-md) | 95 / 797 | Apache-2.0 | Adapt. "Target under 60 lines; never exceed 100", verify paths and commands exist, symlink `CLAUDE.md` to `AGENTS.md` |
| find-bugs | [getsentry/skills `skills/find-bugs`](https://github.com/getsentry/skills/tree/main/skills/find-bugs) | 75 / 707 | Apache-2.0 | Adapt for `review`. Full-diff intake, then attack-surface mapping |
| silent-failure-hunter and others | [claude-plugins-official `plugins/pr-review-toolkit/agents/`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pr-review-toolkit/agents) | agent docs | per-plugin LICENSE (not read) | Candidates for `context/agents/`. Also has `pr-test-analyzer`, `type-design-analyzer`, `comment-analyzer`. Only `silent-failure-hunter` was sampled |
| code-architect, code-explorer | [claude-plugins-official `plugins/feature-dev/agents/`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/feature-dev/agents) | agent docs | per-plugin LICENSE (not read) | Review before deciding; not read |
| code-review command | [claude-plugins-official `plugins/code-review/commands/code-review.md`](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-review/commands/code-review.md) | command | per-plugin LICENSE (not read) | Skip as written. GitHub PR-bound and specifies model tiers |
| differential-review | [trailofbits/skills `plugins/differential-review/skills/differential-review`](https://github.com/trailofbits/skills/tree/main/plugins/differential-review/skills/differential-review) | 225 / 1,834 | CC-BY-SA-4.0 | Optional for security. Blast radius by caller count, and it states coverage limits |
| security-audit | [cloudflare/security-audit-skill `skills/security-audit`](https://github.com/cloudflare/security-audit-skill/tree/main/skills/security-audit) | 192 / not measured | MIT | Optional. Not read past its description |
| mcp-builder | [anthropics/skills `skills/mcp-builder`](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) | 252 / 2,773 | Apache-2.0 | Keep in reserve for when Puck builds MCP tools |
| acquire-codebase-knowledge | [github/awesome-copilot `skills/acquire-codebase-knowledge`](https://github.com/github/awesome-copilot/tree/main/skills/acquire-codebase-knowledge) | 173 / 2,269 | MIT | Optional. Generates codebase docs, which sits awkwardly with the finding on generated context |

**Skill authoring, evals and supply chain**

| Skill or tool | Path | Lines / ~tok | Licence | Verdict |
|---|---|---|---|---|
| skill-creator | [anthropics/skills `skills/skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | 485 / 8,246 | Apache-2.0 | Adopt the method, not the skill. See the last section |
| skill-reviewer | [claude-plugins-official `plugins/plugin-dev/agents/skill-reviewer.md`](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/plugin-dev/agents/skill-reviewer.md) | agent doc | Apache-2.0 | Adapt into `context/agents/`. Read-only (Read, Grep, Glob) and covers structure, description quality and progressive disclosure |
| skill-writer | [getsentry/skills `skills/skill-writer`](https://github.com/getsentry/skills/tree/main/skills/skill-writer) | 156 / 2,504 | Apache-2.0 | Mine. Router-style `SKILL.md`, flat `references/` with "open when" reasons, and `SPEC.md`, `SOURCES.md` and `EVAL.md` per skill. Its rule against naming providers fits Puck. Its evals default to AXIS and Codex |
| skill-scanner | [getsentry/skills `skills/skill-scanner`](https://github.com/getsentry/skills/tree/main/skills/skill-scanner) | 209 / 2,473 | Apache-2.0 | Useful import gate. Checks prompt injection, malicious scripts, permissions, secrets and supply chain. Needs `uv` |
| SkillSpector | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) | tool | Apache-2.0 | Alternative scanner; not evaluated here |
| plugin-eval | [openai/plugins `plugins/plugin-eval`](https://github.com/openai/plugins/tree/main/plugins/plugin-eval) | Node CLI | MIT | Look at the ideas (token budgets, "Fix First", observed usage). Codex-focused; requires Node 20+ and a local checkout |
| skill-improver | [trailofbits/skills `plugins/code-improver/skills/skill-improver`](https://github.com/trailofbits/skills/tree/main/plugins/code-improver/skills/skill-improver) | 138 / 1,847 | CC-BY-SA-4.0 | Skip. Depends on Claude Code workflows and `plugin-dev` |
| skill-development | [claude-plugins-official `plugins/plugin-dev/skills/skill-development`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev/skills/skill-development) | 637 / 5,633 | Apache-2.0 | Skip. Over the 500-line guidance and Claude plugin-specific |
| Microsoft skill-creator | [microsoft/skills `.github/skills/skill-creator`](https://github.com/microsoft/skills/tree/main/.github/skills/skill-creator) | 1,313 / 16,957 | MIT | Skip. Over twice the line guidance, Azure-focused |
| OpenAI skill-creator | [openai/skills `skills/.system/skill-creator`](https://github.com/openai/skills/tree/main/skills/.system/skill-creator) | 368 | Apache-2.0 | Skip. Codex scaffolding with no eval loop found in a keyword scan |
| continual-learning | [microsoft/skills `.github/skills/continual-learning`](https://github.com/microsoft/skills/tree/main/.github/skills/continual-learning) | 79 / 620 | MIT | Reject. Hook-captured learnings in SQLite with automatic decay clashes with reviewable changes to standing context |
| memory-management | [knowledge-work-plugins `productivity/skills/memory-management`](https://github.com/anthropics/knowledge-work-plugins/tree/main/productivity/skills/memory-management) | 323 / 2,167 | Apache-2.0 | Skip. Workplace shorthand memory, using `CLAUDE.md` plus a `memory/` directory |
| claude-md-improver, session-report, receipts | [claude-plugins-official `plugins/`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins) | 179; 42; 300 | per-plugin LICENSE (not read) | Skip. All Claude-specific. `session-report`'s transcript analyser is relevant only if the design's context-measurement question returns |

**Coverage check for learning**
- A full-text search of 1,962 SKILL.md files from 18 repos found zero matches for flashcards, spaced repetition, FSRS, SM-2, Anki, retrieval practice or active recall. "Tutor" appeared in 4 files, all incidental, and "Socratic" only in `mentoring-juniors`. The search excluded NVIDIA test fixtures. It did not cover the other repos in the tables above, or agent and command files — [github/awesome-copilot](https://github.com/github/awesome-copilot), [openai/plugins](https://github.com/openai/plugins), [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins), [microsoft/skills](https://github.com/microsoft/skills).

### Inferences
- A sensible first batch: (1) a Puck `skill-eval` procedure from the skill-creator method, (2) `skill-reviewer` as a Puck agent, (3) a claim-check skill trimmed from `doublecheck`, (4) a misconception-based check, from the k12 design, for use after an attempt, (5) Sentry `agents-md` as guidance for instruction files.
- The k12 design looks like a strong answer to the design doc's finding that LLM flashcards are 36-52% unusable, because it makes distractor quality the thing being judged. This is untested for adult self-study, and it does not replace human approval of cards.
- `doublecheck` fits the design finding that citation accuracy falls behind link validity. Its active mode classifies every response, so it would be better as an on-demand check than as an always-on rule.
- `learning-output-style` is the closest official match to Puck's "learn vs build" modes, and a hook is a better fit than a skill because the design says models under-use optional retrieval. A mode that must apply reliably should not depend on triggering.
- Run a scanner over any imported skill with scripts, even from a trusted vendor. Prose-only imports are easier to review by hand.

### Gaps
- Most candidates were read as headers and opening sections, not in full. Read in full: spec, the two agentskills eval guides, and skill-creator's `SKILL.md`. Read substantially: `exam-ready`, `continual-learning`, part of `doublecheck`, part of `mentoring-juniors`, part of `discernment-nudge`, part of `k12-check-for-understanding`.
- Whether these skills improve outcomes is unknown. I found no published with/without benchmark for any shortlisted skill, and I did not search for one specifically.
- `references/math.md` in `k12-check-for-understanding`, which holds the actual item-design guidance, was not read.
- `plugins/consensus` and `plugins/zotero` in `openai/plugins` could help research and were not read beyond the Zotero description.

## What is the current Agent Skills specification?

### Takeaway
The spec is small and stable: six frontmatter fields, two of them required, with the last spec text change on 2026-08-04. It does not define discovery paths, invocation control, evals or versioning, so harnesses have diverged on these. Puck's lint already matches the spec.

### Cited Findings

**Frontmatter** — [agentskills.io/specification](https://agentskills.io/specification), which matched [docs/specification.mdx](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx) when compared on retrieval:

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1-64 characters; `a-z`, `0-9`, hyphens; no leading, trailing or consecutive hyphens; must match the parent directory |
| `description` | Yes | 1-1024 characters; what it does and when to use it |
| `license` | No | Licence name or bundled file reference |
| `compatibility` | No | 1-500 characters; environment requirements. Most skills do not need it |
| `metadata` | No | Map from string keys to string values |
| `allowed-tools` | No | Space-separated string. Experimental; support varies |

**Directory structure:** a folder with `SKILL.md`, plus optional `scripts/`, `references/` and `assets/`. These are conventions, and any other files are allowed — [specification](https://agentskills.io/specification).

**Progressive disclosure** — [specification](https://agentskills.io/specification):
1. Metadata, about 100 tokens, loaded at startup for all skills.
2. Instructions, under 5,000 tokens recommended, loaded on activation.
3. Resources, loaded as needed.

**Size and reference rules:** keep `SKILL.md` under 500 lines, and keep file references one level deep with relative paths from the skill root. These are recommendations. The hard limits are the character limits on fields — [specification](https://agentskills.io/specification).

**Validation:** `skills-ref validate`, but its README says it is "intended for demonstration purposes only" and not for production — [skills-ref README](https://github.com/agentskills/agentskills/blob/main/skills-ref/README.md).

**History:** recent changes were clarifications. On 2026-08-04, `metadata` was clarified and the open directory structure was made explicit. On 2026-05-16, a character-range fix. The latest repo commit (2026-08-09) added OpenClaw to the client showcase — [commit history](https://github.com/agentskills/agentskills/commits/main/docs/specification.mdx). The spec text shows no version number — [specification](https://agentskills.io/specification).

**Adoption:** the client list has 46 entries, including Claude Code, GitHub Copilot, VS Code, ChatGPT & Codex, Cursor, Gemini CLI, Goose, Kiro and OpenCode — [docs/snippets/clients.jsx](https://github.com/agentskills/agentskills/blob/main/docs/snippets/clients.jsx). A secondary analysis said about 40 as of June 2026 — [Agentman report](https://agentman.ai/blog/agent-skills-ecosystem-report-2026).

**Client implementation guide** (guidance, not spec) — [adding-skills-support.mdx](https://github.com/agentskills/agentskills/blob/main/docs/client-implementation/adding-skills-support.mdx):
- `.agents/skills/` at project and user level is a widely adopted convention for sharing between clients, and the spec does not mandate it.
- Clients should validate leniently, gate project skills on trust, and protect activated skill content from compaction.
- Each skill adds roughly 50-100 tokens to the catalogue.

**Open proposals**, by thumbs-up: a standard skills folder (#15, 188), Claude Code skills-as-commands frontmatter (#105, 35), recursive discovery (#115, 15), subdirectories (#59, 10), XDG paths (#513, 10), dependencies and testing (#110, 8), activation mechanisms (#57, 6), a skill-creator skill (#190, 5) — [issues](https://github.com/agentskills/agentskills/issues).

**Host behaviour**
- Claude Code accepts 20 frontmatter fields and ignores unknown ones. Outside Claude Code (claude.ai uploads, Skills API, `package_skill.py`), only the six spec fields are allowed — [Claude Code skills docs](https://code.claude.com/docs/en/skills).
- Claude Code truncates `description` plus `when_to_use` at 1,536 characters in the listing. The listing budget scales at 1% of the context window, and descriptions get dropped when it overflows — [Claude Code skills docs](https://code.claude.com/docs/en/skills).
- After compaction, Claude Code re-attaches the first 5,000 tokens of each recent skill within a 25,000-token combined budget, most recent first — [Claude Code skills docs](https://code.claude.com/docs/en/skills).
- Claude Code's discovery table lists `.claude/skills`, `~/.claude/skills`, nested, plugin and enterprise locations. `.agents/skills` does not appear in it — [Claude Code skills docs](https://code.claude.com/docs/en/skills).
- Copilot reads project skills from `.github/skills`, `.claude/skills` or `.agents/skills`, and personal skills from `~/.copilot/skills` or `~/.agents/skills` — [GitHub docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).
- Copilot CLI docs list `name`, `description`, `license` and `allowed-tools`, and warn against pre-approving `shell` or `bash` unless the skill and its scripts have been reviewed — [Copilot CLI docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).

**Practice vs spec** (my scan of 1,939 SKILL.md files in 15 repos, excluding NVIDIA fixtures; 3 Microsoft sub-skill files have no frontmatter):
- Field use: `metadata` 549, `license` 323, `allowed-tools` 129, `argument-hint` 97, `compatibility` 80, `user-invocable` 68, `version` 48, `triggers` 46, `disable-model-invocation` 22.
- 4 descriptions run past 1,024 characters by my approximate count, including Anthropic's own `skills/claude-api` at about 1,070. 102 files exceed 500 lines. Regex parsing, so treat these as approximate — [anthropics/skills claude-api](https://github.com/anthropics/skills/tree/main/skills/claude-api).

**Puck's current fit:** lint's standard field set, 64-character name rule, 1,024-character description limit and 500-line body limit all match the spec — [src/core/lint.py](/Users/doug/coding/puck/src/core/lint.py).

### Inferences
- Puck can stay spec-strict in `context/` and leave host-only behaviour to adapters. `metadata.invocation` is the right kind of neutral field, because invocation control is not in the spec.
- Keep descriptions well under 1,024 characters. The hard limit is rarely the constraint, because the 1% listing budget is shared by all skills.
- Keep important instructions in the first 5,000 tokens. That fits the spec recommendation and Claude Code's compaction limit.
- `.agents/skills` is the natural install path for a generic AGENTS.md host, but Claude Code needs its own path, so adapters still matter.
- Spec-compliant does not mean portable. Scripts, `allowed-tools` syntax and tool names remain host-dependent.

### Gaps
- Exactly how each of the 46 clients treats non-spec fields was not surveyed. Only Claude Code and Copilot were checked.
- Copilot's stated field list comes from CLI docs. VS Code's may differ.
- No governance document was read, so how spec changes are decided remains unclear.

## How does skill-creator work, and is its description-optimisation or eval method worth adopting?

### Takeaway
Adopt the method and leave the skill. Baseline comparison, assertions added after the first run, and near-miss trigger tests are worth having, and agentskills.io documents them in vendor-neutral form. The implementation is Claude Code-specific and expensive, so Puck should use a small harness-neutral version. Description optimisation should be reserved for model-invoked skills that show real trigger problems.

### Cited Findings

**Structure:** `SKILL.md` plus `agents/` (grader, comparator, analyzer), `references/schemas.md`, `eval-viewer/`, `assets/eval_review.html` and `scripts/`. Licence is Apache-2.0 and the last change to the folder was 2026-04-20 — [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator). The copy in `claude-plugins-official` has an identical `SKILL.md` — [plugin copy](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator/skills/skill-creator).

**Output eval loop** — [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md):
1. Start with 2-3 realistic prompts in `evals/evals.json`.
2. Run each with and without the skill at the same time. When improving a skill, the baseline is a snapshot of the old version.
3. Draft assertions while the runs are in progress. Record tokens and duration in `timing.json`.
4. Grade each assertion with evidence, using scripts where assertions can be checked by code. Aggregate to `benchmark.json` (mean, stddev and delta).
5. Run an analyst pass for non-discriminating assertions, flaky evals and cost trade-offs.
6. Show outputs to a human in the viewer and read `feedback.json`, where empty feedback means the output was fine.
7. Revise: generalise from feedback, stay lean, explain why, and bundle scripts that every run reinvented.

Blind A/B comparison is optional — [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).

**Grading principles:** require concrete evidence for a PASS, and remove assertions that pass in both configurations because they inflate the with-skill score — [Evaluating skills](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/evaluating-skills.mdx).

**Description optimisation** — [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), [run_loop.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_loop.py):
- About 20 realistic queries: 8-10 should trigger and 8-10 should not, favouring near-misses. A human reviews them.
- Defaults: 40% holdout, 3 runs per query, threshold 0.5, up to 5 iterations, 10 workers, 30-second timeout.
- `split_eval_set` keeps both classes in the holdout, with a fixed seed.
- Test scores are stripped from the history given to the improving model (`blinded_history`), and the best description is picked by test score.

**Implementation** — [run_eval.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py), [improve_description.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/improve_description.py):
- For each query it writes a temporary `.claude/commands/<name>-skill-<id>.md`, runs `claude -p` with stream-json, and watches for a `Skill` or `Read` tool call.
- Improvement also calls `claude -p`, listing failed queries, false triggers and previous attempts, and asks for something "structurally different".

**Vendor-neutral versions:** agentskills.io gives the same method with a replaceable `check_triggered` function, and warns against adding keywords from failed queries. It recommends a final check with 5-10 fresh queries — [Optimizing descriptions](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/optimizing-descriptions.mdx). It also recommends clean-context runs and `evals/evals.json` — [Evaluating skills](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/evaluating-skills.mdx).

**Trigger caveat:** agents typically consult skills only for tasks beyond what they can do alone, so a simple request may not trigger a well-described skill — [Optimizing descriptions](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/optimizing-descriptions.mdx).

**"Pushy" descriptions:** skill-creator says Claude tends to undertrigger, and recommends slightly pushy descriptions — [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md). agentskills.io repeats "err on the side of being pushy" — [Optimizing descriptions](https://github.com/agentskills/agentskills/blob/main/docs/skill-creation/optimizing-descriptions.mdx).

**Puck's design position:** models under-use optional retrieval, so critical context is injected or placed in instruction files, and verification should use a concrete checklist in a separate agent or script — [docs/design.md](/Users/doug/coding/puck/docs/design.md).

### Inferences
- **Adopt:** with/without baseline, assertions after the first run, evidence-based PASS, removing non-discriminating assertions, recording token cost, and near-miss negatives. These fit Puck's checklist-based verification.
- **Skip:** the viewer, packaging, Cowork and Claude.ai branches, audience-tone guidance, and the 485-line skill itself. By the rough character estimate it is about 8,200 tokens, well over the spec's 5,000 recommendation.
- **Cost:** at defaults, 20 queries × 3 runs × 5 iterations is up to 300 `claude -p` runs. That is hard to justify for Puck's three skills.
- **Statistical weakness:** 8 held-out queries give a coarse score, and choosing the best of several iterations on them re-uses the holdout. Agentskills' fresh 5-10 query check addresses this and should be kept.
- **Best first use:** near-miss tests between `task`, `plan` and `review`, since the likely failure for Puck is the wrong skill firing, not no skill firing. A single round of about 10 queries per skill, with human-edited descriptions, should be enough to start.
- **Pushiness needs care:** it may raise false triggers across a small skill set, and it says nothing about hosts other than Claude.
- **Harness neutrality:** `src/core/` cannot name a harness and adapters must stay pure, so any runner needs an adapter-supplied command and detection pattern, with execution elsewhere. `run_eval.py` should be reimplemented, not copied, because its command-file mechanism is Claude Code-specific.
- **Do not rely on triggering for anything critical.** Description work improves odds; it does not make a skill reliable. Pass-critical procedures should stay injected or explicitly invoked.
- **Rubrics from k12** are a good complement for learning skills, whose output quality is hard to capture in simple assertions.

### Gaps
- `agents/grader.md`, `comparator.md`, `analyzer.md`, `references/schemas.md` and `aggregate_benchmark.py` were not read, only described through `SKILL.md`.
- I found no independent measurement showing that this optimisation improves real-world triggering, or on hosts other than Claude.
- Claude Code tooling exposes `claude plugin eval` and `/skill-doctor`, which may replace parts of this loop. They were not researched here.
- How Copilot could report that a skill was activated, which a harness-neutral runner needs, was not checked.
