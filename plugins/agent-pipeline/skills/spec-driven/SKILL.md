---
name: spec-driven
description: Turn a rough idea into a precise, build-ready brief through one-question-at-a-time discovery, then a definition-of-done checklist. Use when asked to clarify a vague feature request, scope work before building, write a brief or mini-PRD, or decide what "done" means before any code is planned. Feeds the agent-pipeline planner via .pipeline/brief.md.
---

# Spec-driven development

The cheapest bug to fix is the one you clarify away before planning. A vague
request — "add export", "make login better" — gets guessed at, and the guess is
usually wrong in a way nobody notices until review. **This skill removes the
ambiguity first** and captures the result as a `brief`: the smallest document
that lets the Planner write a tight spec.

A brief is a **contract for the Planner**, the same way the spec is a contract
for the Coder. Underspecify it and the Planner either guesses or stalls on
OPEN QUESTIONS; overspecify it and you've written the spec twice. Aim for the
floor that makes the next stage unambiguous.

## The interview — one question at a time

The whole method is one discipline: **ask exactly one question per turn.** Ten
questions at once get skimmed and half-answered. One sharp question gets a real
answer — and that answer tells you what to ask next.

1. **Ground before you ask.** Read `REPO_CONTRACT.md` and the modules the idea
   touches. Anything the code can answer, you answer yourself — never spend a
   question on it. Interview only for intent, priorities, and trade-offs.
2. **Each question is the highest-value unknown left.** The one answer that most
   changes the shape of the work. Attach a **default** so the user can confirm in
   a word or redirect. Make it concrete — name real files and real options.
3. **Restate confidence after each answer.** One line of running understanding
   plus a rough percentage. Stop at **~95%**, or sooner on "just go." Don't pad
   the interview to hit a number.
4. **Split scope creep.** If an answer balloons the work, offer a smaller first
   slice plus a follow-up rather than absorbing it silently.

## Definition of done — the acceptance criteria

The brief's acceptance criteria become the Planner's acceptance checks and,
downstream, what the Reviewer gates on. So they must be **observable**, not
aspirational:

- ✅ "POST /export returns 200 with a text/csv body and a Content-Disposition
  filename; an empty table returns a header-only CSV."
- ❌ "Export works well and handles edge cases."

Each criterion should be something the Tester can verify by running the code.
If you can't phrase it as a check, you haven't clarified it yet.

## The brief template

```markdown
# Brief: <short title>

**Objective** — <one sentence: the user-observable outcome>

## Scope
- <what's in this slice>

## Non-goals
- <what's explicitly out — so the Planner doesn't gold-plate>

## Constraints
- <stack, deps policy, files/areas to prefer or avoid, required patterns>

## Acceptance criteria
- [ ] <observable, checkable condition>
- [ ] <...>

## Open risks
- <uncertainties; flag any external/domain decision for /research-feature>
```

## Checklist

- [ ] Interview asked **one** question per turn, each with a default.
- [ ] Everything answerable from the code was answered without asking.
- [ ] Confidence reached ~95% (or the user said "just go") before writing.
- [ ] Acceptance criteria are observable checks, not aspirations.
- [ ] Non-goals are explicit so the Planner won't gold-plate.
- [ ] Brief written to `.pipeline/brief.md`; recap shown; ready for `/ship`.

See `reference.md` for the full method, worked examples, and the
anti-rationalization / red-flags / verification-gates discipline.
