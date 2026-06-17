# Backlog

Features for the pipeline to build. `/ship-overnight` (run with no argument)
picks the **first unchecked item under "Ready to build"** each run, ships it to
its own branch, and checks the box.

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
