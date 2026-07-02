---
description: Groom the backlog. Reviews the codebase (and its knowledge graph) and proposes small, evidence-backed feature candidates into FEATURES.md under "Proposed".
---

Groom the feature backlog: $ARGUMENTS

**Model tier (automatic — no setup).** The scout auto-uses `claude-fable-5` when Fable is available (the most capable model proposes less-generic, better-scoped candidates). Delegate with `model: claude-fable-5`; if that spawn **fails because Fable is unavailable or refused**, re-run it on its default Opus. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces Opus.) See `MODEL-TIERS.md`.

Delegate to the **scout** subagent. Ask it to review the codebase — using `.understand-anything/knowledge-graph.json` if present, otherwise exploring directly — and append a handful of small, evidence-backed candidate features to `FEATURES.md` under the `## Proposed` heading.

If `$ARGUMENTS` is non-empty, treat it as a focus area or constraint (e.g. "focus on the auth module" or "only test-coverage gaps") and pass it to the scout.

The scout only **proposes** — it must not write code and must not touch the `## Ready to build` section. After it finishes, show me its proposals and the one it would pick first, so I can promote the ones I want into "Ready to build" for `/ship-overnight`.
