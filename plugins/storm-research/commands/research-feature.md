---
description: Repo-grounded STORM research for a build decision. Runs the four-phase STORM method grounded in this codebase (REPO_CONTRACT.md + a scoped scan + the knowledge graph) so the recommendation names real files and patterns. Saves to research/<slug>.md for the /ship planner to consume. Call it as /research-feature <decision> (optionally "as <role>").
---

Run **repo-grounded** STORM research for this build decision: **$ARGUMENTS**

This is the bridge between the STORM research method and the `agent-pipeline` `/ship` workflow. Plain `/storm` gives a textbook answer; this grounds the research in *your* codebase so the recommendation is actionable — naming the files and patterns to reuse — and the spec the Planner writes inherits a clean decision. Use it before `/ship` for a feature that hinges on an external/domain choice the codebase can't settle (a security scheme, an OAuth flow, an algorithm, a third-party service, a compliance requirement).

Parse the argument: everything before an optional trailing `as <role>` is the **decision** to research. If `... as <role>` is given, use it; otherwise the role defaults to *"an engineer implementing this in this repo"*. If no decision was given at all, ask the user for one and stop.

Delegate to the **storm-researcher** subagent in **repo-grounded mode** (do not run the method inline — its heavy four-phase-plus-grounding context belongs in the subagent's isolated window; only the short briefing returns). Tell it to:

1. **Ground in the repo first.** Build a compact **Codebase constraints** block from what's present: `REPO_CONTRACT.md` at the repo root (canonical patterns, auth, tests, and the package policy), a *scoped* scan of the feature-relevant area, and `.understand-anything/knowledge-graph.json` if it exists. If `REPO_CONTRACT.md` is absent, proceed anyway (the briefing will be less tailored) and note that running `/map-repo` first would sharpen it.
2. **Also ground on the web** if WebSearch / WebFetch are available and the decision is empirical or contested — external evidence and internal constraints compose.
3. Run all four STORM phases per the reference file, threading the Codebase constraints as *feasibility* context: the five personas still research the decision **broadly** (surface options the repo doesn't already use), but the Phase 3 actionable insight must be repo-specific — name the files/patterns to reuse, cite `REPO_CONTRACT.md` entries, and if the recommended option needs a new dependency, justify why the existing deps don't cover it.
4. Save the briefing to `research/<slug>.md` at the repo root (`<slug>` = the decision, lowercased and hyphenated), with a header note recording which repo inputs were used.

When it returns, show the **one-paragraph summary, the 5 ranked findings, the repo-specific actionable insight, and the overall grade**, tell the user the file path, and remind them they can now run `/ship "<the feature>"` — the Planner will read `research/<slug>.md` and ground the spec in it.

> `research/<slug>.md` is a committed file — it's what carries the briefing into a later `/ship` run (and out of an ephemeral cloud session). If the user is on Claude Code on the web and wants to keep it, remind them to commit and push it.
