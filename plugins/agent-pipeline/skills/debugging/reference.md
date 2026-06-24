# Debugging and error recovery — reference

The companion to `SKILL.md`. Triage tactics, how to tell a symptom-fix from a
root-cause fix, and the discipline that keeps "it works now" from meaning "I
moved the bug."

## Localization tactics

- **Read the value backward.** Start at the bad value and walk *up* the call
  chain to where it was born. The throw site is a witness, not the suspect.
- **Binary search everything.** History (`git bisect run <cmd>`), input (delete
  half, does it still fail?), code path (short-circuit a branch). Each cut halves
  the search space — a 1000-line suspect becomes ~10 lines in seven steps.
- **Instrument, don't squint.** A temporary `print`/log of the actual value at a
  chosen frame beats re-reading the code for the fifth time. Remove the
  instrumentation before you finish.
- **Diff against working.** If it worked before, what changed — code, data, dep
  version, environment? The diff is your suspect list.
- **Trust the reproduction, not the report.** Bug reports describe symptoms
  through a user's mental model. Reproduce, then believe only what you observe.

## Symptom-fix vs root-cause fix

The single most common debugging failure is fixing where it *surfaced*:

| Symptom-fix (bad) | What it hides | Root-cause fix |
|---|---|---|
| `if x is None: x = 0` at the crash site | *Why* is x None? A caller returned early / a key was missing upstream. | Fix the upstream path that produced None. |
| `try/except: pass` around the throw | The error still happens; now it's silent and corrupts state later. | Handle the actual failure, or let it raise where it can be handled meaningfully. |
| Special-case the one input that broke | The class of inputs is still mishandled. | Fix the logic for the whole class. |
| Add a retry around a flaky call | Masks a race / ordering bug that will resurface under load. | Find the race; make the operation correct, then retry only true transients. |
| Bump a timeout | The thing is slow for a reason. | Find why it's slow (or accept it explicitly with a measured number — see `/perf`). |

Test: "If I revert this change, does the *cause* return, or only this one
instance of it?" If only this instance, you fixed a symptom.

## The guard test — why "fails first" is non-negotiable

A regression test you never watched fail is unverified in two ways: it might not
exercise the buggy path at all (passes on broken code too), or it might assert
the wrong thing (passes regardless). Watching it go **red on the unfixed code,
then green with the fix** proves it actually pins *this* bug. Sequence:

1. Write the test against the minimal reduced case.
2. Run it on the current (still-broken) tree → it must **fail**, for the right reason.
3. Apply the fix → it must **pass**.
4. Run the surrounding suite → nothing else regressed.

If step 2 passes, your test is not guarding the bug — fix the test before the code.

## When to stop and escalate

A minimal fix is the goal, but not every bug has one. Stop and report instead of
forcing a patch when:

- The root cause is a design flaw (the data model can't represent the case, an
  interface is wrong). That's a `/ship` feature or a `/research-feature`
  decision, not a debug patch.
- The fix would cross a stop rule: add/upgrade a dependency, change a shared or
  public interface, touch auth or data migrations.
- You cannot reproduce it after a genuine effort. Report the reproduction gap and
  what you'd need (inputs, environment, logs) rather than guessing at a fix.

Reporting a well-localized blocker is a success, not a failure. A wrong fix that
hides the bug is the actual failure.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "I can see the bug, I'll just fix it — no need to reproduce." | Then reproduction costs you nothing and proves you right. Skipping it is how symptom-fixes ship. |
| "Wrapping it in try/except makes the error go away." | The error didn't go away; you blindfolded it. It returns as corrupted state somewhere harder to find. |
| "The test passes now, so it's fixed." | Did you watch it fail first? A test green on broken code guards nothing. |
| "It only fails sometimes, probably just flaky." | "Sometimes" is a race, an ordering dep, or hidden state — a real bug telling you where it lives. |
| "This retry/timeout/null-check makes it stable." | Stable symptom, live cause. Find why it needed the crutch. |
| "Fixing the root cause is too big, I'll patch around it." | Then say that out loud and escalate. A silent patch-around is a debt nobody chose to take. |

## Red flags

- You changed code before reproducing the failure.
- Your fix is at the line that threw, not where the bad value originated.
- The diff adds a `try/except: pass`, a blanket retry, or a magic clamp.
- The regression test was never run against the unfixed code.
- "Fixed" is claimed but the suite wasn't run, or a related test now fails.
- The reproduction is non-deterministic and you proceeded anyway.

## Verification gates

Before claiming a fix:
- [ ] Deterministic reproduction existed and now passes.
- [ ] Root cause is stated and was confirmed, not assumed.
- [ ] The guard test was watched failing on the unfixed tree, then passing.
- [ ] The surrounding suite is green; any new failure is surfaced, not hidden.
- [ ] `.pipeline/debug-report.md` records symptom, repro, root cause, fix, guard, risk.
