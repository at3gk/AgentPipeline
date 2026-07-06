---
description: Lean, test-driven ship flow for a CI-backed repo — scope with grilling, plan, design failing tests, implement to green, confirm, open a PR. Composes the Matt Pocock skills; trusts CI for the full suite.
---

Ship this work, test-first: $ARGUMENTS

A deliberately lean loop for a repo that **already has CI/CD and a test suite**.
It does not re-implement contracts, stop-rule gates, or a mutation grader — CI is
the regression gate and the Matt Pocock skills do the heavy lifting. Your job is
to drive the TDD red→green loop and open a PR.

**Model tier.** When `claude-fable-5` is available, route each stage to the model
it needs per `MODEL-TIERS.md` (guidance, not a mandate); otherwise use defaults.
`POCOCK_FABLE=0` forces defaults. The Pocock `implement` / `code-review` skills
are user-typed and run on the session model — this command composes around them.

## 0. Pick the work

- If `$ARGUMENTS` names an issue (`#123`, a bare number) or a local mirror path,
  use it. Otherwise take the issue the user points at.
- Read the mirrored issue at `<mirror>/<number>/snapshot.md` (from
  `/pocock-local:sync-issues`). If it isn't mirrored yet, run the sync or ask.

## 1. Scope with `grilling` (required — the synced issue may be thin)

The Slack-synced issue is often under-specified. **Before planning, ask the user
to run the Pocock `grilling` skill** on it to interrogate and complete the scope.
Pocock skills are `disable-model-invocation: true` (user-typed only), so you
**surface the step and wait** — never invoke it yourself. Capture the enriched
scope into the issue's `notes.md` (human-owned; append, don't clobber) so it
persists in the mirror and feeds the next steps.

## 2. Plan (light)

From the *grilled* scope, write a short spec and a concrete **acceptance
criteria** list — just enough to drive tests. No four-contract machinery. For a
larger/vaguer piece, suggest the Pocock `to-prd` skill instead of hand-rolling.

## 3. Design tests first — red (delegate to **tdd-tester**, DESIGN mode)

Delegate to the **tdd-tester** subagent in **DESIGN** mode with the acceptance
criteria. It writes tests encoding each criterion and **confirms they fail**
against the current code. These failing tests are the contract for the change.
If nothing can be made to fail meaningfully, the criteria are too vague — go back
to step 1.

## 4. Implement — green (Pocock `implement`)

Ask the user to run the Pocock `implement` skill (user-typed) to make the
designed tests pass, or implement to the tests directly if that's the agreed
flow. **The tests are fixed; code changes to fit them**, not the reverse. If a
test turns out wrong, change it deliberately and out loud, never silently.
Minimal safety note: don't silently add a dependency or touch auth/migrations to
force green — surface it instead.

## 5. Confirm — (delegate to **tdd-tester**, CONFIRM mode)

Delegate to the **tdd-tester** in **CONFIRM** mode. It re-runs the designed tests and
reports them green (flagging any it had to weaken). It does **not** fix code. The
**full suite + lint run in CI** on the PR — don't re-run the whole suite here.

## 6. Open a PR — your naming, CI gates, human review closes the issue

Open a PR for the change. **Respect the team's own conventions — do not impose a
branch or PR name.** If the user works in a `git worktree` with a branch already
checked out, ship from it; otherwise ask what to branch/name rather than inventing
a `feat(...)`-style title. Default the PR title/body from the issue only as a
*suggestion* the user can overwrite.

- **CI/CD is the test gate** — the PR runs the full suite; you don't merge.
- Suggest the user run the Pocock `/code-review` skill (user-typed) against the
  PR as the review gate.
- **The issue closes when the PR merges** — human review committing to the merge
  is the final say. Don't close it here.

Leave the PR for review. Do not merge.
