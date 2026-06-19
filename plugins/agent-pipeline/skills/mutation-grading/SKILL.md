---
name: mutation-grading
description: Grade a pytest suite with mutation testing — measure whether tests actually ASSERT behaviour, not just execute lines. Use when asked to grade/score test quality, find weak or assertion-free tests, harden a suite, or gate a PR on test strength. Wraps cosmic-ray with a scoped allowlist, a survivor→assertion report, a score trend, and a baseline ratchet.
---

# Mutation grading

Line coverage proves a line *ran*. **Mutation testing proves a test would *fail
if that line were wrong*.** It injects small faults — `<`→`<=`, `and`→`or`,
`True`→`False`, deleting a statement — reruns the suite, and asks "did any test
fail?". A **killed** mutant means your assertions caught the injected bug; a
**survivor** is a bug your suite would ship — i.e. a precise pointer to a
missing assertion. The mutation score is `killed / (killed + survived)`.

This skill bundles `grade_tests.py`, a stdlib-only driver around **cosmic-ray**.

## The strategy (do not skip — this is what makes it usable)

Mutation testing is 10–100× slower than a test run, and an undecidable fraction
of mutants (~4–39%) are **equivalent** — impossible to kill, so they show up as
permanent false "survivors". The whole craft is in *not* running it naively:

1. **Scope tightly. Never mutate the whole repo.** Pick **3–8 pure, deterministic,
   dependency-light modules** that carry real logic (prompt builders, plan
   expanders, scoring/weighting ledgers, preset/mapping tables, validators).
   **Exclude** anything importing torch/GPU/network/DB, plus I/O glue, config,
   and logging. A repo that already splits "torch-free" modules out for host
   pytest has *already done the scoping* — the pure-logic boundary is the
   mutation boundary.
2. **Point each module at its covering tests.** cosmic-ray reruns the
   `test-command` once per mutant; running the whole suite per mutant is
   unusably slow. List the specific `tests = [...]` for each module.
3. **Ratchet a baseline, don't chase 100%.** Target **75–85%** on the scoped set.
   Accept genuine equivalent mutants into a baseline so they stop re-nagging;
   fail only on **new** survivors.
4. **Diff-gate PRs, trend nightly.** On a PR, mutate only changed lines
   (`diff --base`). Nightly, run the full scoped set and append the score to a
   trend file. Keep it on a slow CI lane, off the merge critical path.
5. **Mind test isolation.** Mutation testing assumes a clean, deterministic,
   well-isolated suite. Flaky/order-dependent tests silently corrupt the score.
6. **Never run the suite concurrently with a grading run.** cosmic-ray mutates
   source files **in place** (restoring after each mutant). A normal
   `pytest`/CI/IDE test run launched *while* a grade is executing will import a
   transiently-mutated module and fail spuriously. Run grading on its own; if a
   run is hard-killed mid-flight, check `git status` and `git checkout` any
   left-mutated source before doing anything else.

A scoped score is a **biased** estimate of whole-suite quality (it measures your
most-testable code). Report it *with* the scope caveat — never as "the repo's
test quality" full stop.

## Engine choice

**cosmic-ray** is the default here: it runs your real `pytest` command in place,
so it works with conventional `src/`-layout repos whose tests import with a
package prefix (`from src.x import y`). **mutmut 3.x does not** — its trampoline
asserts module names must not start with `src.`, which breaks that common layout.
Use mutmut only for repos whose package is importable at top level. See
`reference.md` for the full tool comparison and the sourced research.

## Setup

```bash
SETUPTOOLS_USE_DISTUTILS=stdlib pip install cosmic-ray   # stdlib flag dodges a yattag/Debian build quirk
```

Create `mutation_grading.toml` at the repo root:

```toml
[mutation_grading]
test_command  = "python -m pytest -x -q"
timeout       = 30.0
report_path   = "reports/mutation/REPORT.md"
trend_path    = "reports/mutation/trend.jsonl"
baseline_path = "reports/mutation/baseline.json"   # commit this — it's the ratchet
session_dir   = ".mutation/sessions"               # gitignore this

[[mutation_grading.modules]]
path  = "src/video/zoompan_presets.py"
tests = ["tests/test_zoompan_presets.py"]
# ... add 3–8 scoped modules
```

Gitignore `.mutation/` and `reports/mutation/trend.jsonl`; **commit**
`reports/mutation/baseline.json` (it travels with the repo as the ratchet).

## Workflow

```bash
python grade_tests.py run                  # full scoped run -> report + trend; exits 1 on NEW survivors
python grade_tests.py run --module src/x.py # one module while iterating
python grade_tests.py baseline             # accept current survivors (equivalents) as the ratchet floor
python grade_tests.py diff --base origin/main  # PR gate: mutate only changed lines
python grade_tests.py report               # re-render report from existing sessions
```

Read `reports/mutation/REPORT.md`. For each **🆕 survivor**: open its
`module:line`, read the mutated operator, and add/strengthen an assertion in the
covering test so that mutation would now fail. If a survivor is a true
equivalent mutant (an `except ImportError` fallback, a log-only branch, an
unreachable default) accept it with `baseline`. Re-run until no 🆕 survivors
remain and the score has moved, then commit the stronger tests + updated
baseline.

## Checklist

- [ ] Scoped to 3–8 pure, torch/IO-free modules — not the whole repo.
- [ ] Each module points at its **covering** tests (fast, correct).
- [ ] `baseline.json` committed; `.mutation/` + `trend.jsonl` gitignored.
- [ ] Each 🆕 survivor became a new assertion **or** a justified baseline entry.
- [ ] Report quotes the score **with the scope caveat**, not as whole-repo quality.
