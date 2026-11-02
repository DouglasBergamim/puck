# Agent harness research notes: search, learning, coding and planning (as of 2026-11-01)

Plan mode was active, so I wrote no files and these notes are the full output.

**Evidence labels**
- **[V]**: I fetched the primary source.
- **[S]**: search snippet or secondary write-up only.
- **[C]**: community claim or anecdote.
- **[I]**: my inference.
- **Stale risk**: the source predates about May 2026.

**Limits on these notes**
- PNAS, SSRN, OpenAI.com, Sage and Springer blocked fetches, so a few claims stay at [S].
- Anthropic docs and research are vendor sources. Since Claude wrote these notes, weigh them accordingly.
- GitHub star counts are popularity, not evidence of value.

**Three premises to correct**
- Karpathy's autoresearch runs ML experiments. It is not web research.
- `claude plugin eval` is real and documented.
- Boris Cherny's "2-3x quality" figure has no measurement behind it that I could find.

---

## Part A1. Which search APIs should an agent use?

### Takeaway
No provider wins across benchmarks, and rankings flip with the metric and configuration. Exa, Perplexity Search and Parallel are the most consistently strong. Tavily looks weaker, and Brave's rank depends heavily on which of its products is tested. Run a small test on your own queries before committing.

### Cited Findings

**Benchmarks**

| Benchmark | Design | Result | Independence |
|---|---|---|---|
| [Artificial Analysis Search Index](https://artificialanalysis.ai/agents/search-api), data 19 Oct 2026 [V] | Fixed agent harness; average of DeepSearchQA, BrowseComp, AA-Omniscience; [same model also grades](https://artificialanalysis.ai/methodology/search-api) [S] | Exa auto 80, Perplexity medium 80, Octen 77, Parallel advanced 75, Brave LLM context 75, OpenAI 74, Firecrawl 73, no-search baseline 33 | Third party. Page shows 12 of 26 providers. Tavily is not in those 12 |
| [Openbenchmarks](https://openbenchmarks.com/web-search/best-search-tools-for-ai-agents), measured 15 Sep 2026 [V] | 100 developer questions; pass needs a working patch plus a citation | Perplexity 77.3%, Firecrawl 70.3%, Parallel fast 66.7%, Exa fast 66.3%, Tavily 51.0%, Brave 38.0% | Operator undescribed; no funding disclosure |
| [AIMultiple](https://aimultiple.com/agentic-search), Dec 2025 snapshot, updated May 2026 [V] | 100 AI/LLM queries; LLM judge; about 10% hand-checked | Brave 14.89, Firecrawl 14.58, Exa 14.39, Parallel Pro 14.21, Tavily 13.67, Perplexity 12.96, SerpAPI 12.28. Top four CIs overlap | Discloses SerpApi as a subscriber. Stale risk |
| [Parallel's own](https://parallel.ai/articles/the-honest-2026-comparison-web-search-apis-for-ai-agents) BrowseComp, Sep 2026 [V] | Harness chosen by the vendor | Parallel 74, Perplexity 74, Exa 70, Tavily 66 | Vendor; it says so itself |

**Pricing, free tier and MCP**

| Provider | Price | Free tier | MCP |
|---|---|---|---|
| [Exa](https://exa.ai/pricing) [V] | $4/1k lite, $7/1k auto, $12-15/1k deep, $1/1k pages contents | $10 credit resets monthly | [mcp.exa.ai](https://parallel.ai/articles/best-web-search-mcp) [S, competitor source] |
| [Tavily](https://www.tavily.com/pricing) [V] | $0.008/credit; $30 for 4k credits | 1,000 credits/month; free for students | mcp.tavily.com [S]. Now "Tavily by Nebius" |
| [Brave](https://brave.com/search/api/) [V] | $5/1k search; 50 QPS | $5 monthly credit; card required | Official brave-search-mcp-server |
| [Perplexity Search API](https://docs.perplexity.ai/getting-started/pricing) [V] | $5/1k, Fast $1/1k; up to 5 queries per request, no token charges | None listed on the page | [api.perplexity.ai/mcp](https://parallel.ai/articles/best-web-search-mcp) [S, single competitor source] |
| [Parallel](https://parallel.ai/articles/the-honest-2026-comparison-web-search-apis-for-ai-agents) [V, vendor] | $1/1k turbo and fast; $5/1k basic and advanced | $5 monthly credit | search.parallel.ai/mcp [S] |
| [Firecrawl](https://www.firecrawl.dev/pricing) [V] | $19/month for 5k credits; search 2 credits per 10 results | 1,000 credits/month | mcp.firecrawl.dev [S] |
| [Jina Reader](https://jina.ai/reader/) [V] | Token-based | 10M tokens per key; 20 RPM keyless, 500 RPM with free key | mcp.jina.ai. Footer and sales appear to be Elastic |
| [SearXNG](https://github.com/searxng/searxng) [V] | Self-host | Free; AGPL-3.0 | No official server confirmed |
| [Claude native](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) [V] | $10/1k plus tokens | n/a | Built in. Citations always on; dynamic filtering from version `web_search_20260209` |
| OpenAI native | [$10/1k plus tokens](https://parallel.ai/articles/the-honest-2026-comparison-web-search-apis-for-ai-agents) [S, competitor source] | n/a | Built in |

**Source conflicts**
- Parallel's article says Brave has no standing free allowance. [Brave's own page](https://brave.com/search/api/) lists $5 monthly credits, and its homepage says "up to $20".
- Parallel lists Exa's free tier as 1,000 requests per month. [Exa's page](https://exa.ai/pricing) shows a $10 monthly credit.
- A [March 2026 blog](https://michaellivs.com/blog/web-search-for-agents-2026/) says Parallel offers 16,000 free requests, which conflicts with the $5 monthly credit in Parallel's own later article.
- AIMultiple's Firecrawl pricing is out of date compared with Firecrawl's page.

**Practitioner view**
- [Livshits, Mar 2026](https://michaellivs.com/blog/web-search-for-agents-2026/) [C]: "pick one and swap later", and extraction matters as much as search.
- Parallel recommends testing 50-100 of your own queries against two or three APIs [V, vendor].

### Inferences
- [I] Brave's swing from 38.0% in Openbenchmarks to 75 in Artificial Analysis probably reflects the product tested (plain search versus LLM context) and the metric. Content depth given to the agent seems to matter more than ranking alone.
- [I] Default stack: keep native search in the coding agent, add one strong API (Exa or Perplexity Search on quality, Parallel on cost), and add a separate extraction step (Jina Reader or defuddle).
- [I] SearXNG makes sense for privacy or zero cost. It is not a quality choice on current evidence.

### Gaps
- I found no independent benchmark of Claude's native search or SearXNG.
- Perplexity Sonar token pricing was not on the page I fetched.
- Keyless MCP endpoints come from Parallel's blog and were not confirmed in vendor docs.
- I did not confirm SearXNG's JSON API from the page fetched.

---

## Part A2. How do deep-research systems work, and which design decisions matter?

### Takeaway
Fan-out improves coverage, but it does not make citations accurate, and more retrieval can make them worse. The highest-value addition for a personal harness is a separate, claim-level verification pass, not more subagents.

### Cited Findings

**Implementations**
- [Anthropic, Jun 2025](https://www.anthropic.com/engineering/multi-agent-research-system) [V, vendor, stale risk]:
  - Orchestrator-worker design with 3-5 parallel subagents.
  - Plan saved to memory, and a separate CitationAgent as the final step.
  - Each subagent gets an objective, output format, tool guidance and task boundaries.
  - 90.2% better than single-agent on an internal eval.
  - About 15x the tokens of chat.
  - Token use explained about 80% of BrowseComp variance.
  - Started with about 20 real queries, scored by one LLM judge on a rubric.
  - Human testing caught agents favouring SEO content farms.
  - Poor fit for tasks with shared context, "such as most coding work".
- [OpenAI Deep Research API](https://developers.openai.com/api/docs/guides/deep-research) [V]:
  - The API runs only the research stage. ChatGPT adds clarify and prompt-rewrite steps beforehand.
  - Citations are annotations carrying character indexes.
  - `max_tool_calls` is the main cost control.
  - The docs list a 23 Jul 2026 shutdown for the `o3` and `o4-mini` deep-research models, with `gpt-5.6-sol` as the replacement.
  - The safety advice is to stage workflows so public web research and private data never run in the same call.
- [STORM](https://github.com/stanford-oval/storm) [V]: perspective-guided questions and simulated writer-expert conversations produce an outline, then an article. It states it "cannot produce publication-ready articles". Latest repo news is Jan 2025.
- [GPT Researcher](https://github.com/assafelovic/gpt-researcher) [V]: planner, execution agents and publisher. Its anti-hallucination claim (pick the most frequent information across sites) is the project's own and unverified.
- [LangChain open_deep_research](https://github.com/langchain-ai/open_deep_research) [V]: the repo is archived and read-only as of 21 Aug 2026. Best listed RACE score is 0.4943, and a full eval costs roughly $20-100.
- [Karpathy autoresearch](https://github.com/karpathy/autoresearch) [V]: an agent edits `train.py`, trains for 5 minutes, and keeps the change if val_bpb improves. About 12 experiments per hour, 99.0k stars. No web research.

**Accuracy evidence (all preprints)**
- [arXiv 2605.06635, May 2026](https://arxiv.org/abs/2605.06635) [V]:
  - 14 LLMs tested.
  - Frontier models reached only 39-77% citation factual accuracy, while link validity stayed above 94%.
  - Across two frontier models, accuracy fell about 42% as tool calls rose from 2 to 150.
- [arXiv 2604.03173, Apr 2026](https://arxiv.org/abs/2604.03173) [V]:
  - 3-13% of citation URLs were hallucinated across about 221k URLs.
  - Deep-research agents hallucinated at higher rates than search-augmented LLMs.
  - Their `urlhealth` liveness tool cut non-resolving URLs 6-79x, to under 1%.
- [arXiv 2601.22984](https://arxiv.org/abs/2601.22984) [V]: all six agents tested had reliability gaps. Failures traced mainly to hallucination propagation and cognitive biases.

### Inferences
- [I] The Anthropic result (more tokens, better BrowseComp) and the arXiv result (more tool calls, worse citation accuracy) fit together: depth buys recall, not claim precision. Measure them separately.
- [I] Skill design:
  1. Clarify the question.
  2. Plan, with explicit effort scaling.
  3. Fan out 3-5 scoped researchers.
  4. Check URLs with a script.
  5. Have a fresh agent check each claim against the fetched text, marking it supported, partial or unsupported.
  6. Separate facts, inference and gaps.
  7. Cap tool calls.
- [I] Adopt autoresearch's pattern (fixed metric, keep or revert) for skill tuning. It is not a research tool.

### Gaps
- OpenAI's original launch post was blocked (403).
- I did not verify the reported DRACO figures (65% citation quality, 68% factual accuracy).
- I found no per-stage breakdown of hallucination from the abstract of 2601.22984.

---

## Part A3. Which academic and documentation sources should the harness use?

### Takeaway
Use alphaXiv for arXiv-heavy work, OpenAlex and Semantic Scholar for citation graphs, and Context7 for library docs. Keep these thin and treat community multi-source MCP servers as unvetted.

### Cited Findings
- [alphaXiv MCP](https://www.alphaxiv.org/docs/mcp) [V]: 21 tools, including `discover_papers`, `get_paper_content`, `answer_pdf_queries` and GitHub reading. Uses OAuth 2.1 or an API key. Search draws on an assistant quota of unspecified size.
- [OpenAlex](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication) [S, official docs snippet]: usage-based since 2026. $0.01/day budget without a key, $1/day with a free key, and 100 requests per second maximum.
- [Semantic Scholar](https://semanticscholar.org/product/api) [S]: a key gives 1 request per second. Official pages disagree on the unauthenticated limit (1000 RPS shared, 5,000 per 5 minutes, or 100 per 5 minutes per IP).
- [Community MCP servers](https://glama.ai/mcp/servers/Liyux3/scholar-mcp) exist for combined arXiv, Semantic Scholar and OpenAlex search [S]. Maintenance status is unverified.
- [Context7](https://github.com/upstash/context7) [V]: 64.0k stars, offered as CLI plus skill or as MCP. The backend is private, and community docs are not guaranteed accurate.

### Inferences
- [I] A small CLI skill that calls OpenAlex or Semantic Scholar directly is simpler and safer than adopting a third-party aggregator.
- [I] Prefer Context7's CLI-plus-skill route, since it avoids always-loaded MCP tool schemas. Verify that for your own setup.

### Gaps
- I found no independent accuracy study of Context7.
- I did not fetch arXiv API docs.

---

## Part B1. What does the evidence say about AI tutors?

### Takeaway
Results depend on design and engagement. Structured, fact-grounded tutoring can work well in the short term. Unstructured answer access can raise practice scores while lowering later learning. The 2026 Khanmigo trial shows the limit of Socratic refusal: students disengaged.

### Cited Findings

| Study | Design and N | Result | Status |
|---|---|---|---|
| [Kestin et al., Sci Reports 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/) [V] | Crossover RCT, 194 analysed, Harvard physics, 2 lessons | Effect 0.63 by regression, 0.73-1.3 SD by quantile regression; median 49 min versus about 60 | Peer-reviewed. Low stakes; authors do not expect this for synthesis tasks |
| [Bastani et al., PNAS 2025](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html) [S] | Field experiment, about 1,000 high-school maths students | Practice +48% (base) and +127% (tutor). Exam -17% for base; tutor about equal to control | Peer-reviewed. PNAS and SSRN blocked |
| [Oreopoulos & Low, Aug 2026](https://edworkingpapers.com/sites/default/files/ai26-1551.pdf) [V] | 2-year cluster RCT, 18 Tennessee schools | 0.06-0.08 SD per year, in line with Khan practice without AI. 96% tried it; median student messaged on a third of practice days, and in 17% of sessions with a mistake; 14.5% of messages had a maths question or reasoning step | Working paper, pre-registered |
| [Shen & Tamkin, Anthropic, Jan 2026](https://www.anthropic.com/research/AI-assistance-coding-skills) [V] | RCT, 52 mostly junior engineers learning Trio | Quiz about 50% versus 67%, p=0.01. About 2 minutes faster, not significant | [Preprint](https://arxiv.org/abs/2601.20245); vendor-authored |
| [Pattern analysis, same study](https://www.anthropic.com/research/AI-assistance-coding-skills) [V] | Qualitative, 24 AI-group participants | Conceptual inquiry and generation-then-comprehension scored 65-86%; delegation and iterative AI debugging 24-39% | Cell sizes 2-7; not causal |
| [Kosmyna, "Your Brain on ChatGPT"](https://arxiv.org/abs/2601.00856) | [54 participants, 18 per group](https://arxiv.org/pdf/2601.00856) [S] | Reduced engagement with LLM | No peer-reviewed publication found. [Comment paper](https://arxiv.org/abs/2601.00856) [V] challenges sample size, reproducibility and EEG methods |
| [LearnLM/Eedi, Dec 2025](https://arxiv.org/abs/2512.23633) [V] | Exploratory RCT, 165 UK students | 66.2% versus 60.7% on novel problems; 76.4% of drafts approved with minimal edits | Preprint, Google co-authored. A human checked every message |
| [Tutor CoPilot](https://nssa.stanford.edu/studies/tutor-copilot-human-ai-approach-scaling-real-time-expertise) [S] | RCT, 700+ tutors, 1,000+ students | +4 percentage points mastery; +9 for lower-rated tutors | AI assists humans, not autonomous |
| [Programming meta-analysis, May 2026](https://arxiv.org/abs/2605.04779) [V] | 23 studies, 27 effect sizes | Productivity g=0.33 (CI 0.09 to 0.58). Learning g=0.14 (CI -0.18 to 0.47), not significant | Preprint |
| [STEM meta-analysis, 2026](https://link.springer.com/article/10.1007/s10462-026-11665-9) [S] | 49 studies, 59 effects | g=0.839, disappears after publication-bias correction | Fetch blocked |

**Bloom 2-sigma**
- [von Hippel, 2024](https://www.educationnext.org/two-sigma-tutoring-separating-science-fiction-from-science-fact/) [V, stale risk but stable]: the 2 SD figure rests on two dissertations with bundled treatments. Only 1 of 65 studies in Cohen, Kulik & Kulik reached it.
- Nickow et al. found 0.37 SD across 96 studies.
- A realistic target is about 0.33 SD on broad tests.

**What made tutors work**
- Kestin's platform sequenced steps itself because the prompt alone did not reliably keep scaffolding in order. It also used pre-written solutions for accuracy [V].
- Bastani's GPT Tutor was given each problem's solution and common mistakes [S].

**Newest signal**
- A follow-up in the same district gated progress on correct answers and showed the chatbot unprompted. Students moved more slowly, were more accurate, and were slightly better a week later ([Chalkbeat, Aug 2026](https://www.chalkbeat.org/2026/08/25/ai-tutoring-students-khanmigo-khan-academy-engagement-study/)) [V, preliminary, secondary report].
- On refusal, [Hechinger, Sep 2026](https://hechingerreport.org/proof-points-khanmigo-math-ai-tutor/) [V] reports that when Khanmigo withheld answers, most students stopped using it.

### Inferences
Design rules, each derived from the evidence above:
1. [I] Require an attempt first, then give help. This follows the generation-then-comprehension pattern and the gating result.
2. [I] Do not rely on prompts alone for tutoring structure. Enforce order in harness state with a hook or checkpoint file.
3. [I] Ground tutoring in sources or an answer key, since accuracy was an engineered property in Kestin and Bastani.
4. [I] Never trust practice performance as a mastery signal. Test later, without AI.
5. [I] Keep Socratic friction adjustable. Pure refusal risks disengagement, though a motivated adult may tolerate it better than remedial middle-schoolers.
6. [I] Default to explanation-seeking when coding to learn, and to delegation only when learning is not the goal. Make that an explicit mode switch.

### Gaps
- Almost all RCTs involve students, not self-directed adults. Transfer to this user is unknown.
- I found no synthesis isolating delayed retention.
- I found no RCT of ChatGPT Study Mode, Gemini Guided Learning or NotebookLM.

---

## Part B2. How are existing learning products built?

### Takeaway
Most "learning modes" are prompts or styles, not separate models. The harder differentiators are progress tracking and diagnostics, which are product state.

### Cited Findings
- **ChatGPT Study Mode**: [custom system instructions](https://simonwillison.net/2025/Jul/29/openai-introducing-study-mode/) [V, Jul 2025, stale risk].
  - Willison's extracted prompt covers asking about goals, building on prior knowledge, guiding with hints, and checking understanding.
  - It includes the line "DO NOT DO THE USER'S WORK FOR THEM".
  - OpenAI's own text was not fetched.
  - [Inconsistent behaviour was reported](https://www.maginative.com/article/openai-launches-study-mode-for-chatgpt/) [S].
- **Claude Code Learning style**: [official docs](https://code.claude.com/docs/en/output-styles) [V].
  - Adds `Insight` blocks.
  - Leaves `TODO(human)` markers at real design decisions, then stops and waits.
  - The docs say output styles are instructions, and nothing enforces them.
  - Custom styles are Markdown in `~/.claude/output-styles`.
- **Claude.ai Learning mode**: a [Socratic style](https://engadget.com/ai/anthropic-brings-claudes-learning-mode-to-regular-users-and-devs-170018471.html) launched for education in Apr 2025, then opened to all users [S].
- **Gemini study notebooks**: launched 25 Jun 2026 with a [diagnostic quiz, 100+ objectives and a progress dashboard](https://blog.google/innovation-and-ai/products/gemini-app/gemini-study-notebooks/) [S]. I found no outcome data.
- **NotebookLM**: [flashcards and quizzes generated from your uploaded sources](https://edu.google.com/ai-notebooklm/) [S, vendor]. The rename to Gemini Notebook is [unclear across sources](https://pasqualepillitteri.it/en/news/6342/gemini-study-notebooks-learning).
- **Khanmigo**: see Part B1.
- **Open source Claude skills** [S, unvetted]:
  - [agent-tutor-skill](https://github.com/bhala-srinivash/agent-tutor-skill) (FSRS, concept mastery)
  - [ProjectSchola](https://github.com/OJ102/ProjectSchola) (citations, Obsidian)
  - [learn-codebase](https://github.com/ktaletsk/learn-codebase) (Socratic codebase learning)
  - [claude-tutor](https://github.com/kirilxd/claude-tutor) (SM-2)
  - [learn-claude-code](https://github.com/cufelix/learn-claude-code) (Leitner boxes, hook-graded quizzes)

### Inferences
- [I] The cheap copy is a custom output style for tone plus a skill for the session loop. The valuable build is the learner state: concepts, attempts and due reviews stored as files.
- [I] Use these repos as design references rather than installing them. See the security notes in the last section.

### Gaps
- I found no learning-outcome evidence for any of the open-source skills.

---

## Part B3. How should spaced repetition be implemented?

### Takeaway
Use FSRS, not hand-rolled intervals. Spaced practice and retrieval have decades of support, while LLM card generation still needs human review.

### Cited Findings

**Learning science**
- Retrieval: [Adesope et al. 2017](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Rethinking-the-Use-of-Tests-A/99900601154801842) [S]. Practice tests beat restudy and other comparison conditions. Secondary figures give about g=0.61 and 118 articles; a [study count conflict](https://studycardsai.com/blog/active-recall-statistics) exists between sources.
- Spacing: [Cepeda et al. 2006](https://pubmed.ncbi.nlm.nih.gov/16719566/) [V]. 317 experiments from 184 articles. The best review gap grows with the desired retention period.
- Generation: [Bertsch et al. 2007](https://pubmed.ncbi.nlm.nih.gov/17645161/) [S]. 445 effect sizes across 86 studies, overall effect about 0.40.
- Self-made cards: [Pan et al. 2022](https://sc-pan.github.io/pdf/PZIZQ_2022.pdf) [S]. Memory advantage d=0.45, human-made cards only.

**FSRS**
- [srs-benchmark](https://github.com/open-spaced-repetition/srs-benchmark) [V]: log loss FSRS-7 recency 0.3370, FSRS-6 0.3460, FSRS-5 0.3561. The README itself conflicts on 10k versus 20k users. Maintainers are the FSRS project, so this is not independent.
- [Expertium](https://expertium.github.io/Benchmark.html) [V]: FSRS-6 beats Anki SM-2 for 99.6% of users, with the caveat that no truly fair comparison exists.
- [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) [V]: `Scheduler`, `Card`, `Rating`, `review_card`, `get_card_retrievability`, plus an optimizer, default retention 0.9.
- [ts-fsrs](https://github.com/open-spaced-repetition/awesome-fsrs) [V]: covers v3 to v7. py-fsrs is listed at v6.

**Anki**
- Several [MCP servers](https://github.com/nailuoGG/anki-mcp-server) exist, plus [ankimcp](https://www.sourcepulse.org/projects/29232007) (reported beta v0.15.1) [S].
- [AnkiConnect requires Anki desktop running](https://github.com/definedan/anki-mcp) [S], so they are not headless.

**LLM card quality**
- [Memory Machines, 2026](https://memory-machines.com/report) [V], from Kirkby and Matuschak, tested about 1,500 labelled prompts.
- Unusable rates: GPT-5.2 36% (best), Opus 4.5 50%, Sonnet 4.5 52%.
- The main failure is construction, not going off-target.
- Models catch off-target prompts but struggle at the boundary between usable and unusable.
- Grounding a judge against human-labelled examples was the biggest improvement: false positives fell from 52% to 17%.

### Inferences
[I] Two viable architectures:
- **Anki as source of truth:** the agent proposes cards, you approve them, and you review in Anki with mobile sync. Least code, and reuses mature tooling. Start here.
- **Local FSRS plus file state:** review inside the agent, grading free-text answers and mapping them to Again, Hard, Good or Easy. This supports conceptual questions, but the grader is itself unvalidated.

[I] Card flow:
1. You pick what matters.
2. The agent drafts 2-3 candidates per idea.
3. You edit and accept them.
4. A concept ID tracks mastery from FSRS retrievability, not from chat performance.

Preserving your own selection and editing keeps some of the generation benefit, though this is unproven for LLM drafts.

### Gaps
- I found no 2025-26 study comparing LLM-drafted and self-created cards on long-term outcomes.
- [Bjork's desirable difficulties](https://pubmed.ncbi.nlm.nih.gov/17645161/) were not sourced directly, and neither was Dunlosky 2013 (403). Treat both as background until checked.
- I did not verify which AnkiConnect endpoints can expose review history or FSRS state.

---

## Part B4. Is markdown plus grep enough for a personal knowledge base?

### Takeaway
Yes, as a starting point. Vendor memory benchmarks are unreliable, and simple baselines match or beat them. Add local hybrid search when you see semantic misses. Add a graph only if you truly need facts tracked over time.

### Cited Findings
- [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (4 Apr 2026) [V]:
  - Layers: raw sources (immutable), LLM-owned wiki, and a schema file.
  - Operations: ingest, query, lint.
  - Files: `index.md` and `log.md`.
  - The index approach works "surprisingly well at moderate scale (~100 sources, ~hundreds of pages)".
  - It names qmd for larger scale.
  - A practitioner reports [breakdown around 200 files](https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base.md) [C].
- [Letta, Aug 2025](https://www.letta.com/blog/benchmarking-ai-agent-memory) [V, vendor, stale risk]: a filesystem agent scored 74.0% on LoCoMo, against Mem0's reported 68.5%.
- [Benchmark Theatre, May 2026](https://essays.bloo-mind.ai/posts/2026-05-20-mem-eval/) [V, third-party essay]:
  - 99 scoring errors in LoCoMo (6.4%).
  - A judge accepted 62.81% of intentionally wrong but adjacent answers.
  - Full-context baseline about 73%.
  - EverMemOS 92.32% claimed versus 38.38% reproduced.
- [Mem0](https://github.com/mem0ai/mem0) [V, vendor]: claims LoCoMo 92.5 and LongMemEval 94.4 from its managed platform, not the open-source version. Discount this given the above.
- [MemoryAgentBench](https://arxiv.org/abs/2507.05257) [V]: all tested systems fall short on the four competencies. A [secondary report](https://www.ajayk.sh/blog/agent-memory-systems-2026/) says BM25 averaged 60.5% against Mem0, Zep, MemGPT and Cognee at 25-44% on accurate retrieval [S]. I did not check this against the paper body.
- Coding: Boris Cherny [reportedly said](https://www.bestblogs.dev/article/409d9979) agentic grep worked better than a local vector database [S, primary podcast not accessed].
- Counterpoint: an [embedding-vs-grep experiment](https://github.com/henry-dowling/embedding-vs-grep-experiment) found embeddings 35% cheaper through fewer round trips, but it used TF-IDF as a proxy [C].

**Tools**

| Tool | What it is | Notes |
|---|---|---|
| [qmd](https://github.com/tobi/qmd) [V] | Local BM25, vector and rerank; MCP | About 2GB of local models. 30.8k stars, MIT |
| [basic-memory](https://github.com/basicmachines-co/basic-memory) [V] | Markdown plus SQLite; Obsidian compatible | AGPL-3.0, 4.4k stars |
| [claude-mem](https://github.com/thedotmack/claude-mem) [V] | Six hooks, SQLite, Chroma | 109k stars. Has optional cloud sync, and promotes a third-party token. Review first |
| [Graphiti](https://github.com/getzep/graphiti) [V] | Bitemporal graph | Needs a graph database. Reference MCP has no auth or injection protection |
| [Letta](https://github.com/letta-ai/letta) [V] | Stateful agents | Active work moved to letta-code |
| [Claude Code auto memory](https://code.claude.com/docs/en/memory) [V] | Built in | First 200 lines or 25KB loaded each session |
| [obsidian-skills](https://github.com/kepano/obsidian-skills) [V] | 6 skills, including defuddle and Bases | 50.6k stars, MIT |

### Inferences
- [I] Recommended layout: Obsidian-compatible Markdown vault, `raw/` left immutable, a wiki owned by the agent, `index.md`, `log.md`, and a weekly lint.
- [I] Upgrade path: grep, then SQLite FTS5 or BM25, then qmd when a labelled set of about 30 queries shows misses.
- [I] LLM-written wikis add a new risk: errors become persistent. Give every wiki claim a link to a raw source, and run citation checks in lint.
- [I] Keep agent operational memory separate from your learning wiki, so tool notes do not pollute knowledge notes.

### Gaps
- I found no controlled test of grep versus embeddings at several hundred personal notes.
- I found no evidence on wiki quality decay over months.

---

## Part C1. Do plan modes work?

### Takeaway
Plan mode is a useful control, but I found no controlled evidence of its value across tools. Its most supported form is explore, interview, write spec, then build in a fresh session.

### Cited Findings
- [Claude Code](https://code.claude.com/docs/en/permission-modes) [V]:
  - Claude can read, run exploratory commands and write a plan, but edits stay blocked until approval.
  - Plans live in `~/.claude/plans/`, with `plansDirectory` to change that.
  - Enforcement depends on context. In an interactive terminal with bypass available, the blocks are not enforced, though Claude is still instructed not to edit.
  - Approval can switch to auto mode or manual edits, or clear the planning context.
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices) [V]: ask Claude to interview you until it could write the spec, write `SPEC.md`, then start a fresh session.
- Other tools [S, comparison blogs]: [OpenCode](https://agentic-ai.readthedocs.io/en/latest/AgenticFrameworks/ai-coding-agents/) has a read-only Plan agent. Sources [conflict](https://toolsbase.dev/en/blog/ai-coding-cli-comparison-2026) on whether Codex has a dedicated plan mode, and on Gemini CLI's status after a reported migration to Antigravity CLI.

### Inferences
- [I] Treat plan mode as a checkpoint. Any "never write" guarantee needs a tool allowlist or a hook.
- [I] A plan skill should output decisions, non-goals and acceptance checks. Line-level steps go stale.

### Gaps
- No head-to-head evaluation of plan mode found.
- Ultraplan was not found in the portion of the docs I read.

---

## Part C2. Does spec-driven development pay off?

### Takeaway
No controlled experiment shows SDD frameworks beat lighter workflows. Executable checks have far better support than Markdown ceremony. Keep specs short and scale process to task size.

### Cited Findings
- [Böckeler, 15 Oct 2025](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) [V, stale risk]:
  - Three levels: spec-first, spec-anchored, spec-as-source.
  - All tools reviewed were spec-first in practice.
  - Kiro turned a small bug into 4 user stories and 16 acceptance criteria.
  - spec-kit was verbose to review, and agents ignored or over-followed instructions.
  - Regeneration was non-deterministic.
  - She warns of a "Verschlimmbesserung".
  - No 2026 Fowler-site update on SDD found. The tools have changed since.
- [arXiv 2606.04967](https://arxiv.org/abs/2606.04967) [V]: qualitative taxonomy of 6 frameworks. No framework covers all six dimensions. It explicitly notes spec-code drift and a lack of full-process benchmarks.
- [Naresh Jain, 13 Oct 2026](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) [V] is the closest experiment. It used 10 paired runs per model, 178 hidden acceptance tests, one greenfield service.

| Model | No harness | With harness | Cost change (my calculation) |
|---|---|---|---|
| GPT-6 Sol | 10/10 | 10/10 | About 6.6x, with about 2.9x the time |
| GPT-6 Luna | 3/10 | 10/10 | About 3.2x, still below unharnessed Sol |

The author notes a single service and small samples, and costs exclude harness authoring. Guides and sensors were not tested separately.

- [Anthropic, Mar 2026](https://www.anthropic.com/engineering/harness-design-long-running-apps) [V, vendor, n=1 per task]: solo $9 and 20 minutes with a broken core feature, versus harness $200 and 6 hours working. The evaluator is worth its cost mainly when a task sits beyond what the model handles reliably alone.

**Frameworks** (the last three are popularity and mechanics, not effectiveness)
- [Spec Kit](https://github.com/github/spec-kit) [V]: 144.9k stars. 1.0 news dated 16 Oct 2026, now with `/speckit-converge` and extensions.
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) [V]: 73.6k stars. Propose, apply, archive, with spec deltas.
- [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) [V]: 54.9k stars. Stable v6.12, v7 expected mid-November 2026.
- [GSD](https://github.com/gsd-build/get-shit-done) [V]: archived, continues as [GSD Core](https://github.com/open-gsd/gsd-core).
- [Superpowers](https://github.com/obra/superpowers) [V]: 310.6k stars, with a separate eval harness but no published results on the page.
- Kiro [S]: reached GA in 2026, with sources conflicting on timing and tiers ([1](https://tooldirectory.ai/tools/kiro), [2](https://theaiagentindex.com/agents/kiro)).
- Tessl: last detailed review is Oct 2025. It now [also markets a skills package manager](https://tessl.io/blog/unpacking-the-unpossible-logic-of-ralph-wiggumstyle-ai-coding) [S].

### Inferences
- [I] Jain's result suggests harness value depends on the model. Frontier models may need only a final gate, and cheap models benefit from continuous sensors.
- [I] For a solo developer, the sensible default is a one-page `SPEC.md` with acceptance checks, not a full framework. Borrow OpenSpec's delta idea only for long-lived features.

### Gaps
- No evidence on maintenance costs of specs over months.
- I did not check Naresh Jain's commercial ties to contract testing tools.

---

## Part C3. What about ADRs, diagrams, grilling and adversarial review?

### Takeaway
All are cheap, but the evidence is practitioner-level. Adopt interviewing and fresh-context review first, ADRs as needed, and second-model review only for high-stakes changes.

### Cited Findings
- **Interview**: officially recommended in [Claude Code docs](https://code.claude.com/docs/en/best-practices) [V].
- **grill-me**: [the current SKILL.md](https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grill-me/SKILL.md) [V] is a thin wrapper that invokes a `grilling` skill, with model invocation disabled. A [reported flow](https://www.ai.joaoqueiros.com/blog/matt-pocock-ai-coding-skills-grill-spec-ticket-review) is grill, spec, tickets, implement, review [S]. Claims that Pocock has moved on from it are [unconfirmed](https://skillselion.com/guide/matt-pocock-skills-map) [C].
- **ADRs**: [Cane, May 2026](https://bencane.com/posts/2026-05-28-coding-agent-architectural-context/) [V, practitioner]: agents "only know what you capture". He prefers ADRs in Git, with an architecture repo added as an extra directory.
- **C4**: [Structurizr docs](https://docs.structurizr.com/ai) [V, interested party]: its model-based DSL enforces C4 rules, and it has an MCP server for validation. Mermaid can be an export target. A [practical split](https://codex.danielvaughan.com/2026/05/13/codex-cli-architecture-diagrams-mermaid-c4-plantuml-source-code-visualisation/) is Mermaid inline, Structurizr for formal docs [S].
- **Adversarial review**: OpenAI's plugin provides [/codex:adversarial-review](https://aident.ai/blog/use-codex-inside-claude-code-code-review) and warns about long unattended loops [S]. I found no controlled comparison of cross-model versus same-model review.
- **Reviewer warnings**:
  - [Claude Code docs](https://code.claude.com/docs/en/best-practices) [V]: a reviewer asked to find problems will always find something, so tell it to skip style.
  - [Anthropic's harness post](https://www.anthropic.com/engineering/harness-design-long-running-apps) [V]: Claude talked itself out of real findings until tuned.

### Inferences
- [I] Require each review finding to carry location and a failure path, and judge against `SPEC.md` rather than taste.
- [I] Default to fresh-context same-model review. Add a second model only for irreversible or high-risk decisions.
- [I] Keep ADRs short and append-only, and have agents draft while you decide.

### Gaps
- I found no evidence specific to design docs.
- I could not pin the source of the claim about agents treating edited ADRs as instructions.

---

## Part C4. What do productivity and verification studies say, and how can a solo developer evaluate a harness cheaply?

### Takeaway
Verification is the best-supported investment, though the size of the benefit is unknown. Productivity data is noisy, and self-reports overstate gains. Compare with and without on your own tasks, and delete anything showing no lift.

### Cited Findings
- **METR RCT, 2025**: tasks [19% longer with AI](https://metr.org/blog/2026-02-24-uplift-update/) (CI +2% to +39%) [V].
- **METR follow-up, Feb 2026** [V]: [57 developers, 800+ tasks](https://metr.org/blog/2026-02-24-uplift-update/).
  - Returning developers -18% time (CI -38 to +9).
  - New developers -4% (CI -15 to +9).
  - METR calls this an "unreliable signal", likely a lower bound. 30-50% of developers skipped tasks they did not want to do without AI.
  - Its [May risk report](https://metr.org/blog/2026-05-19-frontier-risk-report/) mentions small 4-20% benefits [S].
- **METR survey, May 2026** [V]: [N=349 convenience sample](https://metr.org/blog/2026-05-11-ai-usage-survey/). Median 3x speed and 1.4-2x value, self-reported. METR is sceptical.
- **DORA**:
  - [2025 report](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report): nearly 5,000 respondents, AI linked to throughput but negatively to stability [S, stale risk].
  - [2026 ROI report](https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/) [V via InfoQ]: a financial model with illustrative numbers, not new survey data.
  - I found no 2026 State of AI-assisted edition.
- **Stack Overflow 2026** [V/S]:
  - [30,000+ respondents](https://stackoverflow.blog/2026/10/06/the-results-of-the-2026-developer-survey-are-here/).
  - [6.6% (949 of 14,304) trust AI for important decisions; 48.0% trust it when they can easily verify](https://survey.stackoverflow.co/2026/ai/data/ai-trust).
  - 66% of AI users use coding agents.
  - This is a self-selected survey.
- **TDD**:
  - [Böckeler, 10 Aug 2026](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html) [V, about 22 solutions, informal]: no evidence that telling agents to do TDD adds value. 3-8.5x tokens. She stopped asking for test-first.
  - [TDAD](https://arxiv.org/abs/2603.17973) [V, preprint, open-weight models]: TDD instructions alone raised regressions to 9.94% from 6.08%. Targeted test context cut them to 1.82%.
  - [Over-mocking study](https://arxiv.org/abs/2602.00409) [S]: agents add mocks more often (36% vs 26%).
- **Context files**: [arXiv 2602.11988](https://arxiv.org/abs/2602.11988) (v3, Sep 2026) [V, preprint]: no general success gain, and cost up over 20%. Non-standard practices are the useful content. [Lulla et al.](https://blog.clawsouls.ai/en/posts/agents-md-hurts-or-helps/) reportedly found runtime and token reductions [S], so results conflict.
- **Verification**:
  - Cherny's 2-3x is [his estimate, reposted](https://venturebeat.com/technology/the-creator-of-claude-code-just-revealed-his-workflow-and-developers-are) [S]. I found no method or primary post.
  - [Docs](https://code.claude.com/docs/en/best-practices) [V] say to ask for evidence, meaning the command and its output.
  - `/goal` has a separate model check a condition after each turn.
  - `/code-review` uses a fresh subagent.
  - [Anthropic's long-running harness post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) [V, Nov 2025] used JSON feature lists and browser testing.
  - [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) [V] frames this as guides plus sensors.
- **Ralph**: [Huntley, Jul 2025](https://ghuntley.com/ralph/) [V, anecdote, stale risk]. `while :; do cat PROMPT.md | claude-code ; done`, one task per loop with fresh context, best for greenfield. He says the plugin differs from the technique. [No controlled benchmark found](https://venturebeat.com/ai/how-ralph-wiggum-went-from-the-simpsons-to-the-biggest-name-in-ai-right-now) [S].
- **`claude plugin eval`**: [docs](https://code.claude.com/docs/en/plugin-evals) [V].
  - Requires v2.1.269+.
  - Cases have a prompt plus graders, and there are no custom-code graders.
  - Three runs with and three without the plugin, reported as WITH, W/OUT and Δ with cost.
  - `claude plugin eval init` drafts cases.
  - `--runs 1 --ablation none` is the cheap iteration mode.
  - The most common first finding is Δ near zero because the skill never triggers.
  - All runs are billed.
- **skill-creator**: [docs](https://code.claude.com/docs/en/skills) [V]. Uses `evals/evals.json`, which is not interchangeable with plugin evals. For a personal skill baseline, set it `"off"` in `skillOverrides`.

### Inferences
- [I] Mandate the outcome, not the ritual. A failing reproduction test for a bug is different from telling an agent to follow red-green-refactor. Keep the former and skip the latter.
- [I] Solo eval protocol, cheapest first:
  1. Take 5-10 real tasks from your history, including a should-not-trigger case.
  2. Give each case one result grader and one process grader.
  3. Run `--runs 1` while drafting, then the default three runs for a decision.
  4. Prefer deterministic graders, and keep acceptance tests hidden from the agent.
  5. Log cost and time beside quality.
  6. Delete skills with no lift, and rerun on each model change.
- [I] For learning skills, the metric is an unaided quiz at 7 and 30 days on paired topics, one with the skill and one without. Chat performance does not count.
- [I] Run Ralph-style loops only with a machine-checkable stop condition, a budget cap and one task per iteration.

### Gaps
- No RCT covers solo developers using custom harnesses.
- No evidence separates the value of guides from sensors.
- Skill-creator's description optimization section was not read.

---

## What works, what is hype, and what should be built first?

### Takeaway
Build verification and learner state before autonomy or memory infrastructure. Start with thin skills on the existing agent, evaluate them, and treat third-party skills as untrusted code.

### Cited Findings
- [Snyk ToxicSkills, Feb 2026](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub) [S, vendor]: 13.4% of 3,984 skills had critical issues, 76 had confirmed malicious payloads, and skills inherit agent permissions.
- Memory poisoning is an [active preprint topic](https://arxiv.org/pdf/2605.15338) [S].
- [Skill descriptions load on every turn](https://code.claude.com/docs/en/skills) [V], truncated at 1,536 characters. Keep `SKILL.md` under 500 lines.
- `disable-model-invocation: true` removes a description from context, and `/skill-doctor` reports each skill's cost and how often it's used.

### Inferences

**Supported enough to adopt**
- Retrieval and spacing
- Attempt-first tutoring
- Grounded tutoring content
- Executable checks
- Fresh-context review
- Interview-then-spec
- URL and claim verification
- Markdown knowledge base
- Short human-written context files
- With-and-without evals

**Promising but thin**
- Harnesses for cheaper models
- Grounded LLM judges
- Second-model review
- Agent-graded free recall
- Local hybrid search

**Hype or unproven**
- Bloom's 2 sigma as an AI target
- "Brain damage" claims from the MIT preprint
- Vendor memory benchmark scores
- Star counts as quality signals
- Self-reported 10x gains
- Heavy SDD frameworks for solo work
- Mandated TDD rituals
- Graph memory at personal scale
- Unattended loops without stop conditions

**Build order**
1. `verify` conventions: a `SPEC.md` template, an evidence requirement, and a read-only reviewer.
2. `research` skill: a fan-out step with URL and claim-check passes, plus one chosen search API.
3. `kb` skill: Markdown vault, ingest, query and lint.
4. `learn` skill: goal diagnosis, attempt-first loop and concept file. Add a custom output style.
5. Spaced repetition: card drafting with human approval, into Anki first.
6. `plan` skill: interview, decisions, acceptance checks. Keep ADRs optional.
7. Eval suite for each of the above before adding more skills.
8. Later, and only if measured: qmd, a second-model reviewer, long-running loops.

**Security defaults**
- Read skills before installing them.
- Pin versions.
- Keep public web research apart from private data, as [OpenAI advises](https://developers.openai.com/api/docs/guides/deep-research).
- Require review before web-derived text enters long-term memory.

### Gaps
- All build-order choices are my judgement, not measured results.
- Your budget, subscription limits on native search, and subject domains are unknown, and they could change the search and tutoring choices.
