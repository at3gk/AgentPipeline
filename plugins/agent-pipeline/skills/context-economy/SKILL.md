---
name: context-economy
description: Spend fewer tokens without losing answers — by compressing at the authoring layer (how handoffs and outputs are written and ordered), never by rewriting the evidence a later stage must verify. Use when writing a pipeline handoff (spec, changes, review, report) or replying to the human: be terse, lead with the verdict, order content for cache hits, and keep every required contract field. Adapts the token-reduction ideas from Headroom (headroomlabs-ai/headroom) as a markdown discipline — no runtime, no compression tool.
---

# Context economy

Most tokens an agent spends are avoidable: preambles ("let me now…"), restating
code the reader can already see, re-deriving a *why* the previous stage already
wrote down. **Cutting that filler is free** — the same bugs get found and the
same fixes get written; the model just stops re-printing what's already on screen.

This skill adapts the token-reduction ideas behind
[Headroom](https://github.com/headroomlabs-ai/headroom) — but **without its
runtime**. Headroom compresses tool outputs in the API path (lossy, and it can't
run in our managed cloud container). We do the opposite: compress at the
**authoring layer** — how we *write* and *order* handoffs and replies — which is
dependency-free, works identically in the cloud, and never touches the evidence.

> The line that makes this safe: **terse means cutting filler, not evidence.**
> Tellingly, Headroom's own design refuses to compress `tool_result` (it calls it
> the "cache hot zone"). Same instinct as our contracts — never paraphrase away
> the diff or output a downstream gate has to check.

## Four practices

### 1. Output economy (with an evidence guardrail)
- **Lead with the answer.** Verdict, root cause, or result in the first line —
  then support it. Never bury it under "Here's what I found…".
- **No preamble or filler.** Drop "Let me…", "I'll now…", "Great question",
  and closing recaps that restate what you just did.
- **Don't restate what's visible.** Don't re-print code, diffs, or file contents
  the reader already has. Point to them (`file:line`) instead of quoting blocks.
- **Match length to the task.** A one-line answer for a one-line question.
- **Guardrail — never compress away required contract content.** Terseness must
  preserve, in full: the parseable `VERDICT:` line, every finding's `file:line`,
  acceptance-check pass/fail evidence, measured before/after numbers, stop-rule
  triggers, and recorded assumptions. If trimming would drop one of those, stop —
  that's evidence, not filler.

### 2. Effort matching
Spend reasoning where judgment actually lives; stay lean where it doesn't. The
pipeline already does the coarse version (opus for Plan / Review / Debug
root-cause / audits; sonnet for the mechanical Code and Test passes). The
principle for any agent: a turn that just confirms a clean tool result needs
little deliberation; a genuine design question, a failure, or a contract decision
gets full effort.

### 3. Cache-friendly ordering
Prompt caches reward a **stable prefix**. So order content stable-first,
volatile-last:
- In a **command/agent prompt**: fixed instructions and `REPO_CONTRACT.md`
  references up top; the run-specific request (the feature, the diff, the symptom)
  at the end.
- In a **handoff file**: the durable structure (headings, the contract fields)
  first; the run's specifics within them. Don't reshuffle stable boilerplate
  between runs — churn there evicts the cache.

### 4. Lossless evidence
Handoffs are **compressed views, not lossy rewrites.** Summarize and *point*:
"validates input via `auth/schema.py:40`" — not a paraphrase of what that code
does. The source of truth (the git diff, the full file, the test log) stays on
disk and any later stage can re-read it. Compress the *description*; never the
*evidence*.

## Checklist

- [ ] First line carries the answer/verdict, not a preamble.
- [ ] No code/diff/file restated that the reader already has — pointed to by `file:line`.
- [ ] Every required contract field is present and intact (verdict, evidence, numbers, triggers).
- [ ] Stable content leads; run-specific content trails (cache-friendly).
- [ ] Evidence is referenced, not paraphrased away.

See `reference.md` for a before/after example, the ordering rule in detail, and
the anti-rationalization / red-flags / verification-gates discipline.
