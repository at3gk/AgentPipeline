---
description: Groom the backlog. Reviews the codebase (and its knowledge graph) and proposes small, evidence-backed feature candidates — as needs-triage GitHub issues when the repo declares an issue tracker, otherwise into FEATURES.md under "Proposed".
---

Groom the feature backlog: $ARGUMENTS

**Model tier (automatic — no setup).** The scout auto-uses `claude-fable-5` when Fable is available (the most capable model proposes less-generic, better-scoped candidates). Delegate with `model: claude-fable-5`; if that spawn **fails because Fable is unavailable or refused**, re-run it on its default Opus. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces Opus.) See `MODEL-TIERS.md`.

Delegate to the **scout** subagent. Ask it to review the codebase — using `.understand-anything/knowledge-graph.json` if present, otherwise exploring directly — and file a handful of small, evidence-backed candidate features into the backlog. Tell it which backlog the repo uses:

- If `docs/agents/issue-tracker.md` exists at the repo root, the repo tracks its backlog in **GitHub Issues** — the scout files each proposal as a `needs-triage` issue via `gh issue create`.
- Otherwise, it appends proposals to **`FEATURES.md`** under the `## Proposed` heading, as before. Never require `gh` in repos that don't declare the tracker — but when the tracker file is missing, print one line pointing at the bootstrap ("run `/agent-pipeline:setup-pipeline` to set up the GitHub-issues backlog") rather than degrading silently.

If `$ARGUMENTS` is non-empty, treat it as a focus area or constraint (e.g. "focus on the auth module" or "only test-coverage gaps") and pass it to the scout.

**Milestones (only when `docs/agents/issue-tracker.md` defines a "Milestones" section).** Issues created as part of a defined effort are assigned to that effort's milestone **at creation** (`gh issue create --milestone "<name>"`). If the focus names an effort whose milestone doesn't exist yet, create it first — `gh api repos/<owner>/<repo>/milestones -f title="<name>"`, since `gh` has no native milestone-create subcommand — then pass the milestone name to the scout. The scout itself never creates milestones and only assigns one when the focus names an existing milestone; and priority labels (`P1`–`P3`) are never applied at proposal time — they're assigned at promotion.

The scout only **proposes** — it must not write code, must not touch the `## Ready to build` section, and must never apply the `ready-for-agent` label. After it finishes, show me its proposals and the one it would pick first, so I can promote the ones I want — into "Ready to build", or by labeling the issue `ready-for-agent` — for `/ship-overnight`.
