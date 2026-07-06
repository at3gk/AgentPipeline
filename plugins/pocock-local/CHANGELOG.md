# Changelog

## 0.1.0

Initial release — a lean, CI-trusting companion to the Matt Pocock skills in
LOCAL-FILES mode.

- **Read-only assigned-issue sync** (`skills/issue-sync/sync_assigned_issues.py`,
  stdlib-only Python): mirrors `gh issue list --assignee @me` into
  `<dir>/<number>/` as a machine-owned `snapshot.md` (refreshed each run) plus a
  human-owned `notes.md` (created once, never overwritten). Config resolves from
  `POCOCK_ISSUE_REPO`/`POCOCK_ISSUE_DIR`, then `docs/agents/issue-tracker.md`,
  then a flagged fallback — the repo is never guessed. Worktree-safe: a relative
  mirror is anchored at the main worktree root so linked worktrees share one
  mirror. Never writes to GitHub (write-back is an off-by-default TODO).
- **`/pocock-local:setup-local`** — attended bootstrap: install the Pocock skills
  in local-files mode, verify `gh`, configure and wire the sync via a SessionStart
  hook. Flags the enterprise `allowManagedHooksOnly` and unsandboxed-hook risks
  rather than working around them.
- **`/pocock-local:sync-issues`** — manual trigger for the same sync.
- **`/pocock-local:ship-local`** — a lean **TDD** flow: pick an assigned issue,
  scope it with Pocock `grilling` (the synced issue may be thin), plan, have the
  **tester** design failing tests (red), implement to green via Pocock
  `implement`, the tester confirms, then open a PR. CI is the regression gate;
  the issue closes when the PR merges. Respects your own worktree/branch/PR
  naming — imposes none.
- **`tdd-tester` agent** — two modes, DESIGN (red) and CONFIRM (green); never
  writes production code, never weakens a test to pass. (Named distinctly from
  agent-pipeline's `tester` so vendoring both into one repo doesn't collide.)
- **Fable routing** (`MODEL-TIERS.md`) — when `claude-fable-5` is available the
  orchestrator routes each stage to the model it needs (guidance, not a mandate);
  otherwise frontmatter defaults. Escape hatch `POCOCK_FABLE=0`.

The existing `agent-pipeline` and `storm-research` plugins are unaffected.
