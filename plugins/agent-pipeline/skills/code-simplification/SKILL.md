---
name: code-simplification
description: Reduce complexity in working code without changing behaviour — remove dead code, de-duplicate toward existing patterns, untangle indirection and over-abstraction, flatten control flow. Honours Chesterton's Fence and proves behaviour is preserved with tests. Use to clean up a diff or module after it works; not a bug hunt and not a rewrite.
---

# Code simplification

Code is read far more than it is written, so the cost that matters is the effort
to *understand* it. This skill reduces that cost — **without changing what the
code does.** That second clause is the whole discipline: a change that makes code
clearer but alters behaviour is not a simplification, it's a bug with good
intentions.

## Chesterton's Fence — the rule everything else serves

> Do not remove a fence until you know why it was put up.

Before touching any construct, **explain why it exists.** The weird extra branch,
the redundant-looking check, the defensive copy — each may be load-bearing: a fix
for a bug invisible in the current code, an edge case, a contract a caller leans
on. If you can't say *why it's there* and *why it's safe to change*, it stays.

- ❌ "This null check looks unnecessary." → guess → regression.
- ✅ "This null check is unreachable: the only caller, `parse()` at
  models.py:40, guarantees non-null. Safe to drop." → reasoned → safe.

## What complexity to remove

- **Dead code** — unreachable branches, unused functions/imports/vars,
  commented-out code. Delete it; version control remembers.
- **Duplication** — repeated logic that should reuse an existing util or pattern.
  De-duplicate toward the **canonical entry in `REPO_CONTRACT.md`**, don't invent
  a fresh abstraction.
- **Needless indirection** — pass-through wrappers, single-use helpers that hide
  more than they save, "flexibility" layers with one implementation.
- **Over-abstraction** — generic machinery with a single caller. **Rule of
  three**: don't abstract until the third real repetition. Premature generality
  is complexity you pay for now and rarely use.
- **Tangled control flow** — deep nesting → early returns / guard clauses;
  boolean thickets → named predicates; conditions that restate each other.
- **Comments that apologize for the code** — replace with a clearer name or shape
  so the comment becomes unnecessary (keep comments that explain *why*, not *what*).

**Fewer lines is not the goal.** A few more lines that read top-to-bottom beat a
dense clever one-liner. Optimize for the next reader, not the character count.

## Behaviour preservation — how you prove it

"Simplified and tests still pass" is the bar, and it's literal:

1. Run the suite first → establish a **green baseline**. (If it's already red,
   stop — that's a `/debug` job, not a cleanup.)
2. Apply only changes you can argue are behaviour-preserving — same outputs, same
   error types, same public interface, same edge-case handling.
3. Run the suite again → **same tests pass, with their assertions unchanged.**
   Editing a test to make it pass means you changed behaviour. That's not allowed
   here.

Anything you can't prove safe stays in the "proposed, not applied" list. Certain
wins get applied; doubts get surfaced.

## Stay in your lane

This is a **quality** pass: it does not hunt bugs (use `/code-review` /
`/grade-tests`), does not add features, and is not a rewrite. If you spot a bug,
note it for `/debug` — don't fix it here under cover of cleanup, where it rides
in untested and unreviewed.

## Checklist

- [ ] Every removal/change has an explicit "why it exists + why it's safe" (Chesterton's Fence).
- [ ] De-duplication reuses the canonical `REPO_CONTRACT.md` pattern, not a new abstraction.
- [ ] No abstraction introduced before the third real repetition.
- [ ] Tests were green before, and the **same** tests (unchanged assertions) are green after.
- [ ] Public interfaces, error types, and outputs unchanged.
- [ ] No bug fixes or features smuggled in; bugs noted for `/debug`.
- [ ] Uncertain changes left as proposals, not applied.

See `reference.md` for before/after patterns and the anti-rationalization /
red-flags / verification-gates discipline.
