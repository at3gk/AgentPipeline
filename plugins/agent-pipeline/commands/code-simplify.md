---
description: Reduce complexity in a scope without changing behaviour — propose simplifications by default, or apply the safe subset with "improve" — keeping tests green throughout.
---

Simplify: $ARGUMENTS

**Model tier.** The simplifier is Fable-eligible: if `AGENT_PIPELINE_FABLE` is `1`, delegate with `model: claude-fable-5` (behaviour-preservation reasoning benefits); otherwise use its default Opus. See `MODEL-TIERS.md`.

Delegate to the **simplifier** subagent. Ask it to read the bundled
`code-simplification` skill, then look for **behaviour-preserving** ways to make
the code clearer: dead code, duplication that should be reused (point it at
`REPO_CONTRACT.md` patterns), needless indirection, over-general abstractions,
tangled conditionals, comments that exist because the code is unclear.

Scope and mode from `$ARGUMENTS`:
- A path/area → scope there. Empty → the current branch's diff vs the default
  branch (simplify what you just wrote).
- Default mode is **propose**: it writes ranked suggestions to
  `.pipeline/simplification.md` and changes nothing.
- `improve` / `apply` / `fix` → after proposing, it **applies the safe subset**
  (clear wins only) and proves behaviour is unchanged by running the tests
  before and after.

Hard rule: **Chesterton's Fence.** It must explain *why* a construct exists
before removing it — anything load-bearing or unexplained stays. This is a
quality pass, not a bug hunt (use `/code-review` or `/grade-tests` for those) and
not a rewrite. When it finishes, show me the top simplifications and, if it
applied any, the proof that tests still pass.
