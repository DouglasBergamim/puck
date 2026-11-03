# Puck features

Every skill, agent, command and hook Puck has today. The source of truth is `context/` for skills, agents and hooks, and `src/cli/commands/` for commands. Update this page when they change.

## Walkthrough on Claude Code

### 1. Set up, once

From this repository:

```sh
./puck install
```

That's the only setup command, and the only thing you interact with is Puck:
- If [uv](https://docs.astral.sh/uv/) isn't installed, `./puck` asks before installing it with uv's official installer.
- If the `puck` command isn't on your PATH yet, `install` puts it there.
- It links `~/.claude/skills/puck` to `dist/claude`, so every new `claude` session loads Puck.
- It adds Puck's pre-approved commands, its home folder and `PUCK_HOME` to `~/.claude/settings.json`. Everything else in that file stays as it was.

After that, run plain `puck install` from anywhere to repair or refresh the setup. `puck uninstall` removes what `install` added to Claude.

After you edit anything in `context/`, run `puck build`. New sessions pick the change up, with no reinstall.

### 2. Start Claude with Puck

```sh
cd ~/coding/some-project
claude
```

Nothing else is needed. At session start, the `resume` hook tells the model what Puck is, where its home is, and the rules, plus the checklist of any task still open in this folder. To check that Puck is loaded:
- Type `/puck:`: the skills should autocomplete.
- Run `/agents`: `puck:source-finder` and the other workers should be listed.
- Ask "what is Puck?"

To try Puck without installing it, `puck run` starts one session with it loaded.

### 3. Example: a coding task

In a git project, ask for real work:

```
> Add a --verbose flag to the CLI, with a test.
```

The `task` skill takes it from there. You don't run any `puck` command yourself:
1. The agent runs `puck task start "<goal>"`. The task folder is `.puck/tasks/<id>/` in the repository, which git ignores. It holds `SPEC.md`, `findings.md` and `scratch/`.
2. It writes the plan in `SPEC.md`, and adds each step with the command that proves it done: `puck task step "Flag parsed" --check "uv run pytest tests/test_cli.py"`.
3. It works, noting anything non-obvious with `puck note`.
4. It runs `puck task check <step>` for each step. Claude asks you before each check, because a check runs a command the model wrote. For a non-trivial change, the `review` skill sends the diff to the `reviewer` agent.
5. If there were findings, the `retro` agent sorts them. A new procedure becomes a draft skill, and a change to an existing skill becomes a diff in `scratch/drafts/`.
6. It closes the task with `puck task close`, then reports. If the retro drafted skills, it asks you about each one, and promotes only those you approve.

Useful along the way:
- **Don't know what to build yet?** Say "help me plan a sync service". The `plan` skill interviews you and writes `SPEC.md`.
- **Session ended mid-task?** Open `claude` in the same folder. The `resume` hook shows the open task's checklist, so you can say "continue".
- **Parallel work:** ask the agent to start the task with `--worktree`. Each worktree sees only its own task.

### 4. Example: learning a subject

Pick the professor and say what you want to learn:

```
> /puck:professor I want to learn game theory applied to finance
```

Or just say "I want to learn information theory". It asks you at two points: one round of scoping questions, and your yes on the roadmap. In between it runs on its own, saying what each stage produced; step in whenever you want to change something. The skill doing each part is in brackets:

1. **[scope]** It drafts the mission from what you said: the subject (game theory), where it's applied (finance), a goal you could be tested on, and the depth (orient, use or master). It asks at most two questions in one go, such as what's at the centre and what it's for. It doesn't ask about your time or quiz your level. It writes `mission.md`.
2. **[curriculum]** Two `source-finder` agents search in parallel: one for how the subject is taught (textbooks, courses, syllabi, reading lists and "best book" discussions; docs and articles for tech), one for the application's classics. `puck topic check` verifies every link and quote. It writes `sources.json` and `raw/`.
3. **[roadmap]** 3–7 stages from the subject's foundations out to the application, in the order the syllabi and textbooks agree on. Each has chapters or lectures, a time estimate and a checkpoint question; the last checkpoint is your goal. It writes `path.md` and the concept table in `map.md`, then opens the roadmap page in your browser and asks you to agree it or change it. Study starts only after your yes: until `path.md` says `Agreed:` with a date, `puck learn next` refuses.

Everything lands in `context/knowledge/<topic>/`. Then study, in as many sessions as you like:

```
> /puck:professor Let's continue with game theory.
```

- The first session starts from what you said you know; your first attempt shows your real level. Later sessions open by asking what you remember from last time.
- The agent picks the next concept whose prerequisites you've practised, and you try it before it's explained.
- "Show me" gets a diagram, or an interactive HTML page that opens in your browser.
- "Give me an exercise" gets one with the answer key or tests written first, and grading by a separate agent or by the tests.
- At the end, the session is recorded and the concept statuses are updated.

### 5. Example: a research question

```
> /puck:researcher What's known about high-frequency trading and liquidity?
```

1. **[scope]** The question, what it's for, the areas to cover and the depth, in `mission.md`.
2. **[field-map]** Subfields, concepts and debates for those areas, in `map.md`.
3. **[literature]** One `source-finder` per subtopic plus one for criticism. Then `puck topic check` and the `claim-checker` agent verify every source and claim, and it writes `wiki/` pages.
4. **[report]** `report.md`: the answer, what's settled, what's disputed and by whom, what's open, and what to read first, every claim cited.

Once the mission is written, the researcher opens one task with `--agent researcher --topic <topic>`. Its steps are these four stages, each checked by `puck topic check`, so `puck task show` says how far the run got.

### 6. Example: a new skill or agent

```
> /puck:constructor I want a skill that writes a changelog entry from the commits on my branch
```

It classifies the need (here, a skill, not a command or a lead), drafts the design and asks at most three questions, writes it with `puck skill new` and evals, has the `reviewer` check it against `docs/concepts.md`, and promotes it only when you say yes.

Other things you can just say:
- "Where am I with information theory?"
- "Add this chapter to my information-theory notes: <link or file>"
- "What do my notes say about channel capacity?"

If the agent doesn't pick the skill you meant, name it: `/puck:teach information-theory`. Every skill below can be called this way.

## Skills

Skills run in your conversation. In Claude Code, call one as `/puck:<name>`, or just ask, and the model picks it from its description.

### Coding and planning

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `task` | Non-trivial work, from start to a verified close: building or fixing code, or a full research run | A task with steps and checks | `retro` at close, when findings exist | `review` before close |
| `plan` | An undecided goal: interviews you and writes a one-page spec | `SPEC.md` | — | `task` |
| `review` | Reviewing a change or diff against its `SPEC.md` or requirement, or checking it's ready to merge | `review.md` | `reviewer` | — |
| `onboard` | Getting up to speed on a project: what it is, layout, commands (found vs verified), rules, what's in flight, gaps. Reads only and opens no task | A brief in chat | — | `plan` or `task` |
| `commit` | "Commit this": groups the changes into logical commits in the project's message style, stages by path, leaves out secrets, build output and your other staged work. Pushes only when asked | Commits | — | — |

`scope` is shared: it writes the mission for both chains, from `mission-learn.md` or `mission-research.md`.

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `scope` | "I want to learn X" or "what's known about Q?": drafts the mission, then asks at most two questions in one go | `mission.md` | — | `curriculum` or `field-map` |
| `kb` | Adding a source you give it to a topic's notes, or answering from those notes with citations | `raw/`, `wiki/` | — | — |

### Learning

Run them in this order for a new subject, or enter the chain anywhere.

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `curriculum` | "What should I learn X from?": textbooks, courses, syllabi, reading lists, discussions, and the application's classics | `sources.json`, `raw/` | `source-finder` (2 at once) | `roadmap` |
| `roadmap` | "What should I read, and in what order?": 3–7 stages from foundations to application, with chapters, time and a checkpoint question, shown as a page in your browser for your yes | `path.md`, `map.md`, `visuals/roadmap.html` | — | `teach` |
| `teach` | A study session: recall of last time, the next concept, your attempt before any explanation, then a record. Opens no task | `sessions/NNNN.md`, statuses in `map.md` | — | `practice`, `visualize` |
| `practice` | Exercises, with the answer key or tests written before you start | `exercises/<id>/` | `grader` for non-code exercises | `teach` |
| `visualize` | A Mermaid diagram, or a self-contained HTML page with steppers or sliders, when seeing it beats reading it | `visuals/*.html` | — | — |

### Research

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `field-map` | "What are the main areas of research on Q?": subfields, concepts, debates and prerequisites, within the mission's areas | `map.md` | — | `literature` |
| `literature` | "Find the key papers on Q": searches by subtopic plus criticism, verifies sources and claims, writes wiki pages | `sources.json`, `raw/`, `wiki/` | `source-finder` (3–5 at once), `claim-checker` | `report` |
| `report` | "What does the literature conclude?": the answer, what's settled, disputed and open, and what to read first, all cited | `report.md` | — | — |

## Agents

Agents are defined in `context/agents/`. There are two kinds, set by `mode` in each file:
- **Leads** are agents you talk to.
- **Workers** do one job in the background and return one result.

Every agent file lists its tools, skills and the workers it may start. A lead also has a `workflow:` of stages, each with a skill, what it delivers and the check that proves it, and a `Context` section saying what it reads first. The build adds a generated section to each agent with its tools, skills, workers and, for a lead, a "Workflow and deliverables" table, so it knows exactly what it has. Lint checks the stages, the sections and that the skills and workers it names exist. `docs/concepts.md` has the full specification.

### Leads: pick one after starting your harness

Start `claude`, or any harness, as usual. Then type the lead's skill, or just ask for it: "I want the professor". The session takes on that role. Every harness supports skills, so this works the same everywhere; in Claude Code the skill is `/puck:<name>`.

Leads ask you decisions, such as your goal or depth, through the harness's question tool: in Claude Code, a list of options you can click, with your own answer always possible. Harnesses without one ask in plain text. Recall, attempts and checks in study sessions stay open questions, because a list of options would give the answer away.

| Lead | Pick it with | Workflow | Skills it uses | Workers it starts |
|---|---|---|---|---|
| `professor` | `/puck:professor`, or "I want to learn X" | **Plan**, once per topic: 1. Scope the mission. 2. Find how the subject is taught. 3. Build the roadmap.<br>**Study**, every session after: recall of last time, the next concept, your attempt, an explanation, practice and visuals, and a record of the session.<br>It asks you only at scoping and to agree the roadmap; study waits for that yes | `scope`, `curriculum`, `roadmap`, `teach`, `practice`, `visualize`, `kb` | `source-finder`, `grader` |
| `researcher` | `/puck:researcher`, or "what's known about Q?" | 1. Scope the question.<br>2. Map the field.<br>3. Find and verify the literature, with its critics.<br>4. Write a cited report.<br>Only scoping asks you anything; it searches nothing until the mission is written | `scope`, `field-map`, `literature`, `report`, `kb` | `source-finder`, `claim-checker` |
| `engineer` | `/puck:engineer`, or "take this change from the codebase to a commit" | 1. **onboard**: a project brief.<br>2. **plan**: `SPEC.md`, when the goal is undecided.<br>3. **build**: the task skill, through checks, review, retro and close.<br>4. **commit**: only when you ask.<br>Only planning asks you anything | `onboard`, `plan`, `task`, `review`, `commit` | `reviewer`, `retro` |
| `constructor` | `/puck:constructor`, or "make a Puck skill that…" | 1. **classify**: which primitive, new or a change.<br>2. **design**: drafted, then at most 3 questions.<br>3. **write**: scaffolded and written to `docs/concepts.md`, with evals; `puck lint` passes.<br>4. **review**: the `reviewer` against the spec.<br>5. **activate**: promote or build, only on your yes | `task`, `review` | `reviewer` |

### Workers: started by skills

You rarely call a worker yourself. In Claude Code you can @-mention one, for example `@agent-puck:grader`, and give it the inputs below. It works in the background and hands back its result. `/agents` lists them.

| Agent | Does | Tools | Give it | Started by |
|---|---|---|---|---|
| `source-finder` | Finds and records sources for one brief, starting from what people recommend (syllabi, reading lists, discussions, docs) before the academic search, each with an exact quote as evidence. Refuses a topic without a `mission.md` | read, web, shell | Topic, one brief, the mission's subject or question and depth, about 12 searches and at most 6 sources | `curriculum`, `literature` |
| `claim-checker` | Checks each wiki claim against the source text it cites | read | Wiki page paths and the topic folder | `literature` |
| `grader` | Scores an attempt 0 or 1 per rubric criterion, without seeing the teaching conversation | read | The attempt, plus `prompt.md`, `key.md` and `rubric.md` | `practice` |
| `reviewer` | Reviews a code change with fresh eyes | read, shell-read | The change or diff range, and the requirement | `review` |
| `retro` | Sorts a finished task's findings into one-offs, topic wiki pages, draft skills and diffs to existing skills. Never touches instructions | read, shell, edit | The task ID and folder | `task` at close |

## Commands

Commands are deterministic: anything a program can compute exactly is a command, not a prompt. **Pre-approved** means agents can call it without asking you, after `puck install` or under `puck run`.

There are three kinds:
- **Setup**, which you run: `install`, `uninstall`, `run`, `build`, `status`, `skill`.
- **Validation**, one per level: `lint` for Puck's own skills and agents, `task check` for a step, `topic check` for a study topic, `learn check` for an exercise.
- **Per area**, which agents call while working: `task`, `note` and `scratch` for work; `topic`, `sources` and `learn` for research and study.

### Puck itself

| Command | Does | Pre-approved |
|---|---|---|
| `puck run [host] [args…]` | Lints, builds, then starts the host with Puck loaded. If `host` isn't a known host, it's the first message | — |
| `puck install [host]` | Loads Puck in every session of the host: links the package and adds permissions to the host's user settings | — |
| `puck uninstall [host]` | Removes what `install` added | — |
| `puck status [--json]` | Shows Puck's state | yes |
| `puck lint [--root PATH]` | Checks skills, agents, hooks, eval files and context budgets, that `docs/features.md` has a row for every active skill, agent and hook and none for anything else, and that `/puck:<name>` and skill chains such as `scope` → `field-map` in the docs name real skills and agents. `--root` lints another copy, such as the pre-commit hook's snapshot of staged files | yes |
| `puck build` | Lints, then generates the host packages in `dist/` | — |
| `puck skill new <name> --description … --origin …` | Creates a draft skill from the template | — |
| `puck skill promote <name> [--no-evals]` | Lints, runs evals, activates, rebuilds and commits one draft skill. It needs the skill's row in `docs/features.md` first, and commits that file with the skill's folder; anything else you staged stays staged. Runs only when you say yes | — |
| `puck agent new <name> --mode worker\|lead --description …` | Creates an agent from `templates/agent.md` or `templates/agent-lead.md`. Refuses a duplicate, or a lead named like a skill | — |
| `puck hook <id> --event … --host …` | Entry point the host calls for hooks; not for direct use | — |

### Work: tasks, notes and experiments

| Command | Does | Pre-approved |
|---|---|---|
| `puck task start "<goal>" [--type build\|plan\|research\|learn] [--worktree] [--agent LEAD] [--topic TOPIC]` | Opens a task and prints its context pack. With `--agent`, the lead's workflow stages that have checks become the steps. With `--topic`, the SPEC points to the topic's `mission.md` | yes |
| `puck task list [--all]` | Lists open tasks, or all of them | yes |
| `puck task show [--task ID] [--json]` | Shows a task and its steps | yes |
| `puck task step "<description>" --check "<command>"` | Adds a step with the command that proves it done | yes |
| `puck task check <step>` | Runs a step's check | — |
| `puck task close [--outcome done\|partial\|abandoned]` | Closes a task. `done` needs every step passing, and a retro when findings exist. Also removes scratch from tasks closed over 14 days ago | yes |
| `puck note "<text>" --type procedure\|topic\|one-off` | Records a finding for the retro | yes |
| `puck scratch new <name>` | Makes a disposable experiment folder | yes |
| `puck scratch log --hypothesis … --command-run … --result … --verdict …` | Logs an experiment | yes |

### Learning: topics, sources and study

Source references look like `openalex:W…`, `s2:…`, `arxiv:…`, `ol:OL…W` or `doi:10.…`.

| Command | Does | Pre-approved |
|---|---|---|
| `puck topic new "<name>" [--kind learn\|research]` | Creates a topic folder with templates. The kind picks the mission template: a subject to learn (default) or a question to research | yes |
| `puck topic list` | Lists topics | yes |
| `puck topic check <topic> [--has mission,map,path,sources,report] [--no-links]` | The one validator for a topic. Fails unless the named files are written (a mission needs each of its sections filled and a valid depth), DOIs and URLs resolve, quotes match `raw/`, and every wiki claim cites a source whose `raw/` text holds its quotes and numbers. Rebuilds the wiki's `index.md` | yes |
| `puck sources search "<query>" [--kind any\|paper\|survey\|book] [--limit N] [--json]` | Searches OpenAlex, Semantic Scholar, arXiv and Open Library, merged and ranked by citations | yes |
| `puck sources graph <ref> [--direction references\|cited-by] [--limit N] [--since YEAR]` | What a work builds on, or what builds on it | yes |
| `puck sources add <topic> <ref>` or `--url … --title …` | Adds or merges a ledger entry. Options: `--role anchor\|canon\|frontier\|textbook\|practical\|critique\|recommendation`, `--kind paper\|survey\|book\|course\|doc\|web\|discussion`, `--why`, `--quote`, `--group`, `--author`, `--year`, and `--fetch` to save its text to `raw/` in the same command | yes |
| `puck sources list <topic>` | Lists the ledger | yes |
| `puck sources fetch <topic> <id> [--file F\|- --origin "<url, pages>"] [--force]` | Saves a source's text to `raw/`: its abstract or page, or with `--file`, text an agent read itself, such as from a PDF | yes |
| `puck learn status <topic>` | Concept statuses and the last session | yes |
| `puck learn next <topic>` | The next concept whose prerequisites are practised. Refuses while the topic's roadmap isn't agreed | yes |
| `puck learn roadmap <topic> [--no-open]` | Writes the roadmap page, `visuals/roadmap.html`, from `path.md`, `map.md` and `sources.json`, and opens it: the stages with readings, times and checkpoints, each concept's status, and a progress bar | yes |
| `puck learn record <topic> --file F\|- [--status concept=status …]` | Writes the session record and updates statuses | yes |
| `puck learn open <path>` | Opens an HTML visual in the browser | yes |
| `puck learn check <topic> <id>` | Runs a code exercise's tests; only exit 0 passes | — |

Concept statuses: `unseen`, `introduced`, `practised`, `recalled-later`, `can-explain`.

Optional keys from the environment: `OPENALEX_API_KEY`, `S2_API_KEY`. Without `S2_API_KEY`, Semantic Scholar often rate-limits, which shows as a warning.

## Git hooks for Puck's own repository

Tracked in `.githooks/`; `puck install` turns them on by setting `core.hooksPath` (and never replaces a value you set yourself), and `puck uninstall` turns them off. Unlike Puck's hooks below, they fail closed: fix what they report, never commit with `--no-verify`.

| Git hook | Runs |
|---|---|
| pre-commit | `puck lint --root` and `ruff check src tests` (pyflakes rules only) on a snapshot of exactly the staged files, so unstaged edits can't make a commit pass or fail |
| pre-push | `uv run pytest -q` |

The lint code itself runs from the working tree; only the content comes from the snapshot.

## Hooks

Defined in `context/hooks.yaml`. Both fail open, so a broken hook never blocks you.

| Hook | When | Does |
|---|---|---|
| `resume` | Session start, and after compaction | Tells the model what Puck is and where its home is, then gives the rules and the open task's checklist for this folder |
| `close-guard` | The model tries to stop | Once per task, blocks a stop when the task passes its checks but was never closed, and asks for the retro and the close |
