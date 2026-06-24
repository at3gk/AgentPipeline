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
  matching** practice (we already approximate it with the opus/sonnet split).
- **Prompt-cache preservation** — keep steering text byte-stable and at the end so
  cached prefixes survive. That is our **Cache-friendly ordering** practice.

What we **decline**:
- The **runtime** (proxy / `wrap` / MCP server). It sits in the API path, is lossy,
  and gives **zero benefit to our cloud/overnight runs** — the managed container
  can't be wrapped or rerouted. A markdown discipline works everywhere a `.claude/`
  folder is committed, including the cloud.
- **Lossy rewriting of tool output.** Even Headroom won't do this proxy-side: its
  architecture doc pins `tool_result` as the "cache hot zone" and keeps it intact.
  Our Reviewer reads the *real* diff; our Tester records the *real* output. We
  compress the prose around the evidence, never the evidence.

So: take the authoring-layer ideas, leave the runtime. Same token savings on the
parts that are safe to trim, none of the correctness risk on the parts that aren't.

## Before / after (a review handoff)

**Before (verbose — ~110 words, restates the diff):**
> Let me review the changes for this feature. I looked at the git diff and the
> spec carefully. The coder modified `src/reports/export.py` to add a new function
> called `export_csv` which takes the filtered rows and writes them out as CSV.
> Here is the code that was added:
> ```python
> def export_csv(rows): ...
> ```
> Overall this looks good to me. I think the implementation matches the spec well.
> The tests are passing. I'm going to give this a SHIP verdict. Great work!

**After (terse — same verdict, evidence intact, nothing the reader can't already see):**
> VERDICT: SHIP
>
> `export_csv` (`src/reports/export.py:42`) matches the spec; reuses the filter
> parser at `query.py:18` per REPO_CONTRACT. Acceptance checks 1–3 verified in
> `test-results.md`. No stop rules crossed.

The second version is shorter *and* more useful: the parseable verdict leads, the
evidence is pointed to by `file:line`, and not a single byte restates the diff the
reader already has. That's the whole discipline.

## The cache-ordering rule, in full

A prompt cache hits only on an **unchanged prefix**. Every byte you let vary early
in the prompt evicts everything after it. So:

- **Stable → volatile.** Fixed instructions, role, and `REPO_CONTRACT.md`
  references go first and stay byte-identical run to run. The request, the diff,
  the symptom — the parts that change every run — go last.
- **Don't reorder boilerplate.** Cosmetic churn in the stable region (reordering
  headings, rewording a fixed instruction) costs cache hits for no benefit.
- **Handoff files mirror this.** Keep the contract's heading structure fixed;
  vary only the content inside the headings.

This is a modest, free win — and unlike the rest of Headroom, it compounds across
the multi-stage pipeline where each agent re-reads shared context.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "Restating the code makes the handoff self-contained." | The next stage re-reads the source anyway. A `file:line` pointer is self-contained *and* lossless; a paraphrase can drift from the code. |
| "A friendly preamble is more readable." | "Let me now…" is pure token cost. Lead with the verdict; that's what the reader scans for. |
| "Being terse means I can drop the boring evidence." | The evidence is the point. Cut filler, never the `VERDICT:`, the `file:line`s, the numbers, the skipped-check disclosures. |
| "I'll summarize the diff instead of pointing to it." | Summarizing evidence is the lossy move Headroom itself refuses. Point, don't paraphrase. |
| "Shorter is always better." | Not if it drops a required field or a risk the next gate must see. Match length to the task; preserve the contract. |

## Red flags

- The first line is a preamble, not the answer/verdict.
- A code block or diff was re-printed that the reader already has.
- Terseness dropped a `file:line`, a verdict, a measured number, or a disclosed risk.
- A handoff *paraphrases* what code does instead of pointing to it.
- Volatile run-specific content was placed ahead of stable instructions.
- Output length is uncorrelated with task size (a paragraph to say "yes").

## Verification gates

Before finalizing any handoff or human-facing reply:
- [ ] Answer/verdict is the first line.
- [ ] Nothing restated that's already visible to the reader.
- [ ] All required contract fields present and intact (verdict, evidence, numbers, triggers, assumptions).
- [ ] Evidence pointed to (`file:line` / file), not paraphrased away.
- [ ] Stable content leads, volatile content trails.
