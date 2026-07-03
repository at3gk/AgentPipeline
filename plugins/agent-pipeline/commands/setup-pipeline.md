---
description: One-time attended bootstrap - install the Matt Pocock engineering skills, verify the gh CLI, and generate the docs/agents/* conventions that make the pipeline GitHub-issues-first and domain-docs-aware.
---

Bootstrap this machine and repo for the pipeline's GitHub-issues-first backlog: $ARGUMENTS

This is an **attended, one-time setup** — it may install software and log into GitHub, so it must never run from an unattended session (`/ship-overnight` is explicitly forbidden from doing any of this mid-run). Show me each command before you run it, and stop on anything unexpected.

Work through these steps in order, skipping any that are already satisfied:

## 1. Check whether the Matt Pocock skills are installed

The suite ([github.com/mattpocock/skills](https://github.com/mattpocock/skills)) keeps its skill store in `~/.agents/skills/` with per-skill symlinks in `~/.claude/skills/`. Check for these skills specifically: `grilling`, `to-prd`, `to-issues`, `implement`, `triage`, `code-review`, `domain-modeling`, and `setup-matt-pocock-skills`.

- All present → report that and skip to step 3.
- Some or all missing → step 2.

## 2. Install them (following the upstream README, not memory)

Fetch the README of `github.com/mattpocock/skills` **at run time** and follow **its** documented install method — do not rely on a memorized or hardcoded procedure, since the suite's install flow may have changed. (Expect it to be roughly: clone the repo into the skills store, then symlink each skill into `~/.claude/skills/` — but the README is the source of truth.) Show me the commands before running them, and afterwards verify the skill directories/symlinks listed in step 1 actually exist.

## 3. Verify the gh CLI

Run `gh auth status`.

- Authenticated → continue.
- `gh` not installed → guide me through installing it for this platform (`winget install GitHub.cli` on Windows, `brew install gh` on macOS, the distro package on Linux), then continue below.
- Installed but not authenticated → walk me through `gh auth login --web`.

Re-run `gh auth status` to confirm before moving on.

## 4. Generate the repo conventions

Have me run **`/setup-matt-pocock-skills`** in the target repo — it writes the three convention files the pipeline gates on:

- `docs/agents/issue-tracker.md` — declares GitHub Issues as the tracker and the `gh` CLI conventions.
- `docs/agents/triage-labels.md` — the five triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- `docs/agents/domain.md` — declares `CONTEXT.md` as the domain glossary and `docs/adr/` as the ADR store, with the rule "flag ADR conflicts explicitly, never silently override".

Most Matt Pocock skills are `disable-model-invocation: true` (user-typed only), so **ask me to type the command** rather than invoking it yourself; only run it directly if it is genuinely model-invokable in this session.

## 5. Confirm and hand back

Verify `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `docs/agents/domain.md` exist in the repo, then summarize what was installed or already present, and finish with the one-line state of the world: the pipeline will now pull `ready-for-agent` issues in `/ship-overnight`, file `needs-triage` proposals from `/suggest-features`, and ground the Planner/Reviewer/Clarifier/Debugger in `CONTEXT.md` and `docs/adr/`.

Opting out is fine too: a repo that deliberately skips GitHub-issue tracking just doesn't get `docs/agents/issue-tracker.md`, and every pipeline command keeps its `FEATURES.md` behavior without ever requiring `gh`.
