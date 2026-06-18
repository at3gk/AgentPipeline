---
description: Run the full Map -> Plan -> Code -> Test -> Review -> Explain feature pipeline for the given request.
---

Run the full feature pipeline for: $ARGUMENTS

First, clean up stale handoffs: delete any existing files in `.pipeline/` so no agent reads output from a previous run. Recreate the empty `.pipeline/` directory.

Execute these stages in order. Do not skip ahead. After each stage, confirm the handoff file exists before starting the next.

0. **Map (optional precursor).** If `.understand-anything/knowledge-graph.json` already exists, leave it — the Planner will use it. If it is missing or clearly stale **and** the [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) plugin is installed, run `/understand` first to build a fresh codebase map, then continue. If that plugin is not installed, skip this stage silently — the pipeline still works, the Planner just explores the code directly. (If there is no `REPO_CONTRACT.md` at the repo root yet, consider running `/map-repo` once first — the Planner reads it to ground the spec in canonical patterns.)
1. Delegate to the **planner** subagent with the feature request above. Wait for `.pipeline/spec.md`. Then show me a 2–3 sentence plain-language recap of the plan before continuing, so I can catch a wrong direction early.
2. If the spec has **OPEN QUESTIONS**, stop and show them to me. Otherwise delegate to the **coder** subagent. Wait for `.pipeline/changes.md`. If `changes.md` flags any **stop-rule trigger** (a new dependency, a shared-interface change, a new convention, a skipped test, or an auth/migration touch), stop and show it to me before continuing — do not proceed past a stop rule on your own.
3. Delegate to the **tester** subagent. Wait for `.pipeline/test-results.md`. If tests failed, stop and show me the failures.
4. Delegate to the **reviewer** subagent. Wait for `.pipeline/review.md`.
5. Delegate to the **explainer** subagent in pipeline mode (point it at `.pipeline/`). Wait for `.pipeline/explanation.md`.

Report the final verdict from `review.md` (the first line) and a short summary of `explanation.md`. Do not merge anything. Leave the branch for my review.

For an autonomous, branch-creating version that runs end to end without stopping (ideal for overnight or scheduled cloud runs), use `/ship-overnight` instead.
