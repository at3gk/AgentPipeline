---
description: Grade the test suite with mutation testing (cosmic-ray) — find tests that run code without asserting its behaviour, and turn each surviving mutant into a missing-assertion TODO. Scoped, ratcheted, and PR-diff-gateable.
---

Grade the test suite with mutation testing: $ARGUMENTS

Delegate to the **mutation-grader** subagent. Ask it to read the bundled
`mutation-grading` skill, then **scope** mutation testing to a small allowlist
of pure, deterministic, dependency-light modules (prefer ones the repo already
isolates as torch-free / host-testable — never the whole repo), **run**
`grade_tests.py` over them, and **report** the scoped mutation score plus, for
each surviving mutant, the precise `file:line` + operator + the assertion that
is missing.

If `$ARGUMENTS` is non-empty, treat it as a focus or mode and pass it on:
- a focus area (e.g. "just the scoring/weighting modules") → scope to those;
- "improve" / "fix" → after grading, the agent may **add or strengthen tests**
  (test files only — never edit non-test source to kill a mutant) until no new
  survivors remain;
- "diff" / "PR" → run `grade_tests.py diff --base <ref>` to gate only the
  changed lines.

The grader is read-only with respect to source code. When it finishes, show me
the scoped score **with its scope caveat** (it is a biased estimate of
whole-suite quality, not the repo's overall test quality), the real-gap vs
accepted-equivalent split, and the highest-value assertion to add next. Remind
me that `reports/mutation/baseline.json` is meant to be **committed** (it is the
ratchet that fails new survivors), while `.mutation/` and the score trend are
gitignored. Target **75–85%** on the scoped set — never chase 100%.
