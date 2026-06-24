---
name: debugging
description: Fix a failure with a disciplined reproduce -> localize -> reduce -> fix -> guard loop that lands a minimal root-cause fix plus a regression test. Use when debugging a bug, a failing test, a stack trace, a crash, or wrong runtime behaviour — anytime the job is to make something broken work, not to build something new.
---

# Debugging and error recovery

A bug is a gap between what the code does and what you believe it does. You close
that gap by **narrowing reality until the cause has nowhere left to hide** — not
by reading hard and guessing. The discipline below is what separates a fix from a
symptom-mover: a change that makes the error message disappear while the actual
defect survives in a new form.

## The five-step loop

### 1. Reproduce — no fix without a trigger
Turn the symptom into something you can run on demand and watch fail: a test, a
script, a one-liner. Make it **deterministic** — if it fails one run in five,
find the source of variance (time, ordering, randomness, shared state) before
anything else. Capture the exact failing output; it's your before/after oracle.
**If you can't reproduce it, you can't fix it** — stop and report what you'd need.

### 2. Localize — find the *root* cause, not the first frame
The line that throws is where the failure *surfaced*, rarely where it *began*.
Bisect toward the origin:
- Read the whole stack; trace the bad value backward to where it was created.
- Binary-search the space: `git bisect` across history, halve the input, disable
  half the code path. Each step halves where the bug can be.
- **State a hypothesis and confirm it** before editing. "I think X is null
  because Y returns early" → prove Y returns early. An unconfirmed hypothesis is
  a guess wearing a lab coat.

### 3. Reduce — shrink to the smallest failing case
Strip the reproduction to the minimum that still fails. The minimal case usually
*names* the cause and becomes the seed of your regression test.

### 4. Fix — the smallest change at the root
Change the **one thing** that addresses the cause. Beware symptom-fixes:
clamping a value, swallowing the exception, special-casing the input that
happened to break. Ask: "if I revert this, does the *cause* come back, or just
this instance?" If the true cause is a design flaw too large for a minimal, safe
change, **stop and report** — don't force a patch. Don't cross stop rules (new
dependency, shared-interface change, auth/migrations) to land a fix.

### 5. Guard — lock it out with a test
Add a regression test and **watch it fail on the unfixed code first**, then pass
with the fix. A test you never saw fail proves nothing — it may be asserting the
wrong thing or not exercising the path at all. This is the only step that stops
the bug from coming back.

## Checklist

- [ ] Reproduced deterministically; exact failing output captured.
- [ ] Root cause confirmed, not assumed — hypothesis tested before editing.
- [ ] Fix addresses the cause, not the symptom; diff is minimal.
- [ ] Regression test **fails before** the fix and **passes after** (both checked).
- [ ] Affected tests (and a quick broader run) are green; any new failure surfaced.
- [ ] No stop rule crossed silently to land the fix.

See `reference.md` for triage tactics, the symptom-vs-cause catalogue, and the
anti-rationalization / red-flags / verification-gates discipline.
