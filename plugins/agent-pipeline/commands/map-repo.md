---
description: Build or refresh REPO_CONTRACT.md — a short curated index of the codebase's canonical files and patterns (schemas, validators, utils, naming, errors, auth, tests, package policy) that the Planner and Coder read every run.
---

Map the repo into a contract: $ARGUMENTS

Delegate to the **cartographer** subagent. Ask it to explore the codebase — using `.understand-anything/knowledge-graph.json` if present, otherwise exploring directly — and write or refresh `REPO_CONTRACT.md` at the repo root: a short, indexed catalogue of the canonical file (and example symbol) for each area — schemas, validators, shared utils, naming conventions, error patterns, auth patterns, tests/factories, and the package policy.

If `$ARGUMENTS` is non-empty, treat it as a focus or constraint (e.g. "just the API layer" or "we don't use an ORM, skip data models") and pass it to the cartographer.

The cartographer is read-only with respect to source code — the only file it may write is `REPO_CONTRACT.md`. When it finishes, show me a short summary of what it indexed and remind me that `REPO_CONTRACT.md` is meant to be **committed** so it travels with the repo (the Planner reads it on every `/ship` run). Re-run this whenever the codebase drifts enough that the contract goes stale.
