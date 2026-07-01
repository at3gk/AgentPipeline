---
description: Diagnose and fix a failure with a disciplined reproduce -> localize -> reduce -> fix -> guard loop, landing a minimal fix plus a regression test that locks the bug out.
---

Debug this failure: $ARGUMENTS

**Model tier.** The debugger is Fable-eligible: if `AGENT_PIPELINE_FABLE` is `1`, delegate with `model: claude-fable-5` (root-causing is the hardest reasoning here); otherwise use its default Opus. See `MODEL-TIERS.md`.

Delegate to the **debugger** subagent. `$ARGUMENTS` is the symptom — an error
message, a failing test name, a stack trace, or a plain-language description of
wrong behaviour. Ask it to read the bundled `debugging` skill, then work the
five-step loop:

1. **Reproduce** — get a deterministic, minimal trigger first. No fix without a
   reproduction.
2. **Localize** — bisect to the true root cause; don't stop at the first line
   that throws.
3. **Reduce** — shrink to the smallest failing case.
4. **Fix** — the **minimal** change that addresses the root cause, not the symptom.
5. **Guard** — add a regression test that **fails before the fix and passes
   after**, so the bug can't come back.

It writes `.pipeline/debug-report.md` (root cause in one or two sentences, the
fix, and the guard test) and may edit source and tests — minimally. If the root
cause turns out to be a design problem too large for a minimal fix, it stops and
reports rather than papering over it (consider `/ship` or `/research-feature` for
those).

If `$ARGUMENTS` is empty, ask me for the symptom or run the test suite to find a
current failure to work on.
