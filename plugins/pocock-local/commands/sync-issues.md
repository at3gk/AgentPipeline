---
description: Pull the GitHub issues assigned to you into the local Pocock tracking area (read-only). A manual trigger for the same sync the SessionStart hook runs automatically.
---

Sync my assigned issues into the local mirror: $ARGUMENTS

Run the bundled issue-sync driver (read-only toward GitHub — it only lists
issues, never writes):

```
python ${CLAUDE_PLUGIN_ROOT}/skills/issue-sync/sync_assigned_issues.py
```

(When vendored via `install.sh` rather than installed as a plugin, the path is
`.claude/skills/issue-sync/sync_assigned_issues.py`.)

- Pass `$ARGUMENTS` through to the script if the user gave flags (e.g. `--repo`,
  `--dir`, `--dry-run`).
- The script resolves the repo and local dir from `POCOCK_ISSUE_REPO` /
  `POCOCK_ISSUE_DIR`, else `docs/agents/issue-tracker.md`, else it flags what to
  set — it never guesses the repo. Relay any `issue-sync:` advisory it prints.
- Report its stdout to the user: which issues were newly pulled and which
  snapshots were refreshed. Each issue lands under `<mirror>/<number>/` as a
  machine-owned `snapshot.md` (refreshed each run) plus a human-owned `notes.md`
  (created once, never overwritten).

This is the same sync that runs on session start; use it for a mid-session
refresh after the Slack agent assigns you something new. Normally you don't need
it — the hook keeps the mirror current. To set up the hook and configuration, run
`/pocock-local:setup-local`.
