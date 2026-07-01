---
description: Measure-first performance audit — profile to find the real hot path, then report (or, with "improve", apply) only optimizations backed by a before/after number. Writes reports/perf/REPORT.md.
---

Performance audit: $ARGUMENTS

**Model tier.** The perf-auditor is Fable-eligible: if `AGENT_PIPELINE_FABLE` is `1`, delegate with `model: claude-fable-5`; otherwise use its default Opus. See `MODEL-TIERS.md`.

Delegate to the **perf-auditor** subagent. Ask it to read the bundled
`performance` skill, then work measure-first: **no number, no change.**

1. **Measure** — profile or time the scope to find where the time/memory actually
   goes. The bottleneck is almost never where intuition points.
2. **Diagnose** — explain *why* the hot path is hot (algorithmic complexity, N+1
   queries, repeated work, allocation, I/O in a loop).
3. **Report / improve** — by default, write `reports/perf/REPORT.md`: the
   measurement, the bottleneck, and ranked optimizations each with an **expected**
   gain. With `improve`/`apply` in `$ARGUMENTS`, apply only changes it can back
   with a **measured before/after**, and keep the tests green.

Scope from `$ARGUMENTS`: a path/area/endpoint to focus on, or empty for the
hot paths the auditor can identify and profile. `improve` switches from audit to
apply.

Hard rule: it **refuses to optimize without a measurement** — premature
optimization that trades clarity for an unverified guess is rejected, not
applied. Behaviour and tests must stay green; a faster wrong answer is not faster.
When it finishes, show me the bottleneck and the before/after for anything it changed.
