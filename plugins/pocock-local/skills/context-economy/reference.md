# Context economy — reference

The companion to `SKILL.md`. Where this comes from, a before/after, the
cache-ordering rule in full, and the discipline that keeps "terse" from quietly
becoming "lossy."

## Where this comes from (and what we deliberately left behind)

[Headroom](https://github.com/headroomlabs-ai/headroom) is a context-compression
layer for AI agents. Two of its ideas transfer to a markdown pipeline; the rest
of it does not, and that distinction is the whole point.

What we **adapt** (its `docs/output-token-reduction-guide.md`):
- **Verbosity steering** — a terseness directive that, at its default level,
  "finds the same bugs and writes the same fixes; it just stops re-printing code
  and the 'let me…' intro." That is our **Output economy** practice.
- **Effort routing** — turn thinking down on a turn that merely follows a clean
  tool result; keep it up for real questions and errors. That is our **Effort
  matching** practice (we already approximate it with the Fable-routing tiers).
- **Prompt-cache preservation** — keep steering text byte-stable and at the end so
  cached prefixes survive. That is our **Cache-friendly ordering** practice.

What we **decline**:
- The **runtime** (proxy / `wrap` / MCP server). It sits in the API path, is lossy,
  and gives **zero benefit in a managed cloud container** that can't be wrapped or
  rerouted. A markdown discipline works everywhere a `.claude/` folder is committed.
- **Lossy rewriting of tool output.** Even Headroom won't do this proxy-side: its
  architecture doc pins `tool_result` as the "cache hot zone" and keeps it intact.
  Here, the tdd-tester reports the *real* run output and CI runs the *real* suite.
  We compress the prose around the evidence, never the evidence.

So: take the authoring-layer ideas, leave the runtime. Same token savings on the
parts that are safe to trim, none of the correctness risk on the parts that aren't.

## Before / after (a tdd-tester red report)

**Before (verbose — restates the tests):**
> Let me walk through the tests I designed for this change. I looked at the
> acceptance criteria and wrote three tests in `tests/test_export.py`. Here is the
> first one:
> ```python
> def test_export_csv_writes_header(): ...
> ```
> I ran them and they all fail right now because `export_csv` doesn't exist yet.
> Overall I think these cover the criteria well. Great, handing back to implement!

**After (terse — same contract, evidence intact, nothing the reader can't see):**
> RED: 3/3 designed tests fail as expected (`export_csv` not implemented).
>
> - criterion 1 (header row) → `tests/test_export.py:12`
> - criterion 2 (comma escaping) → `tests/test_export.py:31`
> - criterion 3 (empty result → empty file) → `tests/test_export.py:48`
> All fail with `ImportError: export_csv` — a missing-behaviour failure, not a
> harness error. These are the contract; implement to them.

The second version is shorter *and* more useful: the red/green result leads, each
criterion is pointed to by `file:line`, and not a byte restates the test the
reader already has.

## The cache-ordering rule, in full

A prompt cache hits only on an **unchanged prefix**. Every byte you let vary early
in the prompt evicts everything after it. So:

- **Stable → volatile.** Fixed instructions and role go first and stay
  byte-identical run to run. The issue scope, the acceptance criteria, the diff —
  the parts that change every run — go last.
- **Don't reorder boilerplate.** Cosmetic churn in the stable region (reordering
  headings, rewording a fixed instruction) costs cache hits for no benefit.
- **Handoffs mirror this.** Keep the report's heading structure fixed; vary only
  the content inside the headings.

This is a modest, free win — and it compounds across the red→implement→green loop
where each step re-reads the shared criteria.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "Restating the test makes the handoff self-contained." | The next step re-reads the file anyway. A `file:line` pointer is self-contained *and* lossless; a paraphrase can drift from the test. |
| "A friendly preamble is more readable." | "Let me now…" is pure token cost. Lead with the red/green result; that's what the reader scans for. |
| "Being terse means I can drop the boring evidence." | The evidence is the point. Cut filler, never the which-tests-fail-and-why, the `file:line`s, or a weakened-test disclosure. |
| "I'll summarize the failing tests instead of pointing to them." | Summarizing evidence is the lossy move Headroom itself refuses. Point, don't paraphrase. |
| "Shorter is always better." | Not if it drops a criterion mapping or a risk the next step (or CI) must see. Match length to the task; preserve the evidence. |

## Red flags

- The first line is a preamble, not the red/green result.
- A test body or diff was re-printed that the reader already has.
- Terseness dropped a `file:line`, a criterion→test mapping, or a disclosed risk.
- A handoff *paraphrases* what a test asserts instead of pointing to it.
- Volatile run-specific content was placed ahead of stable instructions.
- Output length is uncorrelated with task size (a paragraph to say "all green").

## Verification gates

Before finalizing any handoff or human-facing reply:
- [ ] Result/answer is the first line.
- [ ] Nothing restated that's already visible to the reader.
- [ ] Every acceptance criterion maps to its test; red/green evidence intact.
- [ ] Evidence pointed to (`file:line` / file), not paraphrased away.
- [ ] Stable content leads, volatile content trails.
