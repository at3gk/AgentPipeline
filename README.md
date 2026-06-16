# AgentPipeline

A reusable multi-agent development pipeline for [Claude Code](https://code.claude.com).

You type one command and a chain of specialist subagents takes a feature from
request to reviewed, tested, and explained code — each one staying in a clean,
narrow context and handing off to the next through a shared `.pipeline/` folder.

## The agents

| Stage | Agent | Model | Role |
|------|-------|-------|------|
| 1 | **planner** | opus | Turns your request into a tight spec at `.pipeline/spec.md`. Never writes code. |
| 2 | **coder** | sonnet | Implements the spec exactly. Summarizes to `.pipeline/changes.md`. |
| 3 | **tester** | sonnet | Writes and runs tests. Reports to `.pipeline/test-results.md`. Never fixes the code. |
| 4 | **reviewer** | opus | Read-only final gate. Verdict (SHIP / NEEDS WORK / BLOCK) to `.pipeline/review.md`. |
| 5 | **explainer** | opus | Read-only teaching pass. Walks you through what was built and why, in `.pipeline/explanation.md`. |

The split keeps each agent focused, and the read-only Reviewer and Explainer
can't paper over problems — they can only judge and teach.

About 70% of token spend lands on the cheaper Sonnet model (Coder + Tester),
30% on Opus (Planner, Reviewer, Explainer), which run once per feature where
reasoning quality matters most.

## Commands

- `/ship <feature request>` — run the full pipeline. Cleans `.pipeline/`,
  then Planner → Coder → Tester → Reviewer → Explainer, stopping to show you
  open questions or test failures. Never merges; leaves the branch for you.
- `/explain <file | module | feature>` — run just the Explainer on demand to
  learn any part of the codebase. With no argument, it explains your most
  recent changes.

```
/ship add rate limiting to the login endpoint, max 5 attempts per minute per IP, return 429 after limit
/explain src/auth/session.py
```

## Install — option A: as a plugin (recommended, reusable everywhere)

This repo is also a Claude Code plugin marketplace. Install once and the
agents and commands are available in every repo, with automatic updates.

```bash
# From GitHub
/plugin marketplace add at3gk/agentpipeline
/plugin install agent-pipeline@agent-pipeline-marketplace
```

To develop or try it locally without installing:

```bash
claude --plugin-dir ./plugins/agent-pipeline
```

When installed as a plugin, the commands are namespaced:
`/agent-pipeline:ship` and `/agent-pipeline:explain`.

## Install — option B: vendor the files into a repo

If you'd rather copy the agents and commands straight into a project (no
plugin system), run the install script from this repo:

```bash
# Install into the current directory
/path/to/AgentPipeline/install.sh

# Or into a specific repo
/path/to/AgentPipeline/install.sh ~/code/my-project
```

It copies the agents into `<repo>/.claude/agents/`, the commands into
`<repo>/.claude/commands/`, and adds `.pipeline/` to the repo's `.gitignore`.
Commands are then `/ship` and `/explain` (no namespace).

## Using it overnight

1. Create a branch for the feature.
2. Run `/ship <your request>`.
3. In the morning, read `.pipeline/review.md` for the verdict and
   `.pipeline/explanation.md` to learn what was built. If it says SHIP and the
   code looks right, merge. If NEEDS WORK, read the specific feedback.

The pipeline never merges. You are the final gate.

## Tips

- **Be specific.** "Add rate limiting, max 5/min per IP, return 429" beats
  "add rate limiting somewhere." A tighter request makes a tighter spec.
- **Start small.** Bounded features (an endpoint, a settings page, one module)
  first; scale up once you trust it.
- **Read the `.pipeline/` files.** Even on SHIP, reading spec / changes /
  test-results / review / explanation teaches you how each agent thinks and
  helps you write better requests.
- **Parallel features** want separate git worktrees so agents don't edit the
  same files.

## Repository layout

```
.claude-plugin/marketplace.json     # marketplace catalog
plugins/agent-pipeline/
  .claude-plugin/plugin.json        # plugin manifest
  agents/                           # planner, coder, tester, reviewer, explainer
  commands/                         # ship, explain
install.sh                          # vendor the files into any repo (option B)
```
