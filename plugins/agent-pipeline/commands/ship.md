---
description: Run the full Planner -> Coder -> Tester -> Reviewer -> Explainer feature pipeline for the given request.
---

Run the full feature pipeline for: $ARGUMENTS

First, clean up stale handoffs: delete any existing files in `.pipeline/` so no agent reads output from a previous run. Recreate the empty `.pipeline/` directory.

Execute these stages in order. Do not skip ahead. After each stage, confirm the handoff file exists before starting the next.

1. Delegate to the **planner** subagent with the feature request above. Wait for `.pipeline/spec.md`.
2. If the spec has **OPEN QUESTIONS**, stop and show them to me. Otherwise delegate to the **coder** subagent. Wait for `.pipeline/changes.md`.
3. Delegate to the **tester** subagent. Wait for `.pipeline/test-results.md`. If tests failed, stop and show me the failures.
4. Delegate to the **reviewer** subagent. Wait for `.pipeline/review.md`.
5. Delegate to the **explainer** subagent in pipeline mode (point it at `.pipeline/`). Wait for `.pipeline/explanation.md`.

Report the final verdict from `review.md` and a short summary of `explanation.md`. Do not merge anything. Leave the branch for my morning review.
