# Changelog

## 1.7.0

- **GitHub-issues-first backlog** (Matt Pocock skills convention). When a repo
  declares GitHub Issues as its tracker (`docs/agents/issue-tracker.md` at the
  repo root, labels in `docs/agents/triage-labels.md`), backlog operations go
  through `gh`:
  - `/ship` accepts an issue reference (`#123`, a bare number, or an URL) and
    builds from the full issue thread; the human closes the issue (attended flow).
  - `/ship-overnight` with no argument pulls the oldest open, unassigned
    `ready-for-agent` issue (skipping assigned or `Blocked by: #n`-blocked ones),
    claims it by assignment, comments + closes on ship, and unassigns + leaves it
    open when blocked. It never pulls `needs-triage`/`needs-info` issues.
  - `/suggest-features` (the scout) files proposals as `needs-triage` issues,
    dedupes against open and recently closed issues, and never applies
    `ready-for-agent` — promotion stays a human act.
  - Repos without the tracker file keep the exact existing `FEATURES.md`
    behavior; `gh` is never required there.

## 1.6.0 and earlier

See git history.
