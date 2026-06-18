# AgentPipeline

A Claude Code plugin marketplace with two reusable plugins for
[Claude Code](https://code.claude.com):

- **[`agent-pipeline`](#the-pipeline)** — a multi-agent *development* pipeline
  (Plan → Code → Test → Review → Explain).
- **[`storm-research`](#storm-research-plugin)** — the Stanford STORM *research*
  method: turn any topic into a sourced, reliability-scored briefing.

Both install from the same marketplace and work in every repo, locally and in the
cloud. The development pipeline is documented first; the research plugin follows.

You type one command and a chain of specialist subagents takes a feature from
request to reviewed, tested, and explained code — each one staying in a clean,
narrow context and handing off to the next through a shared `.pipeline/` folder.

Run it interactively while you work, autonomously overnight, or on a schedule in
the cloud so features land while your computer is off.

## The pipeline

| Stage | Agent | Model | Role |
|------|-------|-------|------|
| 0 | **map** *(optional)* | — | If the [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) plugin is installed, builds a codebase knowledge graph the Planner reads first. Skipped silently if absent. |
| 1 | **planner** | opus | Turns your request into a tight spec at `.pipeline/spec.md`. Never writes code. |
| 2 | **coder** | sonnet | Implements the spec exactly. Summarizes to `.pipeline/changes.md`. |
| 3 | **tester** | sonnet | Writes and runs tests. Reports to `.pipeline/test-results.md`. Never fixes the code. |
| 4 | **reviewer** | opus | Read-only gate. First line of `.pipeline/review.md` is a machine-readable `VERDICT: SHIP / NEEDS WORK / BLOCK`. |
| 5 | **explainer** | opus | Read-only teaching pass. Walks you through what was built and why, in `.pipeline/explanation.md`. |

The split keeps each agent focused, and the read-only Reviewer and Explainer
can't paper over problems — they can only judge and teach.

About 70% of token spend lands on the cheaper Sonnet model (Coder + Tester),
30% on Opus (Planner, Reviewer, Explainer), which run once per feature where
reasoning quality matters most.

### The contracts

Each handoff is a **contract**, so the pipeline stays honest instead of just
producing plausible-looking diffs:

- **Repo contract** — `REPO_CONTRACT.md` (committed). A short, curated index of
  the codebase's canonical files and patterns: schemas, validators, utils,
  naming, errors, auth, tests, and package policy. Generate it with `/map-repo`;
  the Planner reads it every run so specs reuse what exists.
- **Task contract** — `.pipeline/spec.md`. Before code: the behavior, the
  **allowed/forbidden files**, the package policy, and concrete **acceptance
  checks** the run will be judged against.
- **Diff contract** — `.pipeline/changes.md`. After code: for each changed
  surface, *why* it changed, what pattern it reused, and what would break if
  reverted.
- **Evidence contract** — `.pipeline/test-results.md`. Acceptance checks marked
  verified or not, plus skipped checks, manual verification, and known risks.
  No "done" without evidence.
- **Stop rules** — the Coder stops rather than silently adding a dependency,
  changing a shared interface, inventing a new convention, skipping a test, or
  touching auth/data migrations. Interactively, `/ship` surfaces the trigger to
  you; unattended, `/ship-overnight` hard-blocks the risky ones (deps, shared
  interfaces, auth/migrations) and records the rest as assumptions.

The **Reviewer enforces the contracts as a hard gate** (`VERDICT: NEEDS WORK` /
`BLOCK` if one is missing or violated), and the **Explainer** turns them into a
learning walkthrough — reading the *why* straight from the diff contract rather
than re-deriving it. Only committed `REPO_CONTRACT.md` is persistent; the rest
live in the gitignored `.pipeline/` folder per run.

## Commands

- **`/map-repo [focus]`** — have Opus (the **cartographer** agent) index the
  codebase into a committed `REPO_CONTRACT.md`: the canonical file (and example
  symbol) for schemas, validators, utils, naming, errors, auth, tests, and the
  package policy. Run it once per repo and refresh it when the codebase drifts;
  the Planner reads it on every run. Read-only with respect to source code.
- **`/ship <feature request>`** — the interactive pipeline. Cleans `.pipeline/`,
  then Map → Plan → Code → Test → Review → Explain. Shows you a plain-language
  recap of the plan, and stops for open questions or test failures. Never merges.
- **`/ship-overnight <feature request>`** — the autonomous pipeline. Creates its
  own branch, runs end to end without stopping, and includes a **bounded auto-fix
  loop**: if the Reviewer says NEEDS WORK or BLOCK, it feeds the feedback back to
  the Coder and retries (up to 2 rounds). If it still can't ship, the Explainer
  writes up exactly *why it's stuck* and the smallest next step. Either way it
  pushes the branch and leaves a committed morning report — **no PR, no merge**.
  With no argument it pulls the next unchecked item from the `## Ready to build`
  section of a `FEATURES.md` backlog.
- **`/suggest-features [focus]`** — have Opus (the **scout** agent) review the
  codebase and its knowledge graph and propose small, evidence-backed candidates
  into the `## Proposed` section of `FEATURES.md`. It only proposes — you promote
  the ones you want into `## Ready to build`. Great as a grooming pass before a
  night of `/ship-overnight` runs.
- **`/explain <file | module | feature>`** — run just the Explainer on demand to
  learn any part of the codebase. With no argument, it explains your most recent
  changes.

```
/map-repo
/ship add rate limiting to the login endpoint, max 5 attempts/min/IP, return 429
/ship-overnight build a CSV export endpoint for the reports table
/suggest-features focus on test-coverage gaps in the auth module
/explain src/auth/session.py
```

When installed as a plugin the commands are namespaced: `/agent-pipeline:map-repo`,
`/agent-pipeline:ship`, `/agent-pipeline:ship-overnight`,
`/agent-pipeline:suggest-features`, `/agent-pipeline:explain`.

## Install (recommended: as a plugin)

This repo is also a Claude Code plugin marketplace. Install once and the agents
and commands are available in every repo.

```bash
/plugin marketplace add at3gk/agentpipeline
/plugin install agent-pipeline@agent-pipeline-marketplace
/reload-plugins
```

To develop or try it locally without installing:

```bash
claude --plugin-dir ./plugins/agent-pipeline
```

## Keeping it up to date

The plugin is versioned, so new releases reach you cleanly. Two ways:

**Automatic (set once).** Run `/plugin`, open the **Marketplaces** tab, select
`agent-pipeline-marketplace`, and choose **Enable auto-update**. Claude Code then
refreshes the marketplace and updates the installed plugin at startup, prompting
you to `/reload-plugins` when something changed. (Third-party marketplaces have
auto-update off by default, which is why this is a one-time opt-in.)

**Manual (anytime).**

```bash
/plugin marketplace update agent-pipeline-marketplace
/reload-plugins
```

You only receive an update when the plugin's `version` in `plugin.json` changes,
so updates are deliberate rather than every-commit churn.

## Companion: Understand-Anything (the Map stage)

The pipeline works on its own, but Stage 0 lights up when you also install
[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) — a plugin
that analyzes a codebase into a knowledge graph at
`.understand-anything/knowledge-graph.json`. The **Planner reads that graph first**,
so the spec points at real files, functions, and patterns and the Coder follows
existing conventions instead of guessing. It's a soft dependency: present → richer
plans; absent → the Planner just explores the code directly.

Install it from its own marketplace:

```bash
/plugin marketplace add Egonex-AI/Understand-Anything
/plugin install understand-anything@understand-anything
/reload-plugins
```

Then generate the map once per repo (refresh it after big changes):

```bash
/understand
```

> Plugins run code on your machine — review Understand-Anything's source and
> only install marketplaces you trust.

## Running it overnight (locally)

1. Make sure your working tree is clean (the autonomous command refuses a dirty tree).
2. Run `/ship-overnight <your request>` — it creates a `claude/overnight-<slug>-<date>`
   branch, runs the whole loop, commits each round, and pushes the branch.
3. In the morning, read `reports/<branch>.md` for the verdict and summary, and
   `.pipeline/explanation.md` for the full walkthrough. If it says SHIPPED and the
   code looks right, merge. If BLOCKED, the report tells you exactly where it stopped.

The pipeline never merges. You are the final gate.

## Running it in the cloud (no computer left on)

This is the real fix for "I don't want to leave my laptop running." With
[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web),
the pipeline runs in an Anthropic-managed cloud container — your machine can be
closed — and results come back as a pushed branch.

> **Cloud sessions don't have the interactive plugin manager.** `/plugin
> marketplace add` and `/plugin install` open a terminal picker that doesn't exist
> on the web, and a fresh container never carries your personal `~/.claude/`. So
> the marketplace install you did locally is *not* present in a cloud session.
> What loads in the cloud is whatever the repo **commits** under `.claude/`. Two
> ways to get the pipeline there: **(a) vendor it into the repo** — run this repo's
> [`install.sh`](#install--option-b-vendor-the-files-into-a-repo), which copies the
> agents/commands into `.claude/agents/` and `.claude/commands/` (auto-discovered,
> zero install); or **(b) declare the plugin in committed settings** — add
> `extraKnownMarketplaces` + `enabledPlugins` to the repo's `.claude/settings.json`,
> which the cloud fetches at startup *if the network policy allows reaching the
> marketplace*. Vendoring (a) has no network dependency and is the most reliable.

**One-off cloud run:** at [claude.ai/code](https://claude.ai/code), connect GitHub,
create a cloud environment for your repo, and submit `/ship-overnight <feature>`.

**Scheduled, unattended runs (recommended for overnight):** use a
[**Routine**](https://code.claude.com/docs/en/routines) — a saved prompt + repo +
environment that fires on a trigger, with **no machine of yours involved**:

1. Create a cloud environment for your repo. Set the network policy to **Trusted**
   (or higher) so test dependencies — and Understand-Anything — can install.
2. Add a **SessionStart hook** to your project's `.claude/settings.json` so the
   fresh container has your test tooling — copy [`examples/claude-settings.json`](examples/claude-settings.json)
   and trim its command to your stack.
3. Copy [`examples/FEATURES.md`](examples/FEATURES.md) to your repo root and fill in
   the `## Ready to build` section. (Or run `/suggest-features` and promote the
   candidates it proposes.)
4. At [claude.ai/code/routines](https://claude.ai/code/routines), create a Routine
   on a **Schedule** trigger (e.g. daily at 2am) with the prompt `/ship-overnight`
   (no argument). Each night it grabs the next item from `## Ready to build`, ships
   it to a `claude/overnight-*` branch, checks the box, and pushes — ready for your
   review with coffee. (Routines can also be triggered by GitHub events or an API call.)

**Optional: let it refill its own backlog.** Add a second Routine on a slower
schedule (say, weekly) running `/suggest-features`. It proposes candidates into
`## Proposed` — it never ships them — so you skim the list and promote what you
want. This keeps "decide what to build" a human-gated step while the nightly
shipper handles "build it."

> Cloud containers are ephemeral and clone the repo fresh, so only committed
> files travel — which is why the morning report is committed to `reports/` rather
> than left in the gitignored `.pipeline/` folder. Personal `~/.claude/` config does
> not carry to the cloud, and the interactive `/plugin install` you ran locally is
> not present either — so the pipeline reaches the cloud only because it's **committed
> under `.claude/`** (vendored via `install.sh`) or **declared in committed
> `.claude/settings.json`**, per the note above.

## Install — option B: vendor the files into a repo

If you'd rather copy the agents and commands straight into a project (no plugin
system), run the install script from this repo:

```bash
/path/to/AgentPipeline/install.sh            # into the current directory
/path/to/AgentPipeline/install.sh ~/code/app # or a specific repo
```

It copies the agents into `<repo>/.claude/agents/`, the commands into
`<repo>/.claude/commands/`, and adds `.pipeline/` to the repo's `.gitignore`.
Commands are then `/map-repo`, `/ship`, `/ship-overnight`, `/suggest-features`,
and `/explain` (no namespace).

## Tips

- **Be specific.** "Add rate limiting, max 5/min per IP, return 429" beats "add
  rate limiting somewhere." A tighter request makes a tighter spec.
- **Start small.** Bounded features (an endpoint, a settings page, one module)
  first; scale up once you trust it.
- **Read the `.pipeline/` files.** Even on SHIP, reading spec / changes /
  test-results / review / explanation teaches you how each agent thinks.
- **Parallel features** want separate git worktrees so agents don't edit the same
  files.

## STORM research plugin

The second plugin in this marketplace, **`storm-research`**, is a *research* tool,
not a coding one. It runs the [Stanford STORM method](https://storm.genie.stanford.edu)
(Stanford OVAL Lab, NAACL 2024) inside Claude: instead of the one-prompt majority
view, it simulates **five expert perspectives** on your topic — the practitioner,
the academic, the skeptic, the economist, and the historian — then makes the
disagreements between them do the work. In Stanford's peer-reviewed testing this
produced articles ~25% more organized and ~10% broader than single-prompt research.

It runs four phases in one continuous context (each reads the last):

1. **Multi-Perspective Scan** — all five expert reads of the topic.
2. **Contradiction Map** — where they clash, what they *all* agree on (likely
   true), and what *none* of them addressed (the field's blind spot).
3. **Synthesis** — a 60-second CEO summary, five findings ranked by reliability, a
   hidden cross-perspective connection, a specific action for your role, and the
   frontier question.
4. **Peer Review** — the briefing grades itself: confidence scores, weakest link,
   bias check, a possible missing angle, and a letter grade. This is STORM's
   built-in guard against its own known weakness (source bias / fact misassociation).

When web tools are available it grounds the personas in real sources and attaches a
**Sources** list; otherwise it runs from model knowledge and says so plainly.

### Use it

- **Skill (automatic).** Just ask Claude to *research a topic properly* — "research
  the state of solid-state batteries", "I need to understand X before a decision" —
  and the `storm-research` skill kicks in. Great before writing, a business or
  investment decision, an interview, a negotiation, or a presentation.
- **`/storm <topic> [as <role>]`** — the explicit driver. Runs all four phases and
  **saves the briefing to `research/<slug>.md`**, then shows you the summary,
  ranked findings, action, and grade. The role tailors the actionable insight:
  `/storm the creator economy in 2026 as a YouTube channel owner`.
- **`storm-researcher` agent** — runs the whole method in an isolated context and
  writes the file. Use it to keep your main thread clean or to research several
  topics in parallel.
- **`/research-feature <decision> [as <role>]`** — **repo-grounded** STORM, the
  bridge to the `/ship` pipeline. Runs the four phases grounded in *your* codebase
  (`REPO_CONTRACT.md` + a scoped scan + the knowledge graph), so the recommendation
  names the real files and patterns to reuse and honors your dependency policy —
  not a textbook verdict. It saves to `research/<slug>.md`, and the next `/ship` run
  picks it up: the Planner reads the briefing and grounds the spec in it. Use it for
  a feature that hinges on an external/domain choice the codebase can't settle (a
  security scheme, an OAuth flow, an algorithm, a third-party service, a compliance
  rule). It's an opt-in *precursor* to `/ship`, not a pipeline stage — and if the
  Planner hits such a decision with no briefing present, it will recommend running
  this first. `/research-feature the rate-limiting approach for the login endpoint`

When installed as a plugin the commands are namespaced `/storm-research:storm` and
`/storm-research:research-feature`.

### Install

Same marketplace as the pipeline — if you already added it, just install the
second plugin:

```bash
/plugin marketplace add at3gk/agentpipeline
/plugin install storm-research@agent-pipeline-marketplace
/reload-plugins
```

Try it locally without installing: `claude --plugin-dir ./plugins/storm-research`.

**For Claude Code on the web (cloud), the plugin install above does nothing** — the
interactive plugin manager isn't available there and a fresh container doesn't carry
your local install (see the [cloud note](#running-it-in-the-cloud-no-computer-left-on)).
Instead **vendor the files into the repo** so they ride along in the clone and
auto-load with no install step:

```bash
/path/to/AgentPipeline/install.sh ~/code/your-repo
```

That copies the skill to `.claude/skills/storm-research/`, the command to
`.claude/commands/storm.md`, and the agent to `.claude/agents/storm-researcher.md`.
The `storm` command and `storm-researcher` agent read the prompts from
`${CLAUDE_PLUGIN_ROOT}/skills/storm-research/reference.md` when installed as a plugin
and from `.claude/skills/storm-research/reference.md` when vendored, so the same
files work both ways. Commit `.claude/`, push, and `/storm` is live in every cloud
session of that repo.

> `research/<slug>.md` is a normal committed file, which is what carries the
> briefing out of an ephemeral cloud session — commit and push it to keep it.

## Repository layout

```
.claude-plugin/marketplace.json     # marketplace catalog (both plugins)
plugins/agent-pipeline/
  .claude-plugin/plugin.json        # plugin manifest (version lives here)
  agents/                           # cartographer, planner, coder, tester, reviewer, explainer, scout
  commands/                         # map-repo, ship, ship-overnight, suggest-features, explain
plugins/storm-research/
  .claude-plugin/plugin.json        # plugin manifest
  skills/storm-research/
    SKILL.md                        # auto-invokable method (runs inline)
    reference.md                    # the four verbatim STORM prompts (source of truth)
  commands/                         # storm, research-feature  (save research/<slug>.md)
  agents/                           # storm-researcher (isolated full-method run)
examples/
  FEATURES.md                       # starter backlog (copy to your repo root)
  REPO_CONTRACT.md                  # filled-in repo-contract template (generate yours with /map-repo)
  claude-settings.json              # SessionStart hook for cloud runs
install.sh                          # vendor the files into any repo (option B)
```
