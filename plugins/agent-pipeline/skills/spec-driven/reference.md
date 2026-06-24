# Spec-driven development — reference

The companion to `SKILL.md`. This is the long form: why discovery beats
guessing, a worked interview, and the discipline that keeps a clarifying pass
from becoming a requirements-gathering marathon.

## Why a brief, and why before planning

The Planner is good at turning a *clear* request into a tight spec. It is bad —
as is any agent — at guessing what you *meant*. Every ambiguity it can't resolve
becomes either a silent assumption (wrong ~half the time) or an OPEN QUESTION
that stalls the run. A five-minute interview up front converts both into
decisions, and the decisions live in one place the Planner reads.

The brief is deliberately smaller than a PRD. It is not a document for
stakeholders; it is the **handoff that grounds `.pipeline/spec.md`**. Capture
what was decided, nothing more.

## The one-question rule, illustrated

Bad (a wall — gets skimmed):

> 1. What format? 2. Auth required? 3. Which table? 4. Pagination? 5. Filename?
> 6. Empty case? 7. Streaming or buffered? 8. Which endpoint path?

Good (one at a time, each grounded and defaulted):

> I see `reports` is rendered from `ReportRow` in `src/reports/models.py`.
> **Which rows should the export include — the current filtered view, or the
> whole table?** (Default: the current filtered view, matching what the user
> sees on screen.)

The user answers "filtered view," your confidence jumps, and the *next* question
is now obvious (how filters arrive at the endpoint) — which you couldn't have
asked well before the first answer. That's why the wall is worse than it looks:
it freezes the question set before you've learned anything.

## Reaching confidence — and stopping

Track a rough percentage out loud after each answer. The goal is **~95%**: high
enough that the Planner won't have to guess, not so high that you're asking about
things that don't change the build. Two failure modes, equally bad:

- **Stopping at 60%** because the conversation felt done — the Planner inherits
  the gaps.
- **Grinding to 99%** by inventing questions — you've now written the spec in the
  interview and wasted the user's time.

When the user says "just go" or "you decide," stop immediately and record the
remaining unknowns as **Open risks** with your chosen default. That's a
legitimate 95%: explicit assumptions beat unasked questions.

## Worked brief

```markdown
# Brief: CSV export for the reports table

**Objective** — A user viewing the reports table can download the currently
filtered rows as a CSV.

## Scope
- New GET endpoint that streams the filtered ReportRow set as text/csv.
- A "Download CSV" button on the reports view wired to it.

## Non-goals
- No XLSX/PDF. No background-job/email delivery. No new columns.

## Constraints
- Reuse the filter parsing in src/reports/query.py (REPO_CONTRACT: "report filters").
- No new dependencies — stdlib csv is sufficient.
- Auth: same session guard as the reports view (Forbidden: auth module changes).

## Acceptance criteria
- [ ] GET /reports/export?<filters> returns 200, text/csv, with a
      Content-Disposition filename.
- [ ] The CSV rows match the on-screen filtered set exactly (same order).
- [ ] An empty result returns a header-only CSV, not a 500.

## Open risks
- Very large exports could be slow; streaming chosen over buffering as a hedge.
  Not load-tested in this slice (flagged for /perf later).
```

Notice what's *absent*: no function signatures, no file-by-file plan. That's the
Planner's job. The brief fixes intent and boundaries; the spec fixes mechanics.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "I basically know what they want, I'll skip the interview." | "Basically" is where the rework lives. One grounded question is cheaper than one wrong slice. |
| "Let me ask everything now to save round-trips." | The wall freezes your questions before you've learned anything. Each answer should reshape the next question. |
| "It's a small change, a brief is overkill." | Then the interview is one question and the brief is six lines. Small ≠ unspecified. |
| "I'll let the Planner sort out the ambiguity." | The Planner guesses or stalls. Neither is clarification — you've just moved the gap downstream. |
| "More detail is always safer, I'll spec it fully here." | Then you've written the spec twice and boxed in the Planner. Stop at intent + boundaries. |

## Red flags

- You asked more than one question in a single turn.
- You asked something the code already answers.
- The brief contains function signatures or a file-by-file plan (that's the spec).
- Acceptance criteria read as adjectives ("robust", "clean") not checks.
- Confidence never got stated, or jumped to "done" without passing through a number.
- The interview ran more than a handful of questions for a bounded change.

## Verification gates

Before writing the brief:
- [ ] Every question that could be answered by reading code, was.
- [ ] Confidence is ~95% **or** the user said go (with assumptions recorded).

Before declaring it ready for `/ship`:
- [ ] `.pipeline/brief.md` exists and follows the template.
- [ ] Every acceptance criterion is an observable check the Tester could run.
- [ ] Non-goals are explicit.
- [ ] A 3–4 line recap was shown to the user.
