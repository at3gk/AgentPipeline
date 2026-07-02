---
description: Turn a rough idea into a precise, build-ready brief by interviewing you one question at a time, then writing .pipeline/brief.md for the planner to pick up.
---

Clarify this idea into a build-ready brief: $ARGUMENTS

**Model tier (automatic — no setup).** The clarifier auto-uses `claude-fable-5` when Fable is available (better discovery-interview judgment; brief quality compounds into the plan). Delegate with `model: claude-fable-5`; if that spawn **fails because Fable is unavailable or refused**, re-run it on its default Opus. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces Opus.) See `MODEL-TIERS.md`.

Delegate to the **clarifier** subagent. Ask it to read the bundled
`spec-driven` skill, then run a **one-question-at-a-time** discovery interview
with me — never a wall of questions — until it can describe the work at ~95%
confidence. Each question should be the single highest-value unknown left,
offer a sensible default, and build on my previous answer.

When it has enough, it writes a tight brief to `.pipeline/brief.md` (objective,
scope and non-goals, constraints, acceptance criteria, open risks) and shows me
a short recap.

This is the **Define** stage — the optional precursor to `/ship`. The Planner
reads `.pipeline/brief.md` on its next run and grounds the spec in it, so
`/clarify <idea>` then `/ship` (no argument re-states the idea) is the natural
chain. The clarifier is **read-only** with respect to source code: it asks,
researches the repo to ground its questions, and writes only the brief.

If `$ARGUMENTS` is empty, ask me what I want to build first, then begin the
interview.
