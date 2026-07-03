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

## The pipelines

`agent-pipeline` is a **suite of composable pipelines** mapped to the development
lifecycle. The feature pipeline (`/ship`) is the spine; the rest are standalone
commands you run on their own *or* chain around `/ship`. Each follows the same
recipe — a command delegates to a specialist subagent that reads a bundled skill
— and each enforces *evidence*, not vibes: a parseable verdict, a measured
number, a guard test, green tests.

| Phase | Command | What it does | Output |
|------|---------|--------------|--------|
| **Define** | `/clarify <idea>` | Interviews you one question at a time to a build-ready brief | `.pipeline/brief.md` → feeds `/ship` |
| **Build** | `/ship <feature>` | The full Map→Plan→Code→Test→Review→Explain feature pipeline | reviewed, tested branch |
| | `/ship-overnight` | The same, autonomous: branch, auto-fix loop, pushed morning report | pushed `claude/overnight-*` branch |
| **Verify** | `/debug <symptom>` | Reproduce→localize→reduce→fix→guard; minimal fix + a regression test | `.pipeline/debug-report.md` + guard test |
| | `/grade-tests` | Mutation testing — does your suite *assert*, not just run? | `reports/mutation/REPORT.md` |
| **Review** | `/security-review` | Read-only OWASP gate over the branch diff | `reports/security/REPORT.md` (`VERDICT:`) |
| | `/code-simplify` | Behaviour-preserving cleanup (Chesterton's Fence) | `.pipeline/simplification.md` |
| | `/perf` | Measure-first optimization — no number, no change | `reports/perf/REPORT.md` |
| **Groom** | `/suggest-features` | Proposes small, evidence-backed backlog candidates | `needs-triage` GitHub issues, or `FEATURES.md` (`## Proposed`) |
| **Learn** | `/explain <target>` | Read-only teaching walkthrough of any file/module/feature | `.pipeline/explanation.md` |

A natural chain: `/clarify` an idea → `/ship` it → `/security-review` the
result → `/code-simplify` and `/perf` the hot paths. Each is independent, so use
only the ones a given change needs. The feature pipeline is documented first
below; the standalone pipelines follow under [Commands](#commands), and the
research plugin last.

### Token economy (adapted from Headroom)

A multi-stage pipeline re-reads a lot of shared context, so the agents follow a
cross-cutting **`context-economy`** skill that spends fewer tokens *without*
losing answers. The ideas are adapted from
[Headroom](https://github.com/headroomlabs-ai/headroom)'s token-reduction work,
but **not its runtime** — we deliberately kept the discipline at the *authoring*
layer (how handoffs are written and ordered), not a proxy that rewrites traffic:

- **Output economy** — lead with the verdict/answer, cut preamble, and point at
  code by `file:line` instead of re-printing diffs the reader already has.
- **Cache-friendly ordering** — stable instructions first, run-specific content
  last, so prompt-cache prefixes survive across stages.
- **Lossless evidence** — handoffs are compressed *views* (summary + pointers);
  the real diff/output a later gate must verify is never paraphrased away.

This matters because it's **cloud-safe and correctness-safe**: Headroom's proxy
can't run in the managed cloud container and compresses lossily, whereas an
authoring discipline works everywhere `.claude/` is committed and never touches
the evidence the Reviewer reads. (Headroom's own design agrees — it refuses to
compress `tool_result`, "the cache hot zone.") It's a discipline, not a command —
there's nothing to invoke.

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
  Accepts a GitHub issue reference (`#123` or an issue URL) as the request — it
  builds from the full issue thread but leaves the issue open for you to close
  after reviewing the branch.
- **`/ship-overnight <feature request>`** — the autonomous pipeline. Creates its
  own branch, runs end to end without stopping, and includes a **bounded auto-fix
  loop**: if the Reviewer says NEEDS WORK or BLOCK, it feeds the feedback back to
  the Coder and retries (up to 2 rounds). If it still can't ship, the Explainer
  writes up exactly *why it's stuck* and the smallest next step. Either way it
  pushes the branch and leaves a committed morning report — **no PR, no merge**.
  Point it at a GitHub issue (`#123` or an issue URL) and it builds from the full
  issue thread, comments the branch name back, and closes the issue on ship.
  With no argument it pulls the next backlog item: in a repo that declares GitHub
  Issues as its tracker (a `docs/agents/issue-tracker.md` file at the repo root),
  that's the oldest open, unassigned `ready-for-agent` issue — claimed by
  assignment, closed on ship, unassigned and left open when blocked; otherwise
  it's the next unchecked item from the `## Ready to build` section of a
  `FEATURES.md` backlog.
- **`/suggest-features [focus]`** — have Opus (the **scout** agent) review the
  codebase and its knowledge graph and propose small, evidence-backed candidates
  into the backlog: `needs-triage` GitHub issues when the repo declares the
  tracker, otherwise the `## Proposed` section of `FEATURES.md`. It only
  proposes — you promote the ones you want by labeling them `ready-for-agent`
  (or moving them into `## Ready to build`). Great as a grooming pass before a
  night of `/ship-overnight` runs.
- **`/explain <file | module | feature>`** — run just the Explainer on demand to
  learn any part of the codebase. With no argument, it explains your most recent
  changes.
- **`/clarify <rough idea>`** — the **Define** stage. Have the **clarifier** agent
  interview you **one question at a time** — each the highest-value unknown left,
  with a sensible default — until it can describe the work at ~95% confidence,
  then write a build-ready brief (objective, scope, non-goals, constraints,
  acceptance criteria) to `.pipeline/brief.md`. The Planner reads it on the next
  `/ship`, so a vague request becomes a tight spec. Read-only with respect to
  source code.
- **`/debug <error | failing test | symptom>`** — have the **debugger** agent work
  a disciplined **reproduce → localize → reduce → fix → guard** loop: get a
  deterministic reproduction, bisect to the *root cause* (not the first line that
  throws), apply the **minimal** fix, and add a regression test that **fails
  before and passes after**. Writes `.pipeline/debug-report.md`. It fixes the
  cause, not the symptom — and escalates instead of forcing a patch when the cause
  is a design problem.
- **`/security-review [scope | "full"]`** — have the **security-auditor** agent run
  a **read-only** OWASP-lens audit (broken access control, injection, secrets,
  SSRF, deserialization, crypto). Defaults to the branch diff vs `main`. Writes
  `reports/security/REPORT.md` whose **first line is a machine-readable**
  `VERDICT: PASS / FINDINGS / BLOCK`, with each finding's `file:line`, severity
  (rated by impact), and concrete fix. A gate, not a fixer — run it before merge
  on security-sensitive features.
- **`/code-simplify [scope] [improve]`** — have the **simplifier** agent reduce
  complexity **without changing behaviour**: dead code, duplication, needless
  indirection, over-abstraction, tangled control flow. It obeys **Chesterton's
  Fence** (explain why a construct exists before touching it) and proves
  behaviour is preserved by keeping the **same tests green**. Proposes by default
  (`.pipeline/simplification.md`); `improve` applies the safe subset.
- **`/perf [scope] [improve]`** — have the **perf-auditor** agent optimize
  **measure-first**: profile to find the real bottleneck, diagnose why it's hot
  (algorithmic, N+1 queries, repeated work, I/O), and report (or, with `improve`,
  apply) only changes backed by a **measured before/after**. Writes
  `reports/perf/REPORT.md`. Its rule is *no number, no change* — it refuses to
  optimize on a guess.
- **`/grade-tests [focus | "improve" | "diff"]`** — have the **mutation-grader**
  agent score how well your suite actually *asserts* behaviour, not just runs it.
  It scopes mutation testing (cosmic-ray) to a small allowlist of pure-logic
  modules, then reports the mutation score and turns each *surviving mutant* into
  a precise missing-assertion TODO (`file:line` + the operator no test caught).
  Pass `improve` to have it strengthen the tests, or `diff` to gate only a PR's
  changed lines. See [Grading your tests](#grading-your-tests-mutation-testing).

```
/map-repo
/clarify add a way for users to export their reports
/ship add rate limiting to the login endpoint, max 5 attempts/min/IP, return 429
/ship-overnight build a CSV export endpoint for the reports table
/debug test_login_lockout fails intermittently with a 500
/security-review                       # gate the current branch before merge
/code-simplify src/reports/ improve
/perf the /reports/export endpoint
/suggest-features focus on test-coverage gaps in the auth module
/explain src/auth/session.py
/grade-tests focus on the scoring modules, then improve
```

When installed as a plugin the commands are namespaced: `/agent-pipeline:map-repo`,
`/agent-pipeline:clarify`, `/agent-pipeline:ship`, `/agent-pipeline:ship-overnight`,
`/agent-pipeline:debug`, `/agent-pipeline:security-review`,
`/agent-pipeline:code-simplify`, `/agent-pipeline:perf`,
`/agent-pipeline:suggest-features`, `/agent-pipeline:explain`,
`/agent-pipeline:grade-tests`.

## Grading your tests (mutation testing)

The Tester proves your tests **pass**. `/grade-tests` proves they actually
**assert** — it grades the suite itself.

Line coverage only tells you a line *ran*; a suite can hit 100% coverage while
asserting almost nothing. **Mutation testing** closes that gap empirically: it
injects small faults into your code (`<`→`<=`, `and`→`or`, `True`→`False`,
deleting a statement), reruns the tests, and asks *"did any test fail?"*. A
mutant your tests catch is **killed**; one they miss is a **survivor** — a
precise pointer to a missing assertion. The **mutation score** is
`killed / (killed + survived)`.

It's powerful but expensive (10–100× a normal run) and noisy (an undecidable
~4–39% of mutants are *equivalent* — impossible to kill). So the
**mutation-grader** agent and its bundled `mutation-grading` skill apply the
discipline that makes it usable:

- **Scope tightly** to a hand-picked allowlist of 3–8 pure, deterministic,
  dependency-light modules — never the whole repo. (A repo that already isolates
  "pure-logic" modules for fast tests has done most of this work.)
- **Point each module at its covering tests** so runs stay fast and correct.
- **Ratchet a baseline** of accepted/equivalent survivors and fail only on
  *new* ones; target **75–85%**, never chase 100%.
- **Diff-gate PRs, trend nightly** — `grade-tests diff` mutates only changed
  lines; nightly runs append the score to a trend file.

Output is `reports/mutation/REPORT.md`: the scoped score plus, for every
survivor, its `file:line`, the function, the mutated operator, and the assertion
to add. The engine is **cosmic-ray** (it runs your real `pytest` command in
place, so it works with conventional `src/`-layout repos that import
`from src.x import y` — where mutmut 3.x's trampoline does not). Full strategy,
the sourced research, and the portable `grade_tests.py` driver live in
`plugins/agent-pipeline/skills/mutation-grading/`.

```
/grade-tests                       # scope, run, report the scoped mutation score
/grade-tests improve               # then strengthen tests until no new survivors
/grade-tests diff                  # PR gate: only the lines this branch changed
```

`reports/mutation/baseline.json` is meant to be **committed** (it's the ratchet);
`.mutation/` and the score trend are gitignored.

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
3. Set up the backlog. If the repo tracks work in **GitHub Issues** (it has a
   `docs/agents/issue-tracker.md`), just label the approved issues
   `ready-for-agent`. Otherwise copy [`examples/FEATURES.md`](examples/FEATURES.md)
   to your repo root and fill in the `## Ready to build` section. (Either way,
   `/suggest-features` can propose candidates for you to promote.)
4. At [claude.ai/code/routines](https://claude.ai/code/routines), create a Routine
   on a **Schedule** trigger (e.g. daily at 2am) with the prompt `/ship-overnight`
   (no argument). Each night it grabs the next backlog item — the oldest open,
   unassigned `ready-for-agent` issue, or the next unchecked `## Ready to build`
   item — ships it to a `claude/overnight-*` branch, closes it out (closes the
   issue / checks the box), and pushes — ready for your review with coffee.
   (Routines can also be triggered by GitHub events or an API call.)

**Optional: let it refill its own backlog.** Add a second Routine on a slower
schedule (say, weekly) running `/suggest-features`. It proposes candidates —
`needs-triage` issues, or items under `## Proposed` — it never ships them — so
you skim the list and promote what you want. This keeps "decide what to build"
a human-gated step while the nightly shipper handles "build it."

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
  agents/                           # cartographer, planner, coder, tester, reviewer, explainer, scout,
                                    #   mutation-grader, clarifier, debugger, security-auditor, simplifier, perf-auditor
  commands/                         # map-repo, ship, ship-overnight, suggest-features, explain, grade-tests,
                                    #   clarify, debug, security-review, code-simplify, perf
  skills/                           # each standalone pipeline's process lives in a bundled skill
    mutation-grading/               # SKILL.md + reference.md + grade_tests.py (portable cosmic-ray driver)
    spec-driven/                    # /clarify — one-question discovery + brief template + definition of done
    debugging/                      # /debug — reproduce->localize->reduce->fix->guard + symptom-vs-cause catalogue
    security-review/                # /security-review — OWASP checklist + severity rubric
    code-simplification/            # /code-simplify — Chesterton's Fence + behaviour-preservation discipline
    performance/                    # /perf — measure-first method + optimization catalogue
    context-economy/                # cross-cutting — terse, cache-friendly, lossless-evidence handoffs (adapted from Headroom)
    #   every skill ends with anti-rationalizations / red-flags / verification-gates (process, not prose)
plugins/storm-research/
  .claude-plugin/plugin.json        # plugin manifest
  skills/storm-research/
    SKILL.md                        # auto-invokable method (runs inline)
    reference.md                    # the four verbatim STORM prompts (source of truth)
  commands/                         # storm, research-feature  (save research/<slug>.md)
  agents/                           # storm-researcher (isolated full-method run)
examples/
  FEATURES.md                       # starter backlog (copy to your repo root — fallback for repos not using GitHub Issues)
  REPO_CONTRACT.md                  # filled-in repo-contract template (generate yours with /map-repo)
  claude-settings.json              # SessionStart hook for cloud runs
install.sh                          # vendor the files into any repo (option B)
```
