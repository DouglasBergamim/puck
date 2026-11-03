# Community workflow frameworks: skills and agents worth importing into Puck

Retrieval notes:
- All star, fork, licence, push and issue numbers come from live `gh api repos/OWNER/REPO` calls. The table snapshot was taken on 2026-11-02 at 04:42 UTC. An earlier snapshot was taken at 01:50 to 01:55 UTC.
- Daily star curves come from GitHub's new privacy-safe endpoint, `GET /repos/{owner}/{repo}/stargazers/history`, retrieved 2026-11-02. Each curve sums exactly to the live star count, which validates the data.
- Last-commit dates are default-branch commit dates, from `gh api repos/X/commits?per_page=1`.
- Skill and agent counts come from `git/trees/HEAD?recursive=1`, retrieved 2026-11-02.
- Puck baseline read first:
  - Skills: `task`, `plan`, `review` in `context/skills/`.
  - Agents: `reviewer`, `retro` in `context/agents/`.
  - `task` already has: `puck task check` acceptance checks, scratch experiments, "after three failed attempts on one problem, stop and rethink", and retro.
  - `plan` already interviews a few questions at a time with a recommendation each.
  - `review` already spawns a fresh `reviewer` without passing its own reasoning. The reviewer requires a location plus a concrete failure path.
- Fetched repo content was treated as data. Nothing was cloned or run.

## Q1. Repository facts: stars, licence, activity, issue load, skill/agent counts, curated or dump

### Takeaway
Only a handful of these are curated, single-voice skill sets: obra/superpowers, mattpocock/skills, addyosmani/agent-skills, and the one-skill cloudflare/security-audit-skill. The rest are one of three things:
- **Large aggregations:** ECC, wshobson/agents, davila7/claude-code-templates, VoltAgent, sickn33, ruflo.
- **Link lists:** hesreallyhim, VoltAgent/awesome-agent-skills.
- **Tooling-bound methodologies:** gstack, GSD Core, BMAD, spec-kit. Their skill text depends on their own binaries, config files or directory layout.

### Cited Findings
Each Stars entry gives the 04:42 UTC figure, followed by forks and watchers in parentheses.

| Repo | Stars (forks / watchers) | Licence (GitHub) | Last default-branch commit | Open issues+PRs | SKILL.md files (unique names) | Agent files (unique) | Commits / contributors | Character |
|---|---|---|---|---|---|---|---|---|
| obra/superpowers | 310,737 (27,654 / 1,131) | MIT | 2026-10-21 (release v7.0.1 same day; pushed 10-29) | 377 | 15 | 0 (subagent prompts live inside skills) | 686 / 44 | Curated methodology |
| mattpocock/skills | 309,390 (26,040 / 1,600) | MIT | 2026-10-31 | 201 | 39 (20 engineering, 8 "in-progress", 4 misc) | 0 (`agents/openai.yaml` metadata only) | 553 / 8 | Curated, personal |
| affaan-m/ECC (was everything-claude-code; API now returns `affaan-m/ECC`) | 294,915 (43,654 / 1,446) | MIT | 2026-10-30 | 201 | 1,068 (317 unique; 518 under `docs/` translations) | 310 (76 unique) | 4,321 / 479 | Bundle / dump |
| garrytan/gstack | 138,603 (20,549 / 770) | MIT | 2026-11-02 | 149 | 70 (incl. test fixtures) | 0 | 806 / 16 | Opinionated toolchain, binary-coupled |
| github/spec-kit | 145,074 (13,001 / 728) | MIT | 2026-10-30 | 225 | 2 (repo-internal) + 37 command templates | 0 | 2,312 / 333 | CLI toolkit, not a skill set |
| addyosmani/agent-skills | 112,593 (11,786 / 558) | MIT | 2026-11-01 | 122 | 25 | 4 | 807 / 97 | Curated |
| ruvnet/ruflo (was claude-flow) | 80,560 (9,451 / 475) | MIT | 2026-11-01 | 980 | 388 (302 unique) | 98 (87 unique) | 10,008 / 82 | Platform + dump |
| hesreallyhim/awesome-claude-code | 57,065 (4,903 / 323) | NOASSERTION → actually CC BY-NC-ND 4.0 | 2026-11-02 | 1,084 | 0 | 0 | 2,293 / 16 | Link list |
| cloudflare/security-audit-skill | 56,542 (3,686 / 208) | MIT | 2026-09-14 | 110 | 1 (+ companion docs) | 0 | 14 / 4 | Single curated skill |
| bmad-code-org/BMAD-METHOD | 54,871 (6,131 / 413) | NOASSERTION (LICENSE text is MIT, © BMad Code LLC) | 2026-10-31 | 94 | 35 (32 real skills) | 2 | 2,357 / 163 | Methodology, config-bound |
| wshobson/agents | 42,087 (4,454 / 313) | MIT | 2026-10-30 | 7 | 185 | 202 (137 unique) | 629 / 93 | Plugin marketplace / aggregation |
| VoltAgent/awesome-agent-skills | 36,733 (4,043 / 226) | MIT | 2026-10-30 | 33 | 0 (README link list, 4 files) | 0 | 945 / 287 | Link list |
| davila7/claude-code-templates | 33,050 (3,843 / 193) | MIT | 2026-11-02 | 487 | 917 (896 unique) | 27+ (layout differs; see gaps) | 1,949 / 141 | Catalog / dump |
| VoltAgent/awesome-claude-code-subagents | 26,263 (3,012 / 233) | MIT | 2026-10-30 | 2 | 0 | 165 | 533 / 45 | Agent collection |
| SuperClaude-Org/SuperClaude_Framework | 23,922 (1,988 / 191) | MIT | 2026-09-27 | 72 | 9 (6 unique) | 42 (22 unique; duplicated `src/` and `plugins/`) | 349 / 47 | Persona framework, stalling |
| gsd-build/get-shit-done | 64,183 (5,436 / 271) | MIT | 2026-05-31; **archived** | 0 | 0 | 37 | 2,928 / 144 | Moved |
| open-gsd/gsd-core (GSD's current home) | 11,136 (786 / 36) | MIT | 2026-11-01 | 270 | 144 (72 unique; duplicated for `pi/`) | 67 | 6,463 / 186 | Methodology + CLI |

Sources for the table:
- Repo metadata: https://api.github.com/repos/obra/superpowers and the same `repos/OWNER/REPO` path for each repo.
- Trees: https://api.github.com/repos/OWNER/REPO/git/trees/HEAD?recursive=1.
- GSD move notice: https://github.com/gsd-build/get-shit-done (README "GSD Has Moved", which points to open-gsd/gsd-core).
- awesome-claude-code licence: https://github.com/hesreallyhim/awesome-claude-code/blob/HEAD/LICENSE (CC BY-NC-ND 4.0).
- BMAD licence: https://github.com/bmad-code-org/BMAD-METHOD/blob/HEAD/LICENSE (MIT text).

Other repos above 5,000 stars in scope, from the same live calls:
- **anthropics/skills:** 186,435 stars. No repo-level licence. Licences are per skill:
  - `skills/skill-creator/LICENSE.txt` is Apache-2.0.
  - `skills/docx/LICENSE.txt` is proprietary ("governed by your agreement with Anthropic").
  - 20 SKILL.md files. Source: https://github.com/anthropics/skills
- **anthropics/claude-plugins-official:** 45,745 stars, Apache-2.0. Contains the `pr-review-toolkit` and `feature-dev` agents. https://github.com/anthropics/claude-plugins-official
- **multica-ai/andrej-karpathy-skills:** 228,105 stars. GitHub detects no licence, but the SKILL.md frontmatter says `license: MIT`, so the two conflict. One skill. Last commit 2026-04-20. https://github.com/multica-ai/andrej-karpathy-skills
- **DietrichGebert/ponytail:** 182,255 stars, MIT, 6 skills (duplicated for openclaw). https://github.com/DietrichGebert/ponytail
- **Fission-AI/OpenSpec:** 73,627 stars, MIT. Spec-driven development. https://github.com/Fission-AI/OpenSpec
- **shanraisshan/claude-code-best-practice:** 68,438 stars, MIT.
- **alibaba/open-code-review:** 49,255 stars, Apache-2.0.
- **sickn33/agentic-awesome-skills:** 48,999 stars, MIT. 8,898 SKILL.md files, 2,910 unique. A dump.
- **github/awesome-copilot:** 40,685 stars, MIT. 473 skills and 226 agents.
- **alirezarezvani/claude-skills:** 29,138 stars, MIT. 455 unique skills.
- **OthmanAdi/planning-with-files:** 27,816 stars, MIT. 6 unique skills copied into 12 host folders.
- **EveryInc/compound-engineering-plugin:** 25,840 stars, MIT.
- **morluto/rea:** 419,497 stars. Reverse-engineering tool, so off-topic, but used below as a star anomaly.

Sources for all of the above: the `repos/OWNER/REPO` API and trees as above.

Test and eval infrastructure, counted as files under `test(s)/`, `eval(s)/` or `benchmark(s)/` directories:

| Repo | Test/eval files |
|---|---|
| gstack | 3,023 |
| GSD Core | 1,636 |
| ECC | 588 |
| addyosmani/agent-skills | 110 |
| superpowers | 70 |
| BMAD | 57 |
| wshobson | 47 |
| mattpocock | 0 |
| cloudflare | 0 |

Source: trees API.

Engagement proxies, measured 2026-11-02 01:55 UTC (source: `search/issues`, `repos/X/forks`, `repos/X/issues`, `repos/X/contributors` API). Columns:
- **Issues/10k stars:** issues opened in the last 30 days, per 10,000 stars.
- **Forks pushed:** share of the 100 oldest forks pushed after creation.
- **Unique authors:** distinct authors among the latest 100 issues.
- **Top contributor:** top contributor's share of commits.

| Repo | Issues/10k stars | Forks pushed | Unique authors | Top contributor |
|---|---|---|---|---|
| superpowers | 3.3 | 35% | 31 | 80% |
| mattpocock | 4.3 | 29% | 70 | 94% |
| ECC | 4.0 | 14% | 20 | 47% |
| gstack | 16.5 | 29% | 5 (top filer is the bot `capy-ai[bot]`) | 95% |
| addyosmani | 0.8 | 20% | 6 | 52% |
| ruflo | 30.4 | 43% | 7 (top filer `ruvnet` himself) | 92% |
| karpathy-skills | 0 | 8% | 0 | 61% |
| morluto/rea | 85.7 | 20% | 4 (owner filed 30 of the last 100) | 64% |
| control: astral-sh/uv | 10.8 | 38% | 16 | 32% |

### Inferences
- Superpowers, mattpocock and addyosmani are each one author's voice. Top contributors hold 80% to 94% of commits at superpowers and mattpocock. That gives consistent writing and makes them good import sources.
- ECC, ruflo, davila7, sickn33, alirezarezvani and awesome-copilot are aggregations. Raw SKILL.md counts overstate content: ECC's 1,068 files are 317 unique names, and GSD's 144 are 72.
- hesreallyhim/awesome-claude-code is CC BY-NC-ND, so its text cannot be adapted. Use it only as a pointer list.
- anthropics/skills mixes Apache-2.0 skills with proprietary ones (docx). Check each skill's LICENSE.txt before importing.
- SuperClaude looks stalled:
  - last commit 2026-09-27
  - 0 issues and 2 PRs in 30 days
  - 72 stars in the last 28 days
- The original GSD repo is archived. Development continues in open-gsd/gsd-core, at about 1/6 of the old star count.

### Gaps
- davila7/claude-code-templates stores agents under nested `cli-tool/components/agents/<category>/`. My regex counted only direct `agents/*.md` children, so its agent count is a floor, not a total.
- Open-issue counts from the repo endpoint include PRs. I did not split them.

## Q2. Are the stars credible? Inflation, AI bulk content, filler

### Takeaway
I cannot audit individual stargazers. Since GitHub's July 2026 restriction, the stargazer list returns 404 for every repo I don't administer, including facebook/react and torvalds/linux.

Star-curve shape and engagement proxies give a mixed picture:
- **Organic-looking:** superpowers and mattpocock. Their curves look like uv's or anthropics/skills', and they have real issue and fork activity.
- **Bursty, with weak engagement:** karpathy-skills, cloudflare/security-audit-skill, ruflo and gstack. These are flags, not proof.
- **Extreme outlier:** morluto/rea, with 416,531 of its 419,498 stars in the last 28 days.

Whatever their cause, star counts in this space don't track quality. A one-file CLAUDE.md repo has 228k stars, close to facebook/react's 252k, and superpowers' 310k exceeds react outright.

### Cited Findings
**Stargazer access.**
- Stargazer endpoints return 404 for non-admins. GraphQL returns `stargazerCount` but an empty `edges` list, verified on facebook/react, astral-sh/uv, torvalds/linux and all target repos on 2026-11-02. Only my own repo returned 200. Sources: `gh api repos/facebook/react/stargazers` and the GraphQL `stargazers` connection.
- GitHub limited stargazer data to "a repository's own admins and collaborators" in a changelog of June 30, 2026, per star-history.com. Its September 2026 update says GitHub "shipped a new star history endpoint that returns exact daily star counts for any public repository." — [star-history.com](https://www.star-history.com/blog/github-stargazer-api-restriction)
- The new endpoint is `GET /repos/{owner}/{repo}/stargazers/history`, announced as "privacy-safe star history data." This comes from the search-result summary; I didn't fetch the changelog page directly. — [GitHub changelog 2026-09-04](https://github.blog/changelog/2026-09-04-new-api-endpoint-provides-privacy-safe-star-history-data)

**Background on fake stars.**
- The CMU StarScout study (ICSE 2026) found about 6 million suspected fake stars across 18,617 repos. AI/LLM projects were the largest non-malicious category of recipients. This is from a search summary of the paper page. — [ICSE 2026 paper page](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/14/Six-Million-Suspected-Fake-Stars-on-GitHub-A-Growing-Spiral-of-Popularity-Contests)

**Daily star curves.** Retrieved 2026-11-02 via `stargazers/history`. Columns:
- **Peak:** largest single day and its date.
- **Peak/median:** peak divided by the median of active days.
- **Top 10% share:** share of all stars that came on the top 10% of days.
- **Last 28 days:** stars gained in the last 28 days.

| Repo | Peak (date) | Peak/median | Top 10% share | Last 28 days |
|---|---|---|---|---|
| astral-sh/uv (control) | 1,684 (2024-02-15) | 22.5 | 29.3% | 1,213 |
| anthropics/skills (control) | 2,390 | 6.0 | 25.9% | 7,442 |
| obra/superpowers | 3,922 (2026-03-17) | 5.9 | 26.5% | 16,801 (zero days with no stars) |
| mattpocock/skills | 7,093 (2026-04-28) | 6.5 | 27.1% | 34,271 |
| affaan-m/ECC | 6,989 (2026-03-31) | 9.1 | 30.0% | 23,293 |
| garrytan/gstack | 4,588 (2026-03-19) | 17.2 | 45.0% | 3,970 (launch spike, then decay) |
| ruvnet/ruflo | 2,325 (2026-05-03) | 27.4 | 44.9% | 7,020 |
| SuperClaude | 1,031 (2025-06-26) | 43.0 | 52.4% | 72 |
| karpathy-skills | 8,681 (2026-04-13) | 24.0 | 48.9% | 12,194 |
| cloudflare/security-audit-skill | 3,294 (2026-09-17) | 106.3 | 54.8% | 32,303 of 56,542 total (bursts Sept 16–18 and Oct 21–22) |
| morluto/rea | 54,047 (2026-10-12) | 13,511 | 73.5% | 416,531 of 419,498 total (20.2% zero days) |

anthropics/claude-code's single biggest day was 9,642.

**Throughput between snapshots.** From 01:55 to 04:42 UTC on 2026-11-02 (about 2.8 hours):

| Repo | Stars gained |
|---|---|
| superpowers | +82 |
| mattpocock | +100 |
| ECC | +78 |
| cloudflare | +113 |
| karpathy-skills | +88 |
| gstack | +3 |
| ruflo | +9 |

Source: two `repos/X` snapshots.

**Writing-quality samples, filler.** Read via `contents` API:
- VoltAgent `categories/04-quality-security/debugger.md` (913 words) is mostly keyword lists ("Breakpoint debugging / Time travel debugging / Statistical debugging"). It has no stopping rule or evidence gate, and it tells the agent to "Query context manager", which doesn't exist. — [file](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/HEAD/categories/04-quality-security/debugger.md)
- wshobson `plugins/debugging-toolkit/agents/debugger.md` is a 117-word generic five-step list. `plugins/comprehensive-review/agents/security-auditor.md` (1,146 words) is a capability brochure ("Masters vulnerability assessment… Zero-trust architecture…"). — [debugger](https://github.com/wshobson/agents/blob/HEAD/plugins/debugging-toolkit/agents/debugger.md), [security-auditor](https://github.com/wshobson/agents/blob/HEAD/plugins/comprehensive-review/agents/security-auditor.md)
- ECC `agents/security-reviewer.md` opens with a boilerplate "Prompt Defense Baseline" and centres on `npm audit` and eslint-plugin-security. ECC `.agents/skills/verification-loop/SKILL.md` is a list of npm/pyright/ruff commands piped through `head -30`. — [security-reviewer](https://github.com/affaan-m/ECC/blob/HEAD/agents/security-reviewer.md), [verification-loop](https://github.com/affaan-m/ECC/blob/HEAD/.agents/skills/verification-loop/SKILL.md)
- ruflo `.agents/skills/agent-load-balancer/SKILL.md` (1,294 words) wraps an agent profile with illustrative JavaScript (`workStealingScheduler`, `new PriorityQueue()`) that isn't connected to any code. Its frontmatter description is "Agent skill for load-balancer - invoke with $agent-load-balancer". This reads as generated bulk content. — [file](https://github.com/ruvnet/ruflo/blob/HEAD/.agents/skills/agent-load-balancer/SKILL.md)
- To ruflo's credit, `plugins/ruflo-security-audit/skills/security-scan/SKILL.md` admits "It is a pattern scanner, not a taint or auth-flow analyser." — [file](https://github.com/ruvnet/ruflo/blob/HEAD/plugins/ruflo-security-audit/skills/security-scan/SKILL.md)
- SuperClaude `agents/root-cause-analyst.md` (360 words) is abstract nouns only. `skills/confidence-check/SKILL.md` claims "Precision: 1.000 … Recall: 1.000 … 8/8 test cases passed" on its own 8 tests. — [root-cause-analyst](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/HEAD/plugins/superclaude/agents/root-cause-analyst.md), [confidence-check](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/HEAD/plugins/superclaude/skills/confidence-check/SKILL.md)

**Heavy and coupled files.**
- gstack `investigate/SKILL.md` runs 4,065 words. About 140 lines of preamble come before the method: frontmatter hooks that execute `$HOME/.claude/skills/gstack/freeze/bin/check-freeze.sh`, "gbrain" context queries, and a "Telemetry (run last)" section that writes to `$GSTACK_STATE_ROOT/analytics/`.
- gstack `review/SKILL.md` is 8,098 words. `cso/SKILL.md` requires the `gstack-cso-launcher` binary.
- Sources: [investigate](https://github.com/garrytan/gstack/blob/HEAD/investigate/SKILL.md), [review](https://github.com/garrytan/gstack/blob/HEAD/review/SKILL.md), [cso](https://github.com/garrytan/gstack/blob/HEAD/cso/SKILL.md)
- GSD Core agents are 6,000 to 7,000 words each (`gsd-verifier.md` 6,904; `gsd-plan-checker.md` 6,556). They have issue-number-labelled check sections ("#2962: zsh aborts…") and `@~/.claude/gsd-core/references/...` includes. — [gsd-verifier](https://github.com/open-gsd/gsd-core/blob/HEAD/agents/gsd-verifier.md), [gsd-plan-checker](https://github.com/open-gsd/gsd-core/blob/HEAD/agents/gsd-plan-checker.md)

**Ruflo security history.**
- Issue #1375, "Security Audit Summary: Multiple Critical Concerns" (2026-03-17), alleges several problems:
  - MCP tool descriptions with hidden instructions to add the repo owner as a contributor (citing #1323, which now returns 404)
  - an obfuscated `preinstall` that deleted npx and npm cache entries in v3.1.0-alpha.55 to 3.5.2
  - artifacts that persist after uninstall
  - a SQL injection
- The maintainer replied on 2026-03-19, reporting fixes in v3.5.40: preinstall removed, parameterised queries, SECURITY.md, and a `ruflo cleanup` command. He said a search found no contributor-adding instructions in current tool descriptions.
- A further commenter on 2026-04-04 says a separate audit of v3.5.51 "confirmed" hidden instructions in tool descriptions. The issue was closed as completed on 2026-03-19.
- Source: [issue #1375](https://github.com/ruvnet/ruflo/issues/1375). I did not verify the claims in code.
- A ruflo review says it found no independent report of a production federation deployment and calls the project an experiment. This is from a search summary only. — [andrew.ooo](https://andrew.ooo/posts/ruflo-review-agent-harness-claude-code-codex/)

**Reception of superpowers.**
- Positive but costly:
  - The full loop is called "token-intensive"
  - The top Reddit comment calls it "bloated"
  - One Hacker News commenter said Claude "makes more mistakes" with it
  - Advice: on newer models, run thin with brainstorm and review only
- That article is an unsigned editorial on a directory that promotes its own `superpowers-*` ports, so it has a commercial interest. — [mcp.directory](https://mcp.directory/blog/superpowers-skill-worth-it-2026)
- A Pulumi blog post spent "a few weeks with each" of Superpowers, GSD and gstack, with no controlled benchmark. Its advice by failure mode:
  - quality drops → Superpowers
  - context rot → GSD
  - scope creep → gstack plus Superpowers TDD

  It adds that GSD's orchestrator "never touches source files" and spawns fresh-context subagents per task. — [Pulumi](https://www.pulumi.com/blog/claude-code-orchestration-frameworks/)
- A practitioner built a React ordering app:
  - Superpowers-built modules were "the most stable code", at heavy token cost
  - gstack's `/qa` caught visual bugs, but it has too many roles, and its `/learn` captured style preferences rather than error patterns

  This is qualitative only. — [zerofuturetech](https://zerofuturetech.substack.com/p/i-deep-tested-three-claude-code-harness)
- One author ran 12 sessions with and without Superpowers and reports 14% fewer tokens and better code, but not on every task. This is a search snippet; I didn't fetch it. — [towardsai](https://pub.towardsai.net/i-installed-40-claude-skills-three-survived-29fe64f802ec)

### Inferences
- **Superpowers and mattpocock:**
  - their curves look like uv's and anthropics/skills', with peak/median near 6 and the top 10% of days near 26–27%
  - they have real issue authors (31 and 70 unique per 100 issues)
  - their pushed-fork rates are near uv's

  Their stars look organic, if hype-amplified.
- **morluto/rea:** about 417k stars in 28 days, a single day of 54k (5.6 times claude-code's best day), and 20% zero days. That is either an extraordinary viral event or manipulation. Either way, the absolute numbers in this ecosystem are unreliable as a quality signal.
- **cloudflare/security-audit-skill and karpathy-skills:** bursty curves with light engagement. Karpathy-skills had 0 issues in 30 days for 228k stars. These stars measure virality, and possibly campaigns. Cloudflare's content is nonetheless high quality.
- Aggregations show the AI bulk-content signature:
  - keyword-list personas
  - fictional code blocks
  - near-duplicate files in many languages and host folders
  - stack-specific commands passed off as general skills

  The less filler a repo has, the better its stars tracked its quality. Its star count still didn't predict quality on its own.
- gstack telemetry is local by default: it writes to `$GSTACK_STATE_ROOT/analytics/`. I did not verify whether its binaries send anything remotely. It runs hooks from `$HOME` regardless. Importing gstack text without its binaries would break it.

### Gaps
- No per-account stargazer audit was possible. Without that data a bought burst and a viral launch look the same.
- I didn't fetch the Evan Schwartz Hacker News review or the HN thread itself; I saw only search summaries.
- I found no independent controlled benchmark of any framework.

## Q3. Which skills or agents are worth importing, and what overlaps with Puck

### Takeaway
About eight imports add something Puck lacks, all MIT or Apache-2.0. Each should be rewritten into Puck's template, naming capabilities rather than host tools, not copied.

| # | Import | Source path | What Puck lacks | Overlap with Puck | Verdict |
|---|---|---|---|---|---|
| 1 | Debugging skill | mattpocock `skills/engineering/diagnosing-bugs/SKILL.md` (1,427 words) + superpowers `skills/systematic-debugging/SKILL.md` (1,454 words) | No debug procedure at all | `task` already has the three-failed-attempts stop | **Import** (highest value) |
| 2 | Verification-before-completion claim gate | superpowers `skills/verification-before-completion/SKILL.md` (580 words) | The claim-to-evidence table, distrust of subagent reports, and the revert-must-fail proof for regression tests | `context/instructions/global.md` already says "To claim something is done, show the command you ran and its output"; `task` steps 6 and 9 | **Patch** `task` (or `global.md`); partial overlap |
| 3 | Receiving review | superpowers `skills/receiving-code-review/SKILL.md` (913 words) | Verifying each finding before fixing it | `review` step 3 | **Patch** `review` |
| 4 | Grilling | mattpocock `skills/productivity/grilling/SKILL.md` (333 words) | Design-tree rounds, fact lookup by subagent | `plan` interviews with recommendations | **Patch** `plan` |
| 5 | TDD | mattpocock `skills/engineering/tdd/SKILL.md` (574 words) | No test-first discipline | None | **Import** (medium) |
| 6 | Security review | cloudflare `skills/security-audit/SKILL.md` (3,115 words + companions), guidance mode only; addyosmani `agents/security-auditor.md` (738 words) as a lighter checklist | No security review | None | **Import** (medium-high) |
| 7 | Silent-failure lens | anthropics/claude-plugins-official `plugins/pr-review-toolkit/agents/silent-failure-hunter.md` (1,170 words, Apache-2.0) | Reviewer has no error-handling lens | `reviewer` covers general defects | **Import** as a reviewer lens or second agent |
| 8 | Writing-skills pressure testing | superpowers `skills/writing-skills/SKILL.md` (2,409 words) | Behavioural tests for new skills | `retro` writes trigger evals only | **Patch** `retro` / skill authoring |

### Cited Findings
1. **Debugging.** No Puck skill covers this; `task` has only the generic "three failed attempts" stop.
   - mattpocock/diagnosing-bugs makes building "a tight pass/fail signal" Phase 1 ("This is the skill"). It includes:
     - ten ways to construct a feedback loop
     - a completion criterion: "one command … that you have already run at least once", red-capable, deterministic, fast, and runnable by the agent
     - "Generate 3–5 ranked hypotheses", each falsifiable
     - tagging debug logs `[DEBUG-a4f2]` so cleanup is one grep
     - a "Phase 6: Cleanup" checklist

     [file](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/diagnosing-bugs/SKILL.md)
   - superpowers/systematic-debugging adds:
     - the Iron Law "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
     - instrumenting each boundary in multi-component systems
     - "If ≥ 3 [fixes failed]: STOP and question the architecture"
     - a red-flags thought list

     [file](https://github.com/obra/superpowers/blob/HEAD/skills/systematic-debugging/SKILL.md)
   - gstack `investigate` has the same 3-strike rule plus a "Scope Lock" on edits. Its method is sound, but it is buried in tooling. [file](https://github.com/garrytan/gstack/blob/HEAD/investigate/SKILL.md)
   - Rejected alternatives: VoltAgent debugger, wshobson debugger and debugging-strategies, SuperClaude root-cause-analyst (all filler; see Q2).

2. **Claim gate.** Puck's `task` already requires `puck task check` for every step. Puck's `context/instructions/global.md` already says "To claim something is done, show the command you ran and its output", so the core rule exists. What's missing is the detail. The superpowers skill adds:
   - "If you haven't run the verification command in this message, you cannot claim it passes"
   - a five-step gate function: identify, run, read, verify, then claim
   - a "Claim | Requires | Not Sufficient" table, including "Agent completed | VCS diff shows changes | Agent reports 'success'"
   - the regression-test proof "Revert fix → Run (MUST FAIL) → Restore"

   [file](https://github.com/obra/superpowers/blob/HEAD/skills/verification-before-completion/SKILL.md)

3. **Receiving review.** It overlaps with Puck `review` step 3, "Fix real defects, and record any you reject with a reason". It adds:
   - "VERIFY: Check against codebase reality" before implementing
   - "IF any item is unclear: STOP - do not implement anything yet"
   - one item at a time, testing each
   - no performative agreement

   Patch `review` rather than adding a skill. [file](https://github.com/obra/superpowers/blob/HEAD/skills/receiving-code-review/SKILL.md)

4. **Grilling.** It overlaps strongly with Puck `plan`, which already interviews a few questions at a time with a recommendation each. It adds:
   - a "design tree" whose "frontier" of unblocked decisions is asked in numbered rounds
   - "Word each question so 'yes' accepts your recommended answer"
   - "Finding facts is your job … dispatch a sub-agent with a fresh context window"
   - done when the frontier is empty

   [file](https://github.com/mattpocock/skills/blob/HEAD/skills/productivity/grilling/SKILL.md)

5. **TDD.** mattpocock/tdd covers:
   - testing at agreed seams through public interfaces
   - named anti-patterns: implementation-coupled tests, "Tautological" tests where the expected value is recomputed, and "Horizontal slicing"
   - "Red before green", one slice at a time
   - refactoring belongs to review, not the loop

   [file](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/tdd/SKILL.md)

   Superpowers' TDD (1,475 words) is more absolute, with an Iron Law and a "Common Rationalizations" table. Use its rationalisation rows only. [file](https://github.com/obra/superpowers/blob/HEAD/skills/test-driven-development/SKILL.md)

   The mattpocock version depends on its `codebase-design` skill and GLOSSARY.md conventions. Strip those references.

6. **Security review.** Puck has no security review today.
   - The cloudflare skill is agent-neutral by design: "**Parent** is the agent that coordinates… **Task tool** is the platform's delegation or sub-agent mechanism… Use equivalent platform capabilities". That matches Puck's rule of naming capabilities, not host tools.
   - It has a guidance mode and a full-audit mode, and forbids running target code outside an OS-enforced sandbox. Its bar: "A candidate without a concrete affected principal, resource, or security outcome is not a confirmed finding."
   - Its full mode is very heavy: write isolation, descriptor-based file promotion, coverage ledgers. Import only guidance mode and the evidence bar.

   [file](https://github.com/cloudflare/security-audit-skill/blob/HEAD/skills/security-audit/SKILL.md), [addy agent](https://github.com/addyosmani/agent-skills/blob/HEAD/agents/security-auditor.md)

7. **Silent-failure lens.** The agent inventories every catch block, fallback and null-coalesce, and asks whether each hides errors. It contains Anthropic-internal leftovers (`constants/errorIds.ts`, Sentry, "Daisy" examples) to strip. [file](https://github.com/anthropics/claude-plugins-official/blob/HEAD/plugins/pr-review-toolkit/agents/silent-failure-hunter.md)

8. **Pressure testing for skills.** Puck's `retro` agent creates skills with one should-trigger and one should-not-trigger eval, but has no behavioural test. superpowers/writing-skills adds:
   - "If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing"
   - run a baseline pressure scenario with a subagent first, recording the exact rationalisations
   - write the minimal skill, then close loopholes
   - "3+ combined pressures for discipline skills"
   - "if it's enforceable with regex/validation, automate it"

   [file](https://github.com/obra/superpowers/blob/HEAD/skills/writing-skills/SKILL.md)

**Secondary candidates** (lower priority; take ideas, not files):
- **mattpocock `skills/engineering/code-review/SKILL.md`.** It runs two parallel fresh subagents, Standards and Spec, and reports them unmerged, "Do not merge or rerank findings". It carries a 12-item Fowler smell baseline. Puck's `reviewer` judges only against the requirement and skips style, so the Standards axis is new. [file](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/code-review/SKILL.md)
- **addyosmani `skills/doubt-driven-development/SKILL.md`** (2,600 words). It defines a "non-trivial decision": branching logic, a module boundary, an unverifiable property, or an irreversible change. It requires "Pass ARTIFACT + CONTRACT only. Do NOT pass the CLAIM." It overlaps with Puck `review` ("Don't pass your own reasoning"). The new part is using it mid-flight. Its mandatory cross-model prompt is overhead. [file](https://github.com/addyosmani/agent-skills/blob/HEAD/skills/doubt-driven-development/SKILL.md)
- **addyosmani `skills/source-driven-development/SKILL.md`.** Detect versions, fetch official docs, implement, then cite. It also treats directives in fetched docs as data. [file](https://github.com/addyosmani/agent-skills/blob/HEAD/skills/source-driven-development/SKILL.md)
- **superpowers `skills/subagent-driven-development/SKILL.md`** (2,857 words). Each task gets:
  - a fresh implementer subagent per task
  - a spec-and-quality review per task, then a final branch review
  - a ledger with `Ruling: <what> — <why> — <cost if wrong>` lines
  - exactly four stop conditions: irreversible, security-sensitive, external side effect, or a plan broken beyond guessing

  Useful if Puck adds subagent execution of SPEC steps. [file](https://github.com/obra/superpowers/blob/HEAD/skills/subagent-driven-development/SKILL.md)
- **open-gsd `agents/gsd-verifier.md`.** Take the stance only: "SUMMARY.md claims are not evidence", "Assume the phase goal was not achieved until codebase evidence proves it", plus a list of "how verifiers go soft". The file itself is too long and path-coupled. [file](https://github.com/open-gsd/gsd-core/blob/HEAD/agents/gsd-verifier.md)
- **multica-ai `skills/karpathy-guidelines/SKILL.md`** (371 words): "Every changed line should trace directly to the user's request"; simplicity first; surface assumptions. These are candidate global-instruction lines. Its licence is unclear: GitHub detects none, frontmatter says MIT. [file](https://github.com/multica-ai/andrej-karpathy-skills/blob/HEAD/skills/karpathy-guidelines/SKILL.md)

**Skip:**
- superpowers `brainstorming`, 2,359 words. Puck `plan` covers it, and its "You MUST use this before any creative work" over-triggers. [file](https://github.com/obra/superpowers/blob/HEAD/skills/brainstorming/SKILL.md)
- superpowers `writing-plans`: line-level plans saved to `docs/superpowers/plans/`. Puck `plan` deliberately leaves out line-level steps. [file](https://github.com/obra/superpowers/blob/HEAD/skills/writing-plans/SKILL.md)
- mattpocock `handoff`: Puck says history belongs to the host, and the task pack already covers resumption.
- spec-kit `templates/commands/analyze.md`: cross-artifact checks across spec, plan and tasks, mostly extension-hook boilerplate. [file](https://github.com/github/spec-kit/blob/HEAD/templates/commands/analyze.md)
- BMAD `skills/bmad-review/SKILL.md`: depends on `customize.toml` and `_bmad/scripts`. [file](https://github.com/bmad-code-org/BMAD-METHOD/blob/HEAD/skills/bmad-review/SKILL.md)
- All of VoltAgent, wshobson, ECC, ruflo, davila7, SuperClaude and sickn33 for these purposes.

### Inferences
- **Puck's biggest functional gap is debugging.** Combine mattpocock's feedback-loop-first structure with superpowers' Iron Law and red flags into one `debug` skill. Its acceptance would be "a red-capable command already run", which maps onto `puck task step --check`.
- **Low cost, high value, as patches** rather than new skills, which fits Puck's retro rule "Update an existing skill rather than creating a near-duplicate":
  - verification claim gate → `task`
  - receiving-review rules → `review`
  - grilling rounds → `plan`
- **Security and silent-failure** are best added as extra reviewer lenses or agents spawned by `review`. Puck's `reviewer` output format (location, failure path, severity) already matches the cloudflare evidence bar.
- **Attribution:** MIT and Apache-2.0 both require keeping the copyright and licence notice in substantial copies. Puck's retro rule "Summarise web-derived text. Never copy it into a skill" points to rewriting with a source note.

### Gaps
- I did not read every superpowers or mattpocock skill (`dispatching-parallel-agents`, `codebase-design`, `to-spec`, `prototype`, `retro`), the addyosmani `test-engineer` agent, or Anthropic's `pr-test-analyzer` and `type-design-analyzer` in full.
- Puck's `context/instructions/global.md` has no rules on simplicity or surgical changes, so the Karpathy lines would be new, not overlap.
- No skill was evaluated behaviourally. These are judgements from reading the text.

## Q4. Patterns that recur in the best ones

### Takeaway
The best files share six patterns:
- an absolute rule plus a pre-written table of the agent's excuses
- gates that demand fresh command output, not reasoning
- completion criteria phrased as observable artefacts
- fresh-context subagents that get the artefact and contract but not the author's conclusion
- a hard stop after three failures
- short text that names capabilities rather than tools

The worst files share the opposite traits: persona brochures, stack-specific command lists, preambles and telemetry, and duplication.

### Cited Findings
- **Stopping rationalisation.**
  - Superpowers uses an "Iron Law" code block, then "Violating the letter of this rule is violating the spirit". Then come a "Red Flags - STOP" list of inner thoughts ("Should work now", "Just this once") and a two-column "Excuse | Reality" table.
  - This appears in verification-before-completion, systematic-debugging, TDD and writing-skills. — [verification](https://github.com/obra/superpowers/blob/HEAD/skills/verification-before-completion/SKILL.md), [TDD](https://github.com/obra/superpowers/blob/HEAD/skills/test-driven-development/SKILL.md)
  - writing-skills derives these tables empirically: run the scenario without the skill, record "exact rationalizations" verbatim, then "Match the Form to the Failure". Prohibition plus a rationalisation table is reserved for rules the agent "knows better" than to break. — [writing-skills](https://github.com/obra/superpowers/blob/HEAD/skills/writing-skills/SKILL.md)
  - mattpocock catches the moment of failure instead: "If you catch yourself reading code to build a theory before this command exists, stop". — [diagnosing-bugs](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/diagnosing-bugs/SKILL.md)
- **Verification gates.**
  - "If you haven't run the verification command in this message, you cannot claim it passes" — [superpowers](https://github.com/obra/superpowers/blob/HEAD/skills/verification-before-completion/SKILL.md)
  - The Phase 1 gate is a named command "already run at least once (show the invocation and its output, redacted)" — [mattpocock](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/diagnosing-bugs/SKILL.md)
  - "Assume the phase goal was not achieved until codebase evidence proves it" — [GSD verifier](https://github.com/open-gsd/gsd-core/blob/HEAD/agents/gsd-verifier.md)
  - A finding needs "a concrete affected principal, resource, or security outcome" — [cloudflare](https://github.com/cloudflare/security-audit-skill/blob/HEAD/skills/security-audit/SKILL.md)
- **Subagent use.**
  - Fresh context per role; strip the author's reasoning ("Pass ARTIFACT + CONTRACT only. Do NOT pass the CLAIM") — [addyosmani](https://github.com/addyosmani/agent-skills/blob/HEAD/skills/doubt-driven-development/SKILL.md)
  - Parallel axes that are deliberately not merged — [mattpocock code-review](https://github.com/mattpocock/skills/blob/HEAD/skills/engineering/code-review/SKILL.md)
  - Subagents for fact-finding while the user decides — [mattpocock grilling](https://github.com/mattpocock/skills/blob/HEAD/skills/productivity/grilling/SKILL.md)
  - A fresh implementer per task, with review gates and a rulings ledger — [superpowers SDD](https://github.com/obra/superpowers/blob/HEAD/skills/subagent-driven-development/SKILL.md)
  - Never trust a subagent's success report; check the diff — [superpowers verification](https://github.com/obra/superpowers/blob/HEAD/skills/verification-before-completion/SKILL.md)
  - An orchestrator that "never touches source files" — [Pulumi on GSD](https://www.pulumi.com/blog/claude-code-orchestration-frameworks/)
- **Three-strike stop.**
  - superpowers: "If ≥ 3: STOP and question the architecture" — [systematic-debugging](https://github.com/obra/superpowers/blob/HEAD/skills/systematic-debugging/SKILL.md)
  - gstack: "3-strike rule: If 3 hypotheses fail, STOP" — [investigate](https://github.com/garrytan/gstack/blob/HEAD/investigate/SKILL.md)
  - addyosmani doubt cycle stops after "3 cycles" — [doubt-driven](https://github.com/addyosmani/agent-skills/blob/HEAD/skills/doubt-driven-development/SKILL.md)
  - Puck `task` step 5 already has this rule.
- **Harness neutrality.**
  - Cloudflare defines its role terms abstractly ("Use equivalent platform capabilities") — [file](https://github.com/cloudflare/security-audit-skill/blob/HEAD/skills/security-audit/SKILL.md)
  - Superpowers keeps per-host tool maps in references such as `using-superpowers/references/codex-tools.md`, and its `using-superpowers` section "User Instructions" defers to the user's instruction file — [file](https://github.com/obra/superpowers/blob/HEAD/skills/using-superpowers/SKILL.md)
  - mattpocock ships `agents/openai.yaml` per skill — [tree](https://github.com/mattpocock/skills)
- **Anti-patterns to avoid.**
  - gstack: per-skill preambles, telemetry and `$HOME` hook scripts — [investigate](https://github.com/garrytan/gstack/blob/HEAD/investigate/SKILL.md)
  - GSD: 6,000+ word agents accreted from issue numbers — [plan-checker](https://github.com/open-gsd/gsd-core/blob/HEAD/agents/gsd-plan-checker.md)
  - ECC: duplication across translations and host folders, 1,068 files for 317 names — [tree](https://github.com/affaan-m/ECC)
  - superpowers `using-superpowers`: `<EXTREMELY-IMPORTANT>` shouting to force skill loading — [file](https://github.com/obra/superpowers/blob/HEAD/skills/using-superpowers/SKILL.md)
  - Critics' token-cost complaints about full-methodology installs — [mcp.directory](https://mcp.directory/blog/superpowers-skill-worth-it-2026)

### Inferences
- Puck already has the structural pieces the best frameworks converge on:
  - acceptance checks as commands
  - fresh-context review without the author's reasoning
  - the three-attempt stop
  - retro with evals
- What it lacks is the anti-rationalisation layer: iron-law statements, red-flag thought lists and excuse tables in `task`, `review` and a new `debug` skill. It also lacks behavioural pressure tests for new skills.
- To keep within Puck's own goal of optimising context, borrow the rules and tables, not the length. The best sources are 330–1,500 words. The worst are 4,000–8,000.

### Gaps
- I found no controlled evidence that rationalisation tables or iron laws measurably change agent behaviour. Superpowers' own pressure-testing claims are self-reported, and the only quantitative reception data (14% fewer tokens, 12 sessions) is an unfetched search snippet.
