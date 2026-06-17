---
description: Groom the backlog. Has Opus review the codebase (and its knowledge graph) and propose small, evidence-backed feature candidates into FEATURES.md under "Proposed".
---

Groom the feature backlog: $ARGUMENTS

Delegate to the **scout** subagent. Ask it to review the codebase — using `.understand-anything/knowledge-graph.json` if present, otherwise exploring directly — and append a handful of small, evidence-backed candidate features to `FEATURES.md` under the `## Proposed` heading.

If `$ARGUMENTS` is non-empty, treat it as a focus area or constraint (e.g. "focus on the auth module" or "only test-coverage gaps") and pass it to the scout.

The scout only **proposes** — it must not write code and must not touch the `## Ready to build` section. After it finishes, show me its proposals and the one it would pick first, so I can promote the ones I want into "Ready to build" for `/ship-overnight`.
