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

### 4. Example: learning a topic

Pick the researcher and say what you're curious about:

```
> I want the researcher. I want to research game theory in finance.
```

Or just say "I want to learn information theory": the step skills work without a lead too. Either way, each stage asks you before it moves on.

What follows is a conversation. The skill doing each part is in brackets:

1. **[scope]** The agent asks why you want it, how deep to go (orient, use or master), how much time you have and what you know. Then a few quick questions place your real level. It writes `mission.md`.
2. **[field-map]** "Here are the main areas, and what depends on what. Anything to drop?" You prune, and it writes `map.md`.
3. **[literature]** "Shall I find the key papers and books?" 3–5 `source-finder` agents search in parallel. Then `puck topic check` and the `claim-checker` agent verify every source and claim, and it writes `sources.json`, `raw/` and short `wiki/` pages.
4. **[reading-path]** "Here's what to read, in order": 3–7 stages, each with exact sections, a time estimate and a checkpoint question. It writes `path.md`.

Everything lands in `context/knowledge/information-theory/`. You can stop anywhere, and start mid-chain too: "find the main papers on attention" goes straight to literature.

Then study, in as many sessions as you like:

```
> I want the tutor. Let's continue with information theory.
```

- Each session opens by asking what you remember from last time. Then the agent picks the next concept whose prerequisites you've practised.
- You try each idea before it's explained.
- "Show me" gets a diagram, or an interactive HTML page that opens in your browser.
- "Give me an exercise" gets one with the answer key or tests written first, and grading by a separate agent or by the tests.
- At the end, the session is recorded and the concept statuses are updated.

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

### Research

Run them in this order for a new topic, or enter the chain anywhere.

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `scope` | "I want to learn X": the question, why, depth (orient, use or master), time, background, and a probe of your real level | `mission.md`, starting concept statuses | — | `field-map` |
| `field-map` | "What are the main areas of X?": subfields, concepts, questions, debates and prerequisites, which you prune | `map.md` | — | `literature` |
| `literature` | "Find the key papers and books on X": searches by subtopic, verifies sources and claims, writes wiki pages | `sources.json`, `raw/`, `wiki/` | `source-finder` (3–5 at once), `claim-checker` | `reading-path` |
| `reading-path` | "What should I read, and in what order?": 3–7 stages with exact sections, time and a checkpoint question | `path.md` | — | `teach` |
| `kb` | Adding a source you give it to a topic's notes, or answering from those notes with citations | `raw/`, `wiki/` | — | — |

### Learning

| Skill | Use it for | Writes | Spawns | Hands off to |
|---|---|---|---|---|
| `teach` | A study session: recall of last time, the next concept, your attempt before any explanation, then a record. Opens no task | `sessions/NNNN.md`, statuses in `map.md` | — | `practice`, `visualize` |
| `practice` | Exercises, with the answer key or tests written before you start | `exercises/<id>/` | `grader` for non-code exercises | `teach` |
| `visualize` | A Mermaid diagram, or a self-contained HTML page with steppers or sliders, when seeing it beats reading it | `visuals/*.html` | — | — |

## Agents

Agents are defined in `context/agents/`. There are two kinds, set by `mode` in each file:
- **Leads** are agents you talk to.
- **Workers** do one job in the background and return one result.

Every agent file lists its workflow, tools, skills and the workers it may start. The build adds a generated section to each agent, so it knows exactly what it has. Lint checks that the skills and workers it names exist.

### Leads: pick one after starting your harness

Start `claude`, or any harness, as usual. Then type the lead's skill, or just ask for it: "I want the researcher". The session takes on that role. Every harness supports skills, so this works the same everywhere; in Claude Code the skill is `/puck:<name>`.

Leads ask you decisions, such as your goal or depth, through the harness's question tool: in Claude Code, a list of options you can click, with your own answer always possible. Harnesses without one ask in plain text. Recall, attempts and checks in study sessions stay open questions, because a list of options would give the answer away.

| Lead | Pick it with | Workflow | Skills it uses | Workers it starts |
|---|---|---|---|---|
| `researcher` | `/puck:researcher`, or "I want the researcher" | 1. Clarifies your goal, interests, depth, time and background, one question at a time.<br>2. Maps the field.<br>3. Finds and verifies the literature.<br>4. Orders the reading.<br>5. Hands over to the tutor.<br>It searches nothing until you approve the mission | `scope`, `field-map`, `literature`, `reading-path`, `kb` | `source-finder`, `claim-checker` |
| `tutor` | `/puck:tutor`, or "I want the tutor" | Recall of last time, then the next concept, your attempt, an explanation, practice and visuals, and a record of the session | `teach`, `practice`, `visualize`, `kb` | `grader` |

### Workers: started by skills

You rarely call a worker yourself. In Claude Code you can @-mention one, for example `@agent-puck:grader`, and give it the inputs below. It works in the background and hands back its result. `/agents` lists them.

| Agent | Does | Tools | Give it | Started by |
|---|---|---|---|---|
| `source-finder` | Finds and records sources for one subtopic, each with an exact quote as evidence. Refuses a topic without an approved `mission.md` | read, web, shell | Topic, one subtopic as a question, the mission's goal and depth, search limit | `literature` |
| `claim-checker` | Checks each wiki claim against the source text it cites | read | Wiki page paths and the topic folder | `literature` |
| `grader` | Scores an attempt 0 or 1 per rubric criterion, without seeing the teaching conversation | read | The attempt, plus `prompt.md`, `key.md` and `rubric.md` | `practice` |
| `reviewer` | Reviews a code change with fresh eyes | read, shell-read | The change or diff range, and the requirement | `review` |
| `retro` | Sorts a finished task's findings into one-offs, topic wiki pages, skills, project notes or rules | read, shell, edit | The task ID and folder | `task` at close |

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
| `puck lint` | Checks skills, agents, hooks and context budgets | yes |
| `puck build` | Lints, then generates the host packages in `dist/` | — |
| `puck skill new <name> --description … --origin …` | Creates a draft skill from the template | — |
| `puck skill promote <name> [--no-evals]` | Lints, runs evals, activates, rebuilds and commits one draft skill. The task skill runs it only when you say yes | — |
| `puck hook <id> --event … --host …` | Entry point the host calls for hooks; not for direct use | — |

### Work: tasks, notes and experiments

| Command | Does | Pre-approved |
|---|---|---|
| `puck task start "<goal>" [--type build\|plan\|research\|learn] [--worktree]` | Opens a task and prints its context pack | yes |
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
| `puck topic new "<name>"` | Creates a topic folder with templates | yes |
| `puck topic list` | Lists topics | yes |
| `puck topic check <topic> [--has mission,map,path,sources] [--no-links]` | The one validator for a topic. Fails unless the named files are written, DOIs and URLs resolve, quotes match `raw/`, and every wiki claim cites a source whose `raw/` text holds its quotes and numbers. Rebuilds the wiki's `index.md` | yes |
| `puck sources search "<query>" [--kind any\|paper\|survey\|book] [--limit N] [--json]` | Searches OpenAlex, Semantic Scholar, arXiv and Open Library, merged and ranked by citations | yes |
| `puck sources graph <ref> [--direction references\|cited-by] [--limit N] [--since YEAR]` | What a work builds on, or what builds on it | yes |
| `puck sources add <topic> <ref>` or `--url … --title …` | Adds or merges a ledger entry. Options: `--role anchor\|canon\|frontier\|textbook\|practical\|critique`, `--why`, `--quote`, `--group`, `--kind`, `--author`, `--year` | yes |
| `puck sources list <topic>` | Lists the ledger | yes |
| `puck sources fetch <topic> <id> [--file F\|- --origin "<url, pages>"] [--force]` | Saves a source's text to `raw/`: its abstract or page, or with `--file`, text an agent read itself, such as from a PDF | yes |
| `puck learn status <topic>` | Concept statuses and the last session | yes |
| `puck learn next <topic>` | The next concept whose prerequisites are practised | yes |
| `puck learn record <topic> --file F\|- [--status concept=status …]` | Writes the session record and updates statuses | yes |
| `puck learn open <path>` | Opens an HTML visual in the browser | yes |
| `puck learn check <topic> <id>` | Runs a code exercise's tests; only exit 0 passes | — |

Concept statuses: `unseen`, `introduced`, `practised`, `recalled-later`, `can-explain`.

Optional keys from the environment: `OPENALEX_API_KEY`, `S2_API_KEY`. Without `S2_API_KEY`, Semantic Scholar often rate-limits, which shows as a warning.

## Hooks

Defined in `context/hooks.yaml`. Both fail open, so a broken hook never blocks you.

| Hook | When | Does |
|---|---|---|
| `resume` | Session start, and after compaction | Tells the model what Puck is and where its home is, then gives the rules and the open task's checklist for this folder |
| `close-guard` | The model tries to stop | Once per task, blocks a stop when the task passes its checks but was never closed, and asks for the retro and the close |
