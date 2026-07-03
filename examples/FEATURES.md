# Backlog

Features for the pipeline to build. `/ship-overnight` (run with no argument)
picks the **first unchecked item under "Ready to build"** each run, ships it to
its own branch, and checks the box.

> This file is the **fallback backlog** for repos without issue tracking. If
> your repo declares GitHub Issues as its tracker (a `docs/agents/issue-tracker.md`
> at the repo root), you don't need this file — the pipeline pulls open
> `ready-for-agent` issues instead, and `/suggest-features` files `needs-triage`
> issues.

Keep items **small, specific, and testable** — the same qualities that make a
good `/ship` request. One bounded feature per line.

## Ready to build

<!-- The autonomous nightly run pulls from here, top to bottom. -->
- [ ] Add a `/health` endpoint that returns `{ "status": "ok" }` and a 200
- [ ] Validate that the `email` field is a well-formed address, return 422 otherwise

## Proposed (review, then move up to "Ready to build")

<!--
Candidates suggested by `/suggest-features` land here with a rationale.
They are NOT auto-shipped — promote the ones you want into "Ready to build".
-->

## Done

<!-- Optional: move shipped items here, or just rely on git history. -->
