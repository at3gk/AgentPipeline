# Mutation grading — reference

Condensed from a Stanford-STORM research briefing (five expert perspectives →
contradiction map → synthesis → peer review, graded **A−**). Sources at the
bottom. Read `SKILL.md` first for the workflow; this is the *why*.

## Core thesis

A suite can execute 100% of lines while asserting almost nothing — "the line
ran" and "a test would catch a bug on that line" are different claims. Mutation
testing closes the gap empirically: it injects faults and checks if a test
fails. **Mutation score = killed / (killed + survived)** where each mutant is:

- **killed** — a test failed (good; your assertions caught the fault).
- **survived** — all tests passed despite the fault (a gap → a missing assertion).
- **timeout** — the mutant caused divergence/infinite loop; counts as killed.
- **no-coverage / incompetent** — no test ran the line, or the mutant won't
  import/compile; excluded from the score denominator.

## Five findings (ranked by reliability)

1. **(10/10) Mutation score measures assertion strength; coverage cannot.** A
   zero-assertion smoke test yields high coverage and near-zero kill rate.
2. **(9/10) Scope tightly; never run whole-suite.** Mutate only pure,
   deterministic, host-testable logic. Caveat: a scoped score is a *biased*
   estimator of whole-suite quality.
3. **(9/10) Diff-gate PRs, trend nightly.** Mutate only changed lines on a PR
   and fail on new survivors; run the full scoped set nightly and trend the
   score to ratchet a baseline. (This is what made Java's PIT adoptable.)
4. **(8/10) Equivalent mutants are an undecidable tax (~4–39%).** Target
   **75–85%**, never 100%; keep an explicit ignore-list so equivalents stop
   re-nagging.
5. **(6/10) Tool choice.** `mutmut` 3.x has the smoothest single-repo pytest
   loop *but* changed its execution model and **requires `fork()`**, and its
   trampoline **rejects `src.`-prefixed module names** — so it breaks the common
   `src/`-layout-with-`from src.x import y` pattern. `cosmic-ray` is the mature,
   broadest-operator tool, runs your real test command in place (layout-agnostic),
   has TOML config + SQLite sessions + parallel/Celery distribution. `mutpy` and
   `mutatest` are unmaintained — avoid. (Speed magnitudes in blogs are secondary
   sources; treat as directional. Validate on your own repo.)

## The hidden connection

Every perspective converges on **scoping**, for different reasons — cost
(economist), noise/adoption-stickiness (skeptic), actionability (practitioner),
historical precedent (historian). The corollary: **a repo that already split
torch-free pure-logic modules out for host pytest has done 80% of the scoping
work.** The discipline that makes tests host-runnable is the same discipline
that makes mutation testing affordable.

## Field blind spot (verify this on a real suite)

**Test isolation / non-determinism is a correctness threat to the mutation run
itself.** If tests share state, leak fixtures, or are order-dependent, a tool's
per-mutant test selection can run the wrong subset and **mislabel** a mutant
(killed→survived or vice-versa), silently corrupting the score. Per-test
isolation fixtures matter doubly under mutation testing.

## Why this skill defaults to cosmic-ray (empirically validated)

On a real `src/`-layout repo (`from src.x import y` in 100+ tests), mutmut 3.6
aborts with `AssertionError: Module name starts with 'src.', which is invalid`.
cosmic-ray runs the identical `python -m pytest` command against the same module
and completes cleanly. The research "weakest link" was exactly this — *run it on
your own scoped set* — and the empirical answer for conventional layouts is
cosmic-ray. The bundled `grade_tests.py` wraps cosmic-ray's
`init`/`exec`/`dump`/`cr-filter-git` into one scoped, ratcheting driver.

## Frontier question

Can LLM-assisted equivalent-mutant detection + survivor→assertion generation
make *whole-repo* mutation testing cheap enough to stop scoping? If an LLM can
discard equivalents and draft the missing assertion per survivor, mutation
testing flips from "expensive audit you scope down" to "continuous
assertion-completeness check you run everywhere".

## Sources

- mutmut docs (readthedocs) + boxed/mutmut (GitHub) — 3.x CLI/config, `fork()`
  requirement, v2-vs-v3 execution model.
- Cosmic Ray docs — TOML config, `new-config`/`init`/`exec`, SQLite session,
  Celery distribution, HTML report.
- "An Analysis and Comparison of Mutation Testing Tools for Python" (IEEE/REU)
  and "Static and Dynamic Comparison…" (SBQS/ACM) — tool maturity (cosmic-ray
  most maintained; mutpy/mutatest stale).
- "The Impact of Equivalent Mutants" (Saarland) and "LLMs for Equivalent Mutant
  Detection" (arXiv 2408.01760) — undecidability, 4–39% rates, LLM frontier.
- "Mutation-Guided LLM-based Test Generation at Meta" (arXiv 2501.12862) —
  survivor→assertion generation frontier.
