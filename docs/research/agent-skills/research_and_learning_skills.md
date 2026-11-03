# Research and learning skills worth importing into Puck (milestone 3)

## Which high-star repos ship deep-research or multi-source research skills or agents?

### Takeaway
Nearly every high-star research repo is a search pipeline with little or no verification, or a full application that needs paid keys. The best parts for Puck are small: Hermes' `grounded-citations` ledger, Tavily's subtopic-splitting rule and Claude-Obsidian's "research first, merge later" bound. Puck's planned `claim-checker` is already stronger than most of what these repos ship.

### Cited Findings

**How this data was collected**
- All star, licence and date data came from live `gh` calls on 2026-11-01 local time; the last pull was at 2026-11-02T01:57:50Z, so some dates read 2026-11-02. Web checks ran on 2026-11-02.
- "Last commit" comes from the commits API on the default branch. Rows marked `p:` show `pushed_at` only, because no commit call was made for that repo.
- Star counts moved slightly during the run (`mattpocock/skills` went 309,286 to 309,290). The latest figure seen is used.
- `exa-labs/skills` returned 404. Exa's skills live inside [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server/tree/main/plugins/exa/skills).
- `K-Dense-AI/claude-scientific-skills` now resolves to [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills).

**Research candidates**

| Repo | Stars | Licence | Last commit | Key paths | External dependencies | Works with generic web search only? |
|---|---|---|---|---|---|---|
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 30,418 | Apache-2.0 | 2026-10-10 | [`gpt_researcher/skills/researcher.py`](https://github.com/assafelovic/gpt-researcher/blob/main/gpt_researcher/skills/researcher.py), [`skills/gpt-researcher/SKILL.md`](https://github.com/assafelovic/gpt-researcher/blob/main/skills/gpt-researcher/SKILL.md) | README quickstart sets OpenAI and Tavily keys | No. It is an application; the skill file is a 317-byte Codex/MCP pointer |
| [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research) | 12,681 | MIT | 2026-08-10, archived | [`src/open_deep_research/deep_researcher.py`](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/deep_researcher.py) | Python application; keys not checked | No. Archived, reference only |
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | 31,765 | MIT | 2025-09-30 | Not inspected; already covered in Puck's research notes | Not checked | No. Application, 13 months idle |
| [dzhng/deep-research](https://github.com/dzhng/deep-research) | 19,869 | MIT | 2026-04-11 | Not inspected | Not checked | Unknown |
| [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | 20,092 | Apache-2.0 | p: 2026-02-27 | Not inspected | Not checked | Unknown |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 84,842 | MIT | 2026-11-02 | [`skills/public/deep-research/SKILL.md`](https://github.com/bytedance/deer-flow/blob/main/skills/public/deep-research/SKILL.md) | None for the skill text | Yes, as methodology |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 294,833 | MIT | 2026-10-30 | [`.agents/skills/deep-research/SKILL.md`](https://github.com/affaan-m/ECC/blob/main/.agents/skills/deep-research/SKILL.md) | Firecrawl and Exa MCP servers | No, as written |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 66,262 | MIT | 2026-11-01 | [`skills/last30days/SKILL.md`](https://github.com/mvanhorn/last30days-skill/blob/main/skills/last30days/SKILL.md) (31.7 KB), [`references/research-runbook.md`](https://github.com/mvanhorn/last30days-skill/blob/main/skills/last30days/references/research-runbook.md) (73.5 KB) | Python 3.12+, Node, yt-dlp; many optional keys and browser tokens | Partly. Needs a shell; the README says it degrades to web-only with no keys |
| [firecrawl/skills](https://github.com/firecrawl/skills) | 142 | ISC | 2026-10-22 | [`skills/workflows/firecrawl-deep-research/SKILL.md`](https://github.com/firecrawl/skills/blob/main/skills/workflows/firecrawl-deep-research/SKILL.md) | `FIRECRAWL_API_KEY` required | No |
| [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | 5,208 | MIT | 2026-11-02 | [`plugins/exa/skills/search/SKILL.md`](https://github.com/exa-labs/exa-mcp-server/blob/main/plugins/exa/skills/search/SKILL.md), [`references/source-quality.md`](https://github.com/exa-labs/exa-mcp-server/blob/main/plugins/exa/skills/search/references/source-quality.md) | Exa MCP | No, but the reference text is portable |
| [tavily-ai/skills](https://github.com/tavily-ai/skills) | 491 | MIT | 2026-10-30 | [`skills/tasks/tavily-research/SKILL.md`](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/SKILL.md), [`references/researcher.md`](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/references/researcher.md) | `tvly` CLI | No, as written. The procedure is portable |
| [mattpocock/skills](https://github.com/mattpocock/skills) (research) | 309,290 | MIT | 2026-10-31 | [`skills/engineering/research/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md) (832 bytes) | None | Yes |
| [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | 1,204 | None | 2026-04-11 | [`scripts/verify_claim_support.py`](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/scripts/verify_claim_support.py), [`scripts/verify_citations.py`](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/scripts/verify_citations.py), [`reference/quality-gates.md`](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/reference/quality-gates.md) | Python scripts | Mostly. Needs a shell |
| [Weizhena/Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills) | 2,464 | MIT | 2026-08-23 | [`agents/web-search-agent.md`](https://github.com/Weizhena/Deep-Research-skills/blob/master/agents/web-search-agent.md), `skills/research-codex-en/` | None seen | Yes, but names host tools and a home-directory path |
| [tonyazhuuki/deep-research-skill](https://github.com/tonyazhuuki/deep-research-skill) | 32 | MIT | 2026-10-22 | [`research/SKILL.md`](https://github.com/tonyazhuuki/deep-research-skill/blob/main/research/SKILL.md), [`codex/deep-research/references/evidence.md`](https://github.com/tonyazhuuki/deep-research-skill/blob/main/codex/deep-research/references/evidence.md) | Semantic Scholar, PubMed and CrossRef checks by script | Partly |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 54,898 | CC BY-NC 4.0 by LICENSE text; API reports NOASSERTION | 2026-11-02 | [`deep-research/SKILL.md`](https://github.com/Imbad0202/academic-research-skills/blob/main/deep-research/SKILL.md) (52.5 KB) | Multi-agent host | Partly. Far over Puck's size limit |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 55,677 | MIT | 2026-10-26 | [`skills/scholar-evaluation/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scholar-evaluation/SKILL.md), [`skills/research-lookup/SKILL.md`](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/research-lookup/SKILL.md), `skills/literature-review/` | `research-lookup`: Parallel CLI or key, optional OpenRouter. `scholar-evaluation`: local only | Mixed |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (citations) | 259,523 | MIT | 2026-11-01 | [`skills/research/grounded-citations/SKILL.md`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/SKILL.md), [`scripts/sources.py`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/scripts/sources.py) | Stdlib Python 3 only, per the skill | Yes, with a shell for the script |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (research) | 16,057 | MIT | 2026-10-22 | [`skills/autoresearch/SKILL.md`](https://github.com/AgriciDaniel/claude-obsidian/blob/main/skills/autoresearch/SKILL.md) | Web access | Yes |
| [jamditis/claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism) | 444 | MIT | 2026-10-30 | [`journalism-core/skills/fact-check-workflow/SKILL.md`](https://github.com/jamditis/claude-skills-journalism/blob/master/journalism-core/skills/fact-check-workflow/SKILL.md) | None seen | Yes |

**Official and last30days-style findings**
- The [official plugin marketplace](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) lists 315 plugins. Keyword filtering found `exa`, `tavily` and `youdotcom-agent-skills` as search or research plugins, and `learning-output-style` and `learn-with-coursera` for learning. No general deep-research plugin from Anthropic appeared.
- [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills) has no research skill. Its closest item is [`discernment-nudge`](https://github.com/anthropics/skills/blob/main/skills/discernment-nudge/SKILL.md), which appends 2-3 specific questions about checking facts, reasoning and missing context, at most once per conversation.
- last30days uses engagement as its ranking signal: "Reddit upvotes. X likes. YouTube transcripts", per its [README](https://github.com/mvanhorn/last30days-skill/blob/main/README.md). Its [frontmatter](https://github.com/mvanhorn/last30days-skill/blob/main/skills/last30days/SKILL.md) lists optional secrets including `AUTH_TOKEN` and `CT0`.
- The same [README](https://github.com/mvanhorn/last30days-skill/blob/main/README.md) says Reddit, Hacker News, Polymarket and GitHub need no keys. It also says the research topic is sent to a provider when a reasoning key is set for reranking.
- [`tavily-research`](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/SKILL.md) uses 3 subtopics when unsure, 4 for a comparison with separate criteria and 5 for separate entities, regions or domains. Its [researcher reference](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/references/researcher.md) expects about eight searches and stops by twelve. A keyword search of its SKILL.md found no verification step.
- [`firecrawl-deep-research`](https://github.com/firecrawl/skills/blob/main/skills/workflows/firecrawl-deep-research/SKILL.md) asks how long the run may take, then maps the answer to Quick, Thorough or Exhaustive. It requires a contrarian-views section.
- deer-flow's [description](https://github.com/bytedance/deer-flow/blob/main/skills/public/deep-research/SKILL.md) tells the model to use it "instead of WebSearch for ANY question requiring web research". A keyword search found a pre-writing sufficiency check but no claim-level verification.
- ECC's [rule](https://github.com/affaan-m/ECC/blob/main/.agents/skills/deep-research/SKILL.md) is lighter still: if only one source says it, flag it as unverified.
- Mattpocock's [`research`](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md) is three steps: use a fresh background agent, follow each claim to primary sources, and write one cited Markdown file.
- Claude-Obsidian's [autoresearch](https://github.com/AgriciDaniel/claude-obsidian/blob/main/skills/autoresearch/SKILL.md) says web findings and worker drafts "do not become canonical vault knowledge merely because they were retrieved". Its grep-visible default is at most three rounds, five fetched sources per round and fifteen drafted pages.
- Exa's [source-quality reference](https://github.com/exa-labs/exa-mcp-server/blob/main/plugins/exa/skills/search/references/source-quality.md) separates practitioners from commentators and lists noise signals such as misaligned incentives and positive-only advice.
- The 199-biotechnologies skill's [autonomy rule](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/SKILL.md) says to stop only for critical errors or incomprehensible queries, which skips clarification.

### Inferences
- [I] No high-star search skill is worth installing. Adapt `tavily-research`'s splitting rule and stop limits, because they fit Puck's "effort cap" with almost no text.
- [I] last30days adds a different kind of source: dated community sentiment. It is out of scope for milestone 3 because of its size, shell use and browser-token handling. Consider it later as an optional, user-invoked tool.
- [I] Popularity says little here. The most useful verification code found sits in a 1,204-star repo and in one skill inside a large agent repo.

### Gaps
- I read `SKILL.md` files and excerpts, not whole repos, and did no security audit of any script.
- `dzhng/deep-research`, `Alibaba-NLP/DeepResearch` and STORM were not inspected beyond metadata, and STORM is already covered in Puck's notes.
- `sandbaseai/sandbase-skills`, `WenyuChiou/ai-research-skills` and `GiaSip/giasip-skills` surfaced in curated lists but were not read.
- `anthropics/knowledge-work-plugins` `enterprise-search` skills appeared in the tree and were not read.
- I did not count lines for most skills, so sizes are in bytes.

## Which repos ship learning skills: tutoring, Socratic teaching, quizzes, flashcards, Feynman, wiki and note systems?

### Takeaway
The best learning designs sit in small or unlicensed repos. `mattpocock/skills` teach gives the workspace and record structure, `amosblomqvist/learn` gives the diagnostic probe, and `learning-opportunities` gives the pause discipline. For the wiki, `Astro-Han/karpathy-llm-wiki` is the closest match, and `kfchou/wiki-skills` has the best lint pipeline.

### Cited Findings

**Tutoring, quizzes and teaching**

| Repo | Stars | Licence | Last commit | Key paths | External dependencies | Works with generic web search only? |
|---|---|---|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) (teach) | 309,290 | MIT | 2026-10-31 | [`skills/productivity/teach/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) plus `MISSION-`, `LEARNING-RECORD-`, `RESOURCES-` and `GLOSSARY-FORMAT.md` | None | Yes |
| [amosblomqvist/learn](https://github.com/amosblomqvist/learn) | 3,998 | None | 2026-08-25 | [`skills/teach/SKILL.md`](https://github.com/amosblomqvist/learn/blob/main/skills/teach/SKILL.md), [`agents/researcher.md`](https://github.com/amosblomqvist/learn/blob/main/agents/researcher.md) | Pi harness; `quiz` and `ask_user_question` extensions | Yes as ideas; tools need replacing |
| [OJ102/ProjectSchola](https://github.com/OJ102/ProjectSchola) | 5 | MIT for own code; inherited parts unlicensed | 2026-10-22 | [`skills/teach/SKILL.md`](https://github.com/OJ102/ProjectSchola/blob/main/skills/teach/SKILL.md), [`skills/ingest/SKILL.md`](https://github.com/OJ102/ProjectSchola/blob/main/skills/ingest/SKILL.md), [`hooks/source/librarian-prompt.md`](https://github.com/OJ102/ProjectSchola/blob/main/hooks/source/librarian-prompt.md) | Claude Code hooks and plugin variables | No, as written |
| [DrCatHicks/learning-opportunities](https://github.com/DrCatHicks/learning-opportunities) | 2,531 | CC-BY-4.0 | 2026-08-19 | [`learning-opportunities/skills/learning-opportunities/SKILL.md`](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md), [`resources/PRINCIPLES.md`](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/resources/PRINCIPLES.md) | None | Yes |
| [GarethManning/education-agent-skills](https://github.com/GarethManning/education-agent-skills) | 939 | CC BY-SA 4.0 for educational content; API reports NOASSERTION | 2026-10-22 | [`skills/student-learning/retrieve-first-gate/SKILL.md`](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md), [`skills/student-learning/progressive-hint-ladder/SKILL.md`](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/progressive-hint-ladder/SKILL.md) | None | Yes |
| [SenmuuuuW/universal-diagnostic-tutor-skill](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill) | 256 | MIT | 2026-09-24 | [`skills/universal-diagnostic-tutor/SKILL.md`](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/skills/universal-diagnostic-tutor/SKILL.md), [`FAILURE_TAXONOMY.md`](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/FAILURE_TAXONOMY.md), `EVALS.md` | None seen | Yes |
| [kirilxd/claude-tutor](https://github.com/kirilxd/claude-tutor) | 144 | MIT | 2026-07-20 | [`skills/learn/SKILL.md`](https://github.com/kirilxd/claude-tutor/blob/main/skills/learn/SKILL.md), `skills/quiz/`, [`skills/review/SKILL.md`](https://github.com/kirilxd/claude-tutor/blob/main/skills/review/SKILL.md) | Host question tool | Mostly |
| [bevibing/tutor-skills](https://github.com/bevibing/tutor-skills) | 1,377 | MIT | 2026-02-28 | [`skills/tutor/SKILL.md`](https://github.com/bevibing/tutor-skills/blob/main/skills/tutor/SKILL.md), `skills/tutor-setup/SKILL.md` | Host question tool; Obsidian-style vault | Mostly |
| [ktaletsk/learn-codebase](https://github.com/ktaletsk/learn-codebase) | 98 | MIT | 2026-10-18 | [`SKILL.md`](https://github.com/ktaletsk/learn-codebase/blob/main/SKILL.md), `QUESTION-PATTERNS.md`, `JOURNAL-TEMPLATE.md` | Host question tool | Yes for code; no search needed |
| [Bhala-Srinivash/agent-tutor-skill](https://github.com/Bhala-Srinivash/agent-tutor-skill) | 14 | MIT | 2026-03-01 | [`SKILL.md`](https://github.com/Bhala-Srinivash/agent-tutor-skill/blob/main/SKILL.md), [`references/fsrs.md`](https://github.com/Bhala-Srinivash/agent-tutor-skill/blob/main/references/fsrs.md) | None | Yes |
| [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom) | 295 | MIT | 2026-10-20 | [`skills/bloom-tutor/SKILL.md`](https://github.com/Li-Evan/Bloom/blob/main/skills/bloom-tutor/SKILL.md), [`skills/learn-feynman/SKILL.md`](https://github.com/Li-Evan/Bloom/blob/main/skills/learn-feynman/SKILL.md) | Optional web app | Yes for the skills |
| [tronghieu/agent-skills](https://github.com/tronghieu/agent-skills) | 95 | MIT | p: 2026-10-31 | [`skills/socratic-questor/SKILL.md`](https://github.com/tronghieu/agent-skills/blob/main/skills/socratic-questor/SKILL.md) | None | Yes |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (flashcards) | 259,523 | MIT | 2026-11-01 | [`optional-skills/productivity/memento-flashcards/SKILL.md`](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/productivity/memento-flashcards/SKILL.md) | Python scripts | Yes, with a shell |
| [doasfrancisco/anki-skill](https://github.com/doasfrancisco/anki-skill) | 57 | None | 2026-02-16 | [`SKILL.md`](https://github.com/doasfrancisco/anki-skill/blob/master/SKILL.md) | Bundled scripts use an Anki-Connect module | Search not needed |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 45,725 | Apache-2.0 | p: 2026-11-01 | [`plugins/learning-output-style/`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/learning-output-style) | Claude Code hook | Search not needed |

**Notes, wiki and second-brain systems**

| Repo | Stars | Licence | Last commit | Key paths | External dependencies | Works with generic web search only? |
|---|---|---|---|---|---|---|
| [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) | 2,652 | MIT | 2026-07-23 | [`SKILL.md`](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md), [`scripts/check_evidence.py`](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/scripts/check_evidence.py), `references/` | Python for the lint script | Yes |
| [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) | 188 | MIT | 2026-07-03 | [`skills/wiki-lint/SKILL.md`](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-lint/SKILL.md), [`skills/wiki-audit/SKILL.md`](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-audit/SKILL.md), `skills/wiki-init/assets/bin/lint-mechanical.py` | Python, subagents | Yes |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (wiki) | 259,523 | MIT | 2026-11-01 | [`optional-skills/research/llm-wiki/SKILL.md`](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/research/llm-wiki/SKILL.md) | None seen | Yes |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | 16,057 | MIT | 2026-10-22 | `skills/wiki-ingest/`, `skills/wiki-lint/`, `agents/wiki-lint.md`, [`agents/verifier.md`](https://github.com/AgriciDaniel/claude-obsidian/blob/main/agents/verifier.md) | Claude Code and Obsidian oriented | Partly |
| [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) | 3,670 | MIT | 2026-10-26 | [`tools/lint.py`](https://github.com/SamurAIGPT/llm-wiki-agent/blob/main/tools/lint.py), [`tools/health.py`](https://github.com/SamurAIGPT/llm-wiki-agent/blob/main/tools/health.py), `.claude/commands/` | Python tools | Mostly |
| [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | 3,651 | MIT | 2026-10-27 | `.skills/llm-wiki/SKILL.md` (42.5 KB), `.skills/wiki-lint/SKILL.md` (37.4 KB) | Obsidian oriented | Yes, but very large |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | 50,579 | MIT | 2026-09-15 | [`skills/obsidian-markdown/SKILL.md`](https://github.com/kepano/obsidian-skills/blob/main/skills/obsidian-markdown/SKILL.md), [`skills/defuddle/SKILL.md`](https://github.com/kepano/obsidian-skills/blob/main/skills/defuddle/SKILL.md) | `defuddle` npm CLI for extraction | Yes; format skills need no search |
| [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | 21,270 | GPL-3.0 by LICENSE text; API reports NOASSERTION | p: 2026-10-21 | Desktop application | Application | No |
| [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) | 2,573 | None | p: 2026-07-27 | Not inspected | Not checked | Unknown |
| [lucasastorian/llmwiki](https://github.com/lucasastorian/llmwiki) | 1,740 | Apache-2.0 | p: 2026-10-31 | Not inspected | Hosted-style upload flow, per description | Unknown |
| [vanillaflava/llm-wiki-skills](https://github.com/vanillaflava/llm-wiki-skills) | 70 | MIT | 2026-07-11 | [`wiki-crystallize/SKILL.md`](https://github.com/vanillaflava/llm-wiki-skills/blob/master/wiki-crystallize/SKILL.md) | Config and schema files | Yes |
| [stjbrown/agent-knowledge](https://github.com/stjbrown/agent-knowledge) | 41 | MIT | 2026-08-01 | [`skills/kb-lint/SKILL.md`](https://github.com/stjbrown/agent-knowledge/blob/main/skills/kb-lint/SKILL.md) | Node 18+ for conformance script | Yes |
| [mikonos/zettelkasten-agent-skills](https://github.com/mikonos/zettelkasten-agent-skills) | 3 | MIT | p: 2026-01-25 | `skills/literature-note/`, `skills/connection-discovery/`, `skills/random-walk/` | None seen | Yes |
| [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | 20,059 | MIT | 2026-10-31 | [`SKILL.md`](https://github.com/teng-lin/notebooklm-py/blob/main/SKILL.md) | Described as an unofficial API for Google Gemini Notebook | No |
| [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) | 7,791 | MIT | p: 2026-09-10, archived | Not inspected | NotebookLM | No |

**What the strongest candidates do**
- Mattpocock's [teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) is user-invoked and stateful. It keeps `MISSION.md`, `RESOURCES.md`, `NOTES.md`, numbered `learning-records/` and HTML lessons in a workspace.
- It treats learning records as "loosely equivalent to architectural decision records" and uses them to find the zone of proximal development. It separates fluency strength from storage strength and says "Never trust your parametric knowledge."
- Blomqvist's [teach](https://github.com/amosblomqvist/learn/blob/main/skills/teach/SKILL.md) runs probe, plan, teach. An edge counts as found only when bracketed by a right answer below and a wrong answer above. It treats all-correct as "too easy" and binary-searches difficulty.
- It stops for approval on a plan with a small dependency map, then runs motivate, establish, connect and quiz-check on each node. Its quiz procedure writes the correct claim first and mutates it into distractors so correctness can't be spotted from form.
- [Learning Opportunities](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md) says to end the message right after a question, with no hints or clues. It limits sessions to two exercises, asks before starting, and tells the agent not to credit insight the user never expressed. Fading changes the question setup, not the answer.
- Its [auto plugin](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities-auto/README.md) nudges after git commits through a post-tool hook.
- [Retrieve-first gate](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md) asks for a 0-100 confidence rating, then free recall, then gives a gap map of accurate, missing and misconceived points. Its warm-start text says first exposure should be taught, not guessed at. It keeps the initial recall separate from prompted recall.
- [Progressive hint ladder](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/progressive-hint-ladder/SKILL.md) defines six help levels, from diagnostic question to near-complete scaffold, and starts with "What have you tried so far?"
- The [universal tutor](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/skills/universal-diagnostic-tutor/SKILL.md) says "One correct answer is not mastery" and uses named status terms and a readiness gate. Its [failure taxonomy](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/FAILURE_TAXONOMY.md) lists failures including answer-first regression, fake mastery, no stop point and repeated same explanation, each with a likely fix location.
- ProjectSchola's [source mode](https://github.com/OJ102/ProjectSchola/blob/main/skills/teach/SKILL.md) teaches books from briefs, not raw text. Each brief claim has a code-checked citation, a Stop hook strips forged citations, and additions from outside the book are marked "(not in the book)". Reviews use fixed intervals of 1, 3, 7, 14, 30 and 60 days.
- [Li-Evan/Bloom's Feynman skill](https://github.com/Li-Evan/Bloom/blob/main/skills/learn-feynman/SKILL.md) has the agent play a curious student, probe vague parts, then classify each gap as a missing prerequisite or incomplete thinking.
- [Anthropic's learning output style](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/learning-output-style/hooks-handlers/session-start.sh) injects its instructions through a session-start hook.

**Wiki designs**
- [Astro-Han's skill](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) states a Grounding Invariant: every number, date and direct quote in `wiki/` must exist verbatim in the linked `raw/` files. Values are located before writing.
- [`check_evidence.py`](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/scripts/check_evidence.py) is report-only. It checks fidelity, evidence errors and unreferenced raw files, and its docstring states which claims it deliberately doesn't cover.
- The [same skill](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) triages each source as New, Update, Disputed or No material. It marks old claims Outdated or Disputed instead of rewriting them, and compiles one source at a time because `index.md`, `log.md` and cascades are shared state.
- [wiki-lint](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-lint/SKILL.md) runs a no-LLM script first, then one subagent per tag cluster, so page bodies stay out of the main context. It flags stale claims mechanically: not updated in 90 days and still saying "current" or "latest".
- [wiki-audit](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-audit/SKILL.md) checks one page per run. Footnotes with line ranges and a verbatim quote are verified by string match with no subagent.
- [Hermes' llm-wiki](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/research/llm-wiki/SKILL.md) adds frontmatter such as `contested: true` and `contradictions: [slug]`, and requires orientation before work on an existing wiki.

### Inferences
- [I] Adapt `mattpocock/skills` teach for structure, not its HTML lessons. Keeping lessons as Markdown would fit `knowledge/` better and keep the Obsidian option.
- [I] `amosblomqvist/learn` has the best procedure but no licence, and `ProjectSchola`'s README says the inherited parts stay with their author. Puck's rule that web text is summarised, never copied, covers this: take the ideas and write new text.
- [I] The wiki is close to solved. Use Astro-Han's skill as the base design and kfchou's lint as the upgrade, rather than combining many repos.
- [I] Obsidian compatibility needs only `obsidian-markdown`-level conventions. The `kepano` skills are small and could be vendored, but only that format knowledge is needed in milestone 3.

### Gaps
- None of these repos publishes delayed-retention outcome data that I found. Their evidence claims are citations of general learning science, not tests of the skill.
- `learning-opportunities` has a [measurement playbook](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/docs/MEASURE-THIS.md) aimed at teams. I found no published results from it, but I did not read all of it.
- Repos not read: `ZeKaiNie/universal-examprep-skill` (364 stars), `alchaincyf/feynman-skill` (309 stars) and `inkeep/open-knowledge` (4,757 stars).
- Zettelkasten-specific skills are small and low-signal. The largest I found had 3 stars, though GitHub search matched poorly on this term.
- I could not get star-like statistics for Karpathy's gist. `gh api gists/442a6bf555914893e9891c11519de94f` returned HTTP 502 twice.
- GitHub search ANDs terms, and topic searches returned mostly irrelevant high-star repos. Coverage relies on name searches and curated lists, so small repos may be missing.

## Which subagent-based research patterns work best: fan-out with citation verification, adversarial fact checking, source grading?

### Takeaway
No repo shows a measured advantage for its pattern. Mechanical provenance checks are the cheapest, most defensible addition: IDs from retrieval, quotes matched against fetched text, and a gate that fails. Adversarial debate has only self-reported lab evidence, and weighted source scoring looks weakest, so Puck should keep its claim-checker and add opposing-side searches, not debaters.

### Cited Findings

**Fan-out**
- [`tavily-research`](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/SKILL.md) starts one subagent per subtopic, passes along the user's limits, and runs a second round only for thin parts.
- [Claude-Obsidian autoresearch](https://github.com/AgriciDaniel/claude-obsidian/blob/main/skills/autoresearch/SKILL.md) says to search gaps and contradictions, "not merely more examples of the leading" view, and reports budget use after each round.
- [Astro-Han](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) tells the agent to search the opposing side of any core claim it expects to conclude: failures, criticism and failed replications.

**Citation verification**
- [`grounded-citations`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/SKILL.md) has a script own the URL-to-number mapping, so the model emits only integers it was given.
- Its fact-checking mode rejects a quote unless it appears verbatim in fetched text, marks unsourced claims `[unverified]`, and fails on sources without evidence through `verify --evidence`.
- Its [rationale file](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/references/grounding-rationale.md) says ALCE found citing during composition better than post-hoc citation. The [ALCE abstract](https://arxiv.org/abs/2305.14627) doesn't address that comparison, but it does report that even the best models on ELI5 lacked complete citation support 50% of the time.
- [`verify_claim_support.py`](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/scripts/verify_claim_support.py) uses deterministic entity, number, date and lexical-overlap checks with no LLM calls. Only factual claims hard-fail.
- [wiki-audit](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-audit/SKILL.md) dispatches one subagent per source, with bounded line slices for synthesis claims. Its strong mode adds a cross-model pass.
- ProjectSchola's [librarian](https://github.com/OJ102/ProjectSchola/blob/main/hooks/source/librarian-prompt.md) requires citations with anchors of 6 to 25 verbatim words copied from one line of source text.

**Adversarial checks**
- [tonyazhuuki's pipeline](https://github.com/tonyazhuuki/deep-research-skill/blob/main/research/SKILL.md) uses CRITIC, METHODOLOGIST, FACT-CHECKER and CITATION_VERIFIER roles across 10-19 agents. It spawns tiebreaker Deep Divers on contested claims, with a maximum of two rounds and a 15% budget cap.
- In update mode, that pipeline's scouts don't see the earlier consensus. A diff then labels claims CONFIRMED, REVISED, CONTRADICTED, OBSOLETE or NEW.
- Its stated method cites `arxiv.org/abs/2602.00000` for an Eric Jang piece. That ID looks like a placeholder and was not checked, so treat the attribution with caution.
- [PROClaim](https://arxiv.org/abs/2603.28488) (Mar 2026 preprint) uses courtroom-style agents and reports 81.7% accuracy on Check-COVID, 10.0 points above standard multi-agent debate, with progressive RAG contributing most of the gain. This comes from a search summary and is author-reported.
- [DebateCV](https://arxiv.org/abs/2507.19090) uses two debaters and a moderator. It reports that zero-shot moderators are weaker than debaters, which motivated fine-tuning. This comes from a search summary and is author-reported.

**Source grading**
- [`source_evaluator.py`](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/scripts/source_evaluator.py) computes a 0-100 score: domain 35%, recency 20%, expertise 25% and bias 20%.
- [tonyazhuuki's evidence reference](https://github.com/tonyazhuuki/deep-research-skill/blob/main/codex/deep-research/references/evidence.md) gives each source an `independence_group`. It says confidence "is not the fraction of sources that agree" and must consider design quality, directness, consistency, precision, bias, recency and applicability.
- [Exa's reference](https://github.com/exa-labs/exa-mcp-server/blob/main/plugins/exa/skills/search/references/source-quality.md) uses qualitative tags and runs credibility searches only when the task calls for them.
- [Tavily's researcher](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/references/researcher.md) prefers "the institution in a position to know".

### Inferences
- [I] Best pipeline for Puck's constraints: 3-5 researchers, each returning claim, URL and verbatim quote; a script verifying ledger IDs and quotes; then the fresh `claim-checker` on quoted evidence, not whole pages. This should cut the claim-checker's reading and matches Puck's "URL check script" step. It is untested.
- [I] The ledger's quote check needs a shell, but Puck's `researcher` has none. Researchers can return quotes, and a `puck` command run by the task agent can fetch and verify them. Putting this in the CLI matches the design's "Can a program compute it exactly?" rule.
- [I] Add `independence_group`, because counting agreeing pages rewards syndicated content. It also directly avoids GPT Researcher's "most frequent information" approach, which Puck's notes list as an unverified claim.
- [I] Skip debate agents for now. A "search the other side" instruction gets much of the value at no extra agent cost, and Puck's fan-out cap leaves no room for debaters. The debate papers are on narrow benchmarks.
- [I] Skip numeric source scores. Fixed weights imply precision that isn't there, and domain reputation can penalise a good primary source on a small site. Use qualitative tags.
- [I] Use Temporal Diff when a topic is re-researched, because hiding the old consensus from researchers reduces anchoring. It can be a late addition.

### Gaps
- I found no head-to-head test of these pipelines for any repo, including ledgers versus plain instructions.
- I read the PROClaim and DebateCV results only through search summaries, not the papers.
- I did not verify the WebGPT claim in Hermes' rationale file or test `sources.py`.
- I found no evidence that deterministic lexical checks catch the claim errors reported in arXiv 2605.06635. They may catch numbers and names while missing subtle mischaracterisation, which is why the fresh claim-checker should stay.

## For each candidate: what are the import verdicts, dependencies and pin points?

### Takeaway
Import ideas, not files. All recommended adoptions work on a generic-search host, and the ones with scripts belong in `puck` CLI commands. Licence blocks direct copying from several of the best sources, but Puck's summarise-only rule already avoids that.

### Cited Findings

**Shortlist**

Stars, licence, dates and paths are in the tables above. "Pin" is the short HEAD commit at retrieval, from `gh api repos/<repo>/commits`.

| Candidate | Pin | Verdict | Take | Leave |
|---|---|---|---|---|
| [`learning-opportunities`](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md) | `3862d2eb6e93` | Adapt, credit under CC-BY | Hard stop after a question, no unearned credit, fading rule, exercise types | Coding-only triggers, post-commit hook |
| [`mattpocock/skills` teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) | `4ae2317ddb22` | Adapt | Mission, numbered learning records, resources list, glossary, fluency versus storage | HTML lessons as the main output |
| [`amosblomqvist/learn` teach](https://github.com/amosblomqvist/learn/blob/main/skills/teach/SKILL.md) | Not pinned | Ideas only, [no licence file](https://github.com/amosblomqvist/learn) | Bracketed probe, plan checkpoint, per-node loop, distractor procedure | Pi tools, Obsidian-rendered LaTeX assumptions |
| [`retrieve-first-gate`](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md) | `135d6275e7db` | Ideas only, because of share-alike | Confidence, recall, gap map; first exposure exempt | School-oriented wording and frontmatter |
| [`grounded-citations`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/SKILL.md) | `557254faa24e` | Adapt into CLI | Ledger IDs, verbatim quote gate, `[unverified]` | Hermes paths |
| [`karpathy-llm-wiki`](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) | `eafcc77001e4` | Adapt as `kb` base | Grounding Invariant, triage, Status blocks, `check_evidence.py` logic, serial compile | Project-root layout |
| [`wiki-skills`](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-lint/SKILL.md) | `d9267ec9ccef` | Adapt later | Script-first lint, clustered subagents, line-range quote audit | Writing lint reports as wiki pages by default |
| [`tavily-research`](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/SKILL.md) | `00a131a8033e` | Adapt | Subtopic count rule, stop limits, authoritative-source rule | `tvly` dependency |
| [Failure taxonomy](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/FAILURE_TAXONOMY.md) | `075c1895d255` | Adapt as eval seeds | Answer-first, fake mastery, no stop point, repeated explanation | The full 2.0 tutor |

**Not recommended for milestone 3**

| Candidate | Why |
|---|---|
| [gpt-researcher](https://github.com/assafelovic/gpt-researcher) | Application with keys; Puck is a layer, not a new research app |
| [open_deep_research](https://github.com/langchain-ai/open_deep_research) | Archived |
| [Imbad0202 deep-research](https://github.com/Imbad0202/academic-research-skills/blob/main/deep-research/SKILL.md) | 13 agents, 52.5 KB, non-commercial licence |
| [tonyazhuuki pipeline](https://github.com/tonyazhuuki/deep-research-skill/blob/main/research/SKILL.md) | 10-19 agents; keep the claim-ledger idea only |
| [last30days](https://github.com/mvanhorn/last30days-skill) | Shell-heavy, large, optional browser tokens |
| [kirilxd/claude-tutor](https://github.com/kirilxd/claude-tutor/blob/main/skills/quiz/SKILL.md) | SM-2, `learningStyle` profile, short answers reduced to picking the closest option |
| [agent-tutor-skill](https://github.com/Bhala-Srinivash/agent-tutor-skill/blob/main/references/fsrs.md) | Agent applies FSRS by hand in Markdown; Puck plans py-fsrs |
| [memento-flashcards](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/productivity/memento-flashcards/SKILL.md) | Agent grades free text; fixed +1, +3 and +7 day intervals |
| [notebooklm-py](https://github.com/teng-lin/notebooklm-py) | Unofficial API, and the host product's name and interface are moving |

**Star count context**
- Forks were checked for ten shortlist repos, for example [amosblomqvist/learn](https://github.com/amosblomqvist/learn) with 3,998 stars and 419 forks and [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) with 54,898 stars and 4,185 forks. Topic searches also surfaced repos with very high counts, such as [morluto/rea](https://github.com/morluto/rea) at about 418,947.

### Inferences
- [I] Licence risk is modest today because the repo is private and Puck only summarises. It matters if Puck is published later, so credit CC-BY sources and record provenance in skill metadata. Treat CC BY-SA sources as ideas only.
- [I] Third-party scripts should be reimplemented, not vendored. `check_evidence.py` and `sources.py` are small enough for `src/core`, and that keeps one test suite and the design's locking rule.
- [I] Stars don't discriminate well here. Four of the nine shortlisted repos have under 1,000 stars, while high-star entries such as ECC and last30days did not make the shortlist.

### Gaps
- `amosblomqvist/learn` was not pinned because a SHA wasn't fetched in the final call; its last commit is 2026-08-25.
- [`discernment-nudge`](https://github.com/anthropics/skills/blob/main/skills/discernment-nudge/SKILL.md) says terms are in LICENSE.txt, and I did not read that file. `anthropics/skills` has no repo-level licence in the API.
- I did not read any shortlisted repo's full issue history, so known defects are unknown.
- Fork counts are weak authenticity signals, and I did not test for star manipulation.

## Which candidates fit Puck's milestone 3 design, which conflict, and what ideas does Puck lack?

### Takeaway
Puck's architecture holds up. The real gaps are inside `learn`: it diagnoses the goal but not the learner's level, it has no place for learner records, and it has no retrieval until FSRS arrives in milestone 4. Add a bracketed probe, a free-recall opening and learner records. For `kb`, add a mechanical evidence check. One design tension needs a decision: research text landing in the wiki automatically.

### Cited Findings

**Learning-science evidence that decides between candidates**
- Quiz format: [Kang et al. 2007](https://www.gwern.net/docs/spaced-repetition/2007-kang.pdf) compared initial short-answer and multiple-choice tests on a final test three days later. A follow-up, [McDaniel, Roediger and McDermott](https://profiles.wustl.edu/en/publications/generalizing-test-enhanced-learning-from-the-laboratory-to-the-cl/), reported that short-answer gave greater gains and that production tests and feedback increase learning. Results are not uniform: a Cambridge handbook chapter is titled [multiple-choice and short-answer quizzing "on equal footing in the classroom"](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-cognition-and-education/multiplechoice-and-shortanswer-quizzing-on-equal-footing-in-the-classroom/21FC37C4A8E0EAEDAFF233EA684D8FE2). I read these through search summaries.
- This separates [bevibing's four multiple-choice questions](https://github.com/bevibing/tutor-skills/blob/main/skills/tutor/SKILL.md) and [kirilxd's "Pick the closest answer"](https://github.com/kirilxd/claude-tutor/blob/main/skills/quiz/SKILL.md) from free recall in [retrieve-first-gate](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md).
- Learning styles: [Pashler et al.](https://digitalcommons.usf.edu/psy_facpub/1765/) found no adequate evidence base for building learning-styles assessments into general practice, though they did not show that every form is false. This counts against the `learningStyle` field in [claude-tutor](https://github.com/kirilxd/claude-tutor/blob/main/skills/learn/SKILL.md) and in [agent-tutor-skill's profile](https://github.com/Bhala-Srinivash/agent-tutor-skill/blob/main/SKILL.md).
- Confidence ratings: under the [hypercorrection effect](https://dukespace.lib.duke.edu/items/d6ab09ca-f55c-4efb-9d32-2788bc5838b2), high-confidence errors are more likely to be corrected after feedback. That supports asking for confidence before feedback, as [retrieve-first-gate](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md) does. I read this through a search summary, which reported replications but found no meta-analysis.
- Bloom's 2-sigma: [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom) presents it as its premise, while [Puck's research notes](/Users/doug/coding/puck/docs/research/learning-and-planning.md) list it as hype based on von Hippel's review.

**Fits**
- `kb`: [Astro-Han](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) has the `raw/`, `wiki/`, `index.md`, `log.md`, ingest, query and lint structure that [Puck's design](/Users/doug/coding/puck/docs/design.md) specifies.
- `kb` concurrency: Astro-Han's serial compile matches Puck's locked appends. Puck regenerates `index.md`, as does [wiki-lint](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-lint/SKILL.md) through `generate-index.py`.
- `learn`: the attempt-first and adjustable-friction design matches [progressive hints](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/progressive-hint-ladder/SKILL.md) and [Blomqvist's adaptive Socratic or expository choice](https://github.com/amosblomqvist/learn/blob/main/skills/teach/SKILL.md).
- `research`: Puck's clarify, plan, fan-out, URL check and claim-check sequence is already stronger than the verification in [Tavily](https://github.com/tavily-ai/skills/blob/main/skills/tasks/tavily-research/SKILL.md), [deer-flow](https://github.com/bytedance/deer-flow/blob/main/skills/public/deep-research/SKILL.md) and [ECC](https://github.com/affaan-m/ECC/blob/main/.agents/skills/deep-research/SKILL.md).

**Conflicts**

| Candidate behaviour | Puck rule it breaks |
|---|---|
| [`AskUserQuestion` mandated](https://github.com/bevibing/tutor-skills/blob/main/skills/tutor/SKILL.md), [`${CLAUDE_PLUGIN_ROOT}` in skill text](https://github.com/OJ102/ProjectSchola/blob/main/skills/teach/SKILL.md) | Skill text names capabilities, not host tool names |
| [State in `~/.claude/learning/`](https://github.com/kirilxd/claude-tutor/blob/main/skills/learn/SKILL.md) | `context/` is the source of truth, and personal data lives in one repo |
| [SM-2](https://github.com/kirilxd/claude-tutor/blob/main/skills/review/SKILL.md), [fixed intervals](https://github.com/OJ102/ProjectSchola/blob/main/skills/teach/SKILL.md), [agent-computed FSRS](https://github.com/Bhala-Srinivash/agent-tutor-skill/blob/main/references/fsrs.md) | py-fsrs scheduling |
| [Agent-graded reviews](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/productivity/memento-flashcards/SKILL.md) | Self-graded terminal review, mastery from FSRS retrievability |
| [Post-commit hook nudges](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities-auto/README.md) | Hook events are limited to `session-start` and `stop` |
| [10-19 agents](https://github.com/tonyazhuuki/deep-research-skill/blob/main/research/SKILL.md) | At most 5 workers, no nested fan-out |
| [Required paid keys or MCP servers](https://github.com/firecrawl/skills/blob/main/skills/workflows/firecrawl-deep-research/SKILL.md) | Native host search first; adapters in phase 2 |
| [Ask nothing unless critical](https://github.com/199-biotechnologies/claude-deep-research-skill/blob/main/SKILL.md) | Research starts with clarify |
| [Skills of 31-52 KB](https://github.com/Imbad0202/academic-research-skills/blob/main/deep-research/SKILL.md) | 150-line target, 500-line hard limit |

**Ideas Puck lacks**

| Idea | Source | Where it goes |
|---|---|---|
| Bracketed level probe: floor and ceiling per strand, with difficulty binary search | [Blomqvist](https://github.com/amosblomqvist/learn/blob/main/skills/teach/SKILL.md) | `learn`, before the attempt step. Puck's design says only "diagnose goal" |
| Free-recall opening with confidence rating and gap map; first exposure exempt | [Retrieve-first gate](https://github.com/GarethManning/education-agent-skills/blob/main/skills/student-learning/retrieve-first-gate/SKILL.md), [retrieval check-in](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md) | `learn`, start of each returning session. Gives retrieval before milestone 4 |
| Learner records in the style of ADRs, plus a mission file | [Mattpocock](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) | New per-topic data, separate from the wiki |
| Named status terms that can't be read as mastery | [Universal tutor](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/skills/universal-diagnostic-tutor/SKILL.md) | Concept update in `learn` |
| Stop rule after any question; no unearned credit | [Learning Opportunities](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md) | `learn` rules |
| Grounding invariant with a mechanical check | [Astro-Han](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/scripts/check_evidence.py) | `puck kb lint` |
| Ingest triage and Outdated or Disputed status blocks | [Astro-Han](https://github.com/Astro-Han/karpathy-llm-wiki/blob/main/SKILL.md) | `kb` ingest |
| Stale-claim detection and script-first lint | [wiki-lint](https://github.com/kfchou/wiki-skills/blob/main/skills/wiki-lint/SKILL.md) | `puck kb lint`; subagent pass later |
| Citation ledger and quote gate | [`grounded-citations`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/SKILL.md) | `research`, as a CLI command |
| Mark tutoring content not grounded in the wiki | [Schola's "(not in the book)"](https://github.com/OJ102/ProjectSchola/blob/main/skills/teach/SKILL.md), [Hermes' `[unverified]`](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/grounded-citations/SKILL.md) | `learn` rules |
| Failure taxonomy as eval seeds | [Universal tutor](https://github.com/SenmuuuuW/universal-diagnostic-tutor-skill/blob/main/FAILURE_TAXONOMY.md) | `learn/evals/` |
| Offer a short exercise after build work | [Learning Opportunities](https://github.com/DrCatHicks/learning-opportunities/blob/main/learning-opportunities/skills/learning-opportunities/SKILL.md) | Retro or task close, not a hook |

**Tension to decide**
- [Puck's design](/Users/doug/coding/puck/docs/design.md) lands topic facts in `knowledge/` automatically, while [Claude-Obsidian](https://github.com/AgriciDaniel/claude-obsidian/blob/main/skills/autoresearch/SKILL.md) keeps research as a dossier until a separately reviewed merge.
- Puck's design also says web-derived text can't enter cross-host memory unreviewed, and `learn` is grounded in the wiki. So unreviewed web text can shape tutoring, even though it is never loaded as rules.

### Inferences
- [I] Smallest useful `learn` loop: mission, probe, plan checkpoint, then repeat attempt, feedback and concept update. Returning sessions open with free recall. Do this in Markdown files and without a scheduler.
- [I] Use multiple choice for fast probing, where the goal is locating an edge, and free recall for retrieval practice. The evidence favours production for retention, though not uniformly.
- [I] Learner records need a home. `context/knowledge/<topic>/learner/` would keep them near the wiki but separate from agent-owned facts. This is a small design change, and the exact path is yours to decide.
- [I] Leave `learningStyle` out of `profile.md`. Preferences about pace or friction are still useful, since they don't claim that matched instruction improves learning.
- [I] Resolve the wiki tension by keeping auto-landing but requiring each page to pass the mechanical evidence check, and by labelling pages from unverified research. Prompts alone won't enforce this, so it belongs in `puck` commands.
- [I] Suggested order within milestone 3:
  1. `kb` with Grounding Invariant and `puck kb lint`.
  2. `research` with the Tavily-style split, opposing-side search and the ledger.
  3. `learn` with probe, recall opening and learner records.
  4. Evals from the failure taxonomy.

### Gaps
- All ideas above are design judgement. None has been tested in Puck, and none has delayed-outcome evidence as a skill.
- Whether a free-recall gate survives real adult use is unknown. Puck's notes show pure refusal drove students away, so the gate needs an easy skip.
- Learning-format findings come from search summaries, not full papers, and I did not retrieve exact effect sizes for Kang et al.
- I did not check how `check_evidence.py` behaves on non-English sources or at Puck's planned scale.
- The design's phrase "diagnose goal" may already intend a level check. If so, the probe is a refinement, not a gap.
