---
description: One-time attended setup for the local Pocock flow — install the Matt Pocock skills in LOCAL-FILES mode, verify gh, and wire the assigned-issue sync to run on session start.
---

Set up this machine and repo for the local Pocock flow: $ARGUMENTS

An **attended, one-time setup** — it may install software and log into GitHub, so
never run it unattended. Show each command before running it, and stop on anything
unexpected.

## 1. Install the Matt Pocock skills (LOCAL-FILES mode)

The suite ([github.com/mattpocock/skills](https://github.com/mattpocock/skills))
keeps its skill store in `~/.agents/skills/` with per-skill symlinks in
`~/.claude/skills/`. Check for: `grilling`, `to-prd`, `to-issues`, `implement`,
`triage`, `code-review`, `domain-modeling`, `setup-matt-pocock-skills`.

- Missing → **fetch the upstream README at run time** and follow *its* documented
  install method (do not rely on a memorized procedure). Show the commands first;
  afterwards verify the skills/symlinks exist.
- Then run `/setup-matt-pocock-skills` in this repo and choose the **local files**
  tracker so issues live as local markdown. Most Pocock skills are
  `disable-model-invocation: true` (user-typed), so **ask the user to type it**
  rather than invoking it.

## 2. Verify `gh` (authenticated against your host)

Run `gh auth status`.
- Authenticated → continue.
- Not installed → guide the platform install (`winget install GitHub.cli` /
  `brew install gh` / distro package).
- Installed but not authed → `gh auth login --web`.

For **GitHub Enterprise**, confirm `gh` is authed against your enterprise host —
the sync uses `--repo ORG/REPO` and will surface a `GH_HOST` hint (it won't guess
a host) if the repo can't be resolved.

## 3. Configure the sync

Set the repo and local mirror location (no hardcoded values — pick one):
- Env: `POCOCK_ISSUE_REPO=ORG/REPO` (or `HOST/ORG/REPO` for Enterprise) and
  `POCOCK_ISSUE_DIR=<local tracking dir>`; **or**
- Let the script read them from the `docs/agents/issue-tracker.md` that
  `/setup-matt-pocock-skills` wrote.

Confirm with a dry run:
```
python ${CLAUDE_PLUGIN_ROOT}/skills/issue-sync/sync_assigned_issues.py --dry-run
```

Suggest gitignoring the local mirror dir (it's a personal working area). Note for
**git worktrees**: a relative mirror dir is shared across all linked worktrees
(anchored at the main worktree root); use an absolute `POCOCK_ISSUE_DIR` to pin an
explicit shared location.

## 4. Wire the SessionStart hook

Copy the sync hook from `examples/claude-settings.json` into the project's
`.claude/settings.json` (merge with any existing hooks). It runs the sync on
`startup|resume`, and its stdout ("N new issue(s) pulled…") lands in session
context as a "what's new" note.

**Flag these enterprise realities (do not work around them):**
- **`allowManagedHooksOnly`** may block a personal SessionStart hook entirely. If
  your org enforces it, the hook won't run — you'll need a managed hook or the
  manual `/pocock-local:sync-issues` / the launchd timer instead.
- Hooks run **unsandboxed with your full permissions**. This one only lists issues
  and writes local markdown, but review it before enabling — that trust applies to
  every hook.

## 5. (Optional) Keep the mirror warm off-session

`examples/issue-sync.launchd.plist` runs the sync on a timer (~10–15 min) even
when Claude Code is closed, so a freshly assigned issue is already mirrored when
you open a session. Opt-in — fill in the paths and load it per the instructions in
that file.

## 6. Confirm and hand back

Summarize what was installed/configured and finish with the state of the world:
assigned issues now mirror into your local tracking area (snapshot + notes split,
read-only), and `/pocock-local:ship-local` will scope with `grilling`, drive the
TDD red→green loop, and open a PR that CI gates.
