---
name: issue-sync
description: Mirror the GitHub issues assigned to you into the local Pocock tracking area as markdown, read-only. Use when you want your assigned work pulled into local files (LOCAL-FILES mode) so the Matt Pocock skills can iterate on it — typically run automatically from a SessionStart hook. Never writes to GitHub.
---

# Issue sync (assigned → local files)

A separate agent (e.g. a Slack bot) files GitHub issues and assigns them to you;
"assigned to me" is your signal to start. This skill mirrors those issues into
the local tracking area the Matt Pocock skills use in **LOCAL-FILES mode**, so
`grilling`, `to-prd`, `implement`, etc. have local markdown to work on.

It is **read-only toward GitHub.** The only `gh` call is `gh issue list` (plus
`gh auth status` preflight). It never comments, labels, closes, or touches a
Project board.

This skill bundles `sync_assigned_issues.py`, a stdlib-only Python 3 driver.

## Run it

```
python <skill>/sync_assigned_issues.py            # sync now
python <skill>/sync_assigned_issues.py --dry-run  # resolve + fetch, write nothing
python <skill>/sync_assigned_issues.py --repo ORG/REPO --dir path/to/mirror
```

Normally you don't run it by hand — a **SessionStart hook** runs it each session
and its stdout ("N new issue(s) pulled …") lands in your context as a "here's
what's new" note. See `examples/claude-settings.json` and `/pocock-local:setup-local`.

## Configuration (no hardcoded values)

Resolved in this order, so the plugin adapts to whatever your Pocock setup declared:

1. **CLI flags** `--repo` / `--dir`.
2. **Env** `POCOCK_ISSUE_REPO` (`ORG/REPO`, or `HOST/ORG/REPO` for Enterprise) and
   `POCOCK_ISSUE_DIR` (the local tracking dir).
3. **`docs/agents/issue-tracker.md`** — best-effort parse of the Pocock LOCAL-FILES
   config for the repo slug and local path.
4. **Fallback:** the repo is never guessed — if unresolved, it exits non-
   destructively telling you to set `POCOCK_ISSUE_REPO`. The dir falls back to
   `.scratch/issues` and prints a one-line flag saying it guessed.

## What it writes — snapshot + notes split

Per issue, under `<dir>/<number>/`:

- **`snapshot.md`** — machine-owned. The pulled title/body/labels/url,
  **overwritten every run** so the mirror tracks upstream edits.
- **`notes.md`** — human-owned working scratch (scope from `grilling`, plan,
  decisions). **Created once and never overwritten** — your in-progress notes are
  never clobbered, even as the snapshot refreshes.

## Git worktrees

A **relative** tracking dir is anchored at the **main worktree root** (via
`git --git-common-dir`), so every linked `git worktree` shares **one** mirror and
one set of notes rather than fragmenting a copy into each worktree. Pass an
**absolute** `--dir` / `POCOCK_ISSUE_DIR` to pin an explicit shared location. The
tool creates no branches or PRs, so it never collides with your own branch/PR
naming.

## Enterprise notes (flagged, not worked around)

- Assumes `gh` is already authenticated against your enterprise host. If
  `gh issue list` can't resolve the repo, it prints a `GH_HOST` /
  host-qualified-repo hint and stops — it does not guess a host.
- The SessionStart hook that runs this is subject to two enterprise realities,
  surfaced by `/pocock-local:setup-local`: `allowManagedHooksOnly` may block a
  personal hook, and hooks run **unsandboxed** with your full permissions.

## Not included (opt-in later)

- **Write-back** (push local notes to the issue as a comment) is intentionally
  absent — a clearly-marked, off-by-default TODO in the script. Read-only is the
  default posture.
- **Column-gating** (pull only issues whose Project status is "ready") is not
  built — board status isn't a gate today. It would need
  `gh auth refresh -s project` and `gh project item-list <n> --owner <org> --format json`
  matched to assigned issues by number.
- **`examples/issue-sync.launchd.plist`** keeps the mirror warm on a timer even
  when Claude Code is closed — opt-in.
