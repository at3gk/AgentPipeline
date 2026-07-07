# pocock-local

A lean, **CI-trusting** companion plugin for teams who run the
[Matt Pocock engineering skills](https://github.com/mattpocock/skills) in
**LOCAL-FILES mode**. It does two things:

1. **Mirrors the GitHub issues assigned to you into local markdown** (read-only),
   so the Pocock skills have local files to iterate on. A separate agent (e.g. a
   Slack bot) assigns you issues; "assigned to me" is your start-work signal, and
   this keeps your local tracking area in sync.
2. **Runs a test-driven ship flow** that leans on your existing CI/CD and the
   Pocock skills instead of re-implementing heavy machinery.

It's a deliberately *simpler* sibling to `agent-pipeline`: because your repo
already has CI/CD and a test suite, this plugin drops the four-contract
enforcement, stop-rule gates, and mutation grading, and keeps a tight TDD loop.

## The flow — `/pocock-local:ship-local`

1. **Pick** an assigned issue from the local mirror.
2. **Scope** it with Pocock `grilling` (the Slack-synced issue is often thin);
   the enriched scope is captured to the issue's `notes.md`.
3. **Plan** — a short spec + acceptance criteria.
4. **Design tests first (red)** — the `tdd-tester` agent writes failing tests that
   encode the criteria.
5. **Implement (green)** — via Pocock `implement`.
6. **Confirm** — the `tdd-tester` re-runs the designed tests green; the **full suite
   + lint run in CI** on the PR.
7. **Open a PR** — using *your* branch/PR naming; CI gates it; the issue closes
   when the PR merges (human review = the close gate).

Matt Pocock skills are `disable-model-invocation: true` (user-typed only), so this
plugin **composes around them** — it prompts you to run `grilling`, `implement`,
and `/code-review`, and never calls them itself.

The agent handoffs it *does* own — the acceptance criteria passed to the
`tdd-tester`, and its red/green reports — follow a bundled **`context-economy`**
skill (adapted from [Headroom](https://github.com/headroomlabs-ai/headroom)):
lead with the result, point at `file:line` instead of re-printing code, and order
content for prompt-cache hits, while never trimming the criteria→test mapping or
the red/green evidence.

## The sync — `skills/issue-sync/`

`sync_assigned_issues.py` (stdlib-only) runs `gh issue list --assignee @me` and
writes, per issue, a machine-owned `snapshot.md` (refreshed each run) beside a
human-owned `notes.md` (created once, **never overwritten** — your notes are
safe). It's **read-only toward GitHub**.

**Config (no hardcoded values):** `POCOCK_ISSUE_REPO` / `POCOCK_ISSUE_DIR`, else
`docs/agents/issue-tracker.md`, else a flagged fallback (the repo is never
guessed). **Worktrees:** a relative mirror dir is anchored at the main worktree
root so all linked worktrees share one mirror; use an absolute dir to pin it.

It's meant to run from a **SessionStart hook** (see `examples/claude-settings.json`)
so your assigned work is mirrored the moment you open a session; run
`/pocock-local:sync-issues` for a manual refresh.

## Setup — `/pocock-local:setup-local`

Attended, one-time: installs the Pocock skills in local-files mode, verifies `gh`,
configures the sync, and wires the SessionStart hook. It **flags** two enterprise
realities rather than working around them: `allowManagedHooksOnly` may block a
personal hook, and hooks run **unsandboxed** with your full permissions.

## Install

```bash
/plugin marketplace add at3gk/agentpipeline
/plugin install pocock-local@agent-pipeline-marketplace
/reload-plugins
```

Or vendor it into a repo (files auto-load from `.claude/`, no plugin manager):

```bash
/path/to/AgentPipeline/install.sh ~/code/your-repo
```

When vendored, reference the sync script at
`.claude/skills/issue-sync/sync_assigned_issues.py` instead of
`${CLAUDE_PLUGIN_ROOT}/skills/issue-sync/...`.

## Not included (opt-in later)

- **Write-back** to issues — intentionally absent (read-only posture); a marked,
  off-by-default TODO in the script.
- **Column-gating** (pull only Project-status "ready") — board status isn't a gate
  today; would need `gh auth refresh -s project`.
- **`examples/issue-sync.launchd.plist`** — keep the mirror warm on a timer even
  when Claude Code is closed.
