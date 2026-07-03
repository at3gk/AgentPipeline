---
description: Run the full Map -> Plan -> Code -> Test -> Review -> Learn feature pipeline for the given request.
---

Run the full feature pipeline for: $ARGUMENTS

**GitHub issue as the request.** If the request above references a GitHub issue — `#123`, a bare issue number, or an issue URL — fetch it with `gh issue view <n> --comments` and treat the full issue (title, body, and comments) as the feature request: pass that full text to the Planner, along with any documents the issue links (e.g. a PRD). When the pipeline finishes, remind me to comment on and close the issue after I've reviewed the branch — do **not** close it yourself. This is the attended flow: the human owns the issue lifecycle.

First, clean up stale handoffs: delete any existing files in `.pipeline/` so no agent reads output from a previous run. Recreate the empty `.pipeline/` directory.

**Model tier (automatic — no setup).** The **planner**, **coder**, and **reviewer** stages run on `claude-fable-5` when Fable is available and fall back to their defaults when it isn't. Detect availability from the first eligible delegation: spawn the **planner** with `model: claude-fable-5` (per-spawn override). If that spawn **fails because Fable is unavailable or refused** (not accessible to this org, or a zero-data-retention `400`), re-run the planner on its default model and use the defaults for the coder and reviewer too this run. If it **succeeds**, use `claude-fable-5` for the coder and reviewer as well. The **Tester stays Sonnet**; everything else stays Opus. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces the default tier even when Fable is available.) See `MODEL-TIERS.md`.

Execute these stages in order. Do not skip ahead. After each stage, confirm the handoff file exists before starting the next.

0. **Map (optional precursor).** If `.pipeline/brief.md` exists (from a prior `/clarify` run), the Planner will read it and ground the spec in your clarified objective and acceptance criteria — for a vague request, consider running `/clarify <idea>` first. If `.understand-anything/knowledge-graph.json` already exists, leave it — the Planner will use it. If it is missing or clearly stale **and** the [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) plugin is installed, run `/understand` first to build a fresh codebase map, then continue. If that plugin is not installed, skip this stage silently — the pipeline still works, the Planner just explores the code directly. (If there is no `REPO_CONTRACT.md` at the repo root yet, consider running `/map-repo` once first — the Planner reads it to ground the spec in canonical patterns. And if this feature hinges on a real external/domain unknown — a security scheme, an algorithm, a third-party service — consider running `/research-feature <the decision>` first; the Planner will read its `research/<slug>.md` briefing and ground the spec in it.)
1. Delegate to the **planner** subagent with the feature request above. Wait for `.pipeline/spec.md`. Then show me a 2–3 sentence plain-language recap of the plan before continuing, so I can catch a wrong direction early.
2. If the spec has **OPEN QUESTIONS**, stop and show them to me. Otherwise delegate to the **coder** subagent. Wait for `.pipeline/changes.md`. If `changes.md` flags any **stop-rule trigger** (a new dependency, a shared-interface change, a new convention, a skipped test, or an auth/migration touch), stop and show it to me before continuing — do not proceed past a stop rule on your own.
3. Delegate to the **tester** subagent. Wait for `.pipeline/test-results.md`. If tests failed, stop and show me the failures.
4. Delegate to the **reviewer** subagent. Wait for `.pipeline/review.md`.
5. **Learn — interactive understanding session (run by you, the orchestrator, not a subagent).** First report the review verdict from `review.md` (its first line). Then, if the run shipped, do **not** delegate this stage and do **not** just write a file — an explanation a subagent files away is one I will skip. Instead, *you* already hold the full context (`spec.md`, `changes.md`, `test-results.md`, `review.md`, plus `git diff`), so walk me through the change live so I can stand behind it at push/review time:
   - Open with the **mental model** (2–3 sentences: what changed and how to think about it) and the **guided reading order** — the handful of files/hunks to read and what each contributes.
   - Then walk the change **one logical unit at a time** (grouped by behaviour, not mechanically file-by-file). For each unit: frame the *why* in a sentence, point me at the `file:line`, then **check my understanding with one pointed question** — an edge case, why this approach over the obvious alternative, or what would break if it were reverted — and **wait for my answer before moving on**. Confirm or correct it. The goal is active recall, not a lecture I skim.
   - Invite my questions at each step, and adapt the pace: compress where I am clearly following, slow down and dig where I stumble.
   - Close with a short recap and what to study next. Then **offer** to write the session's key points to `.pipeline/explanation.md` as a record for the PR description / code review — write it only if I say yes.

Do not merge anything. Leave the branch for my review.

**Optional extra gates (opt-in, not part of the core flow).** For a security-sensitive feature, after the Review stage run `/security-review` as an extra gate before you merge — it audits the branch diff and writes a parseable `VERDICT` to `reports/security/REPORT.md`. After the pipeline, `/code-simplify` cleans up the new code behaviour-preservingly, and `/perf` profiles any hot path. These are separate pipelines you invoke deliberately; `/ship` does not run them automatically.

For an autonomous, branch-creating version that runs end to end without stopping (ideal for overnight or scheduled cloud runs), use `/ship-overnight` instead.
