# AgentPipeline

A reusable multi-agent development pipeline for [Claude Code](https://code.claude.com).

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

## Commands

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
/ship add rate limiting to the login endpoint, max 5 attempts/min/IP, return 429
/ship-overnight build a CSV export endpoint for the reports table
/suggest-features focus on test-coverage gaps in the auth module
/explain src/auth/session.py
```

When installed as a plugin the commands are namespaced: `/agent-pipeline:ship`,
`/agent-pipeline:ship-overnight`, `/agent-pipeline:suggest-features`,
`/agent-pipeline:explain`.

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
closed — and results come back as a pushed branch. Because everything the
pipeline needs (agents, commands) lives in this committed plugin, it loads in
cloud sessions exactly as it does locally.

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
> not carry to the cloud; this plugin works because it's installed from the marketplace.

## Install — option B: vendor the files into a repo

If you'd rather copy the agents and commands straight into a project (no plugin
system), run the install script from this repo:

```bash
/path/to/AgentPipeline/install.sh            # into the current directory
/path/to/AgentPipeline/install.sh ~/code/app # or a specific repo
```

It copies the agents into `<repo>/.claude/agents/`, the commands into
`<repo>/.claude/commands/`, and adds `.pipeline/` to the repo's `.gitignore`.
Commands are then `/ship`, `/ship-overnight`, `/suggest-features`, and
`/explain` (no namespace).

## Tips

- **Be specific.** "Add rate limiting, max 5/min per IP, return 429" beats "add
  rate limiting somewhere." A tighter request makes a tighter spec.
- **Start small.** Bounded features (an endpoint, a settings page, one module)
  first; scale up once you trust it.
- **Read the `.pipeline/` files.** Even on SHIP, reading spec / changes /
  test-results / review / explanation teaches you how each agent thinks.
- **Parallel features** want separate git worktrees so agents don't edit the same
  files.

## Repository layout

```
.claude-plugin/marketplace.json     # marketplace catalog
plugins/agent-pipeline/
  .claude-plugin/plugin.json        # plugin manifest (version lives here)
  agents/                           # planner, coder, tester, reviewer, explainer, scout
  commands/                         # ship, ship-overnight, suggest-features, explain
examples/
  FEATURES.md                       # starter backlog (copy to your repo root)
  claude-settings.json              # SessionStart hook for cloud runs
install.sh                          # vendor the files into any repo (option B)
```
