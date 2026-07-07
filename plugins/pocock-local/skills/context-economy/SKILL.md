---
name: context-economy
description: Spend fewer tokens without losing answers — by compressing at the authoring layer (how agent handoffs and outputs are written and ordered), never by rewriting the evidence a later stage must verify. Use when writing a ship-local handoff (plan/acceptance criteria, tdd-tester red or green report) or replying to the human: be terse, lead with the result, order content for cache hits, and keep every piece of evidence intact. Adapts the token-reduction ideas from Headroom (headroomlabs-ai/headroom) as a markdown discipline — no runtime, no compression tool.
---

# Context economy

Most tokens an agent spends are avoidable: preambles ("let me now…"), restating
code the reader can already see, re-deriving a *why* the previous stage already
wrote down. **Cutting that filler is free** — the same tests get designed and the
same failures get reported; the model just stops re-printing what's already on
screen.

This skill adapts the token-reduction ideas behind
[Headroom](https://github.com/headroomlabs-ai/headroom) — but **without its
runtime**. Headroom compresses tool outputs in the API path (lossy, and it can't
run in a managed cloud container). We do the opposite: compress at the
**authoring layer** — how we *write* and *order* handoffs and replies — which is
dependency-free, works identically everywhere `.claude/` is committed, and never
touches the evidence.

> The line that makes this safe: **terse means cutting filler, not evidence.**
> Tellingly, Headroom's own design refuses to compress `tool_result` (it calls it
> the "cache hot zone"). Same instinct here — never paraphrase away the failing
> test, the diff, or the run output a downstream step (or CI) has to check.

This is a lean plugin, so the handoff surface is small but real: `ship-local`
passes acceptance criteria to the **tdd-tester**, which hands back a red report
(the failing tests that are the contract) and later a green report. Those are the
places this discipline pays off.

## Four practices

### 1. Output economy (with an evidence guardrail)
- **Lead with the result.** The red/green outcome, the count of failing tests, or
  the answer in the first line — then support it. Never bury it under "Here's what
  I found…".
- **No preamble or filler.** Drop "Let me…", "I'll now…", "Great question", and
  closing recaps that restate what you just did.
- **Don't restate what's visible.** Don't re-print code, diffs, or test bodies the
  reader already has. Point to them (`file:line`) instead of quoting blocks.
- **Match length to the task.** A one-line answer for a one-line question.
- **Guardrail — never compress away real evidence.** Terseness must preserve, in
  full: which tests fail and *why* (red), the pass/fail result (green), each
  acceptance criterion → the test that covers it, `file:line`s, and any weakened
  test or surfaced risk. If trimming would drop one of those, stop — that's
  evidence, not filler.

### 2. Effort matching
Spend reasoning where judgment lives; stay lean where it doesn't. This plugin's
Fable routing (`MODEL-TIERS.md`) already does the coarse version — route the
harder-reasoning stage to `claude-fable-5` when it's available, keep the tester on
Sonnet by default. The per-turn principle: confirming a clean green run needs
little deliberation; designing tests for a subtle acceptance criterion, or
diagnosing a failure, gets full effort.

### 3. Cache-friendly ordering
Prompt caches reward a **stable prefix**. Order content stable-first, volatile-last:
- In a **command/agent prompt**: fixed instructions up top; the run-specific
  content (the issue scope, the acceptance criteria, the diff) at the end.
- In a **handoff**: the durable structure (headings) first; the run's specifics
  within them. Don't reshuffle stable boilerplate between runs — churn there
  evicts the cache.

### 4. Lossless evidence
Handoffs are **compressed views, not lossy rewrites.** Summarize and *point*:
"criterion 2 covered by `tests/test_export.py:31`" — not a paraphrase of what that
test asserts. The source of truth (the test file, the git diff, the run log) stays
on disk and any later step — or CI — can re-read it. Compress the *description*;
never the *evidence*.

## Checklist

- [ ] First line carries the result/answer, not a preamble.
- [ ] No code/diff/test restated that the reader already has — pointed to by `file:line`.
- [ ] Every acceptance criterion still maps to its test; red/green evidence intact.
- [ ] Stable content leads; run-specific content trails (cache-friendly).
- [ ] Evidence is referenced, not paraphrased away.

See `reference.md` for a before/after example, the ordering rule in detail, and
the anti-rationalization / red-flags / verification-gates discipline.
