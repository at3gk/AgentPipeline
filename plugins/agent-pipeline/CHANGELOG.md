# Changelog

## 1.8.0

- **Matt Pocock skills integration** ([mattpocock/skills](https://github.com/mattpocock/skills)).
  All new behavior is gated on the convention files `/setup-matt-pocock-skills`
  writes (`docs/agents/issue-tracker.md`, `triage-labels.md`, `domain.md`);
  repos without them keep the previous behavior exactly.
  - **Domain-docs awareness**: the Planner, Reviewer, Clarifier, and Debugger
    read `CONTEXT.md` (domain glossary — terms used verbatim, no synonym drift)
    and `docs/adr/` when present. ADR conflicts are surfaced, never silently
    overridden: the Planner flags them as OPEN QUESTIONS, the Clarifier makes
    them the first interview question, the Reviewer BLOCKs a diff that
    contradicts an accepted ADR unless the spec or issue reopens it, and the
    Debugger reports (not fixes) a "bug" that matches an accepted decision.
  - **Issue-faithfulness gate**: issue-sourced runs write the full issue text
    to `.pipeline/issue.md` (after the cleanup step); the Planner treats it as
    the source of truth for what to build, and the Reviewer checks the diff
    against the originating issue — not just the spec — naming any unmet
    requirement verbatim and rejecting scope creep.
  - **Agent-ready proposals**: the scout files issues with the `/to-issues`
    body template (What to build / Acceptance criteria / Blocked by) plus a
    category label, so promotion is a label flip; `/ship-overnight` recognizes
    both the `## Blocked by` heading and inline `Blocked by: #n` blockers.
  - **`/setup-pipeline` bootstrap**: a new attended command that installs the
    Matt skills per the upstream README (checked at run time), verifies
    `gh auth status`, and drives `/setup-matt-pocock-skills`. Commands point
    at it in one line when conventions are missing; `/ship-overnight` never
    installs anything mid-run — it falls back and notes the gap in the
    morning report.
  - `/ship` closes by suggesting the Matt `/code-review` skill as an
    independent final gate (never invoked automatically — most Matt skills
    are user-typed only).
- **Built-in self-check questions.** The Planner, Reviewer, and Debugger now
  end their stage by answering "What am I least confident about right now?"
  and "What's the biggest thing I'm missing — what don't I realize?" (spec
  confidence note, review Residual doubts, debug-report residual risk); the
  Clarifier asks the blind-spot question as its final interview question; the
  `/ship` Learn stage asks the user the first and answers the second; and the
  `/ship-overnight` morning report carries both answers as a self-check
  section.

## 1.7.0

- **GitHub-issues-first backlog** (Matt Pocock skills convention). When a repo
  declares GitHub Issues as its tracker (`docs/agents/issue-tracker.md` at the
  repo root, labels in `docs/agents/triage-labels.md`), backlog operations go
  through `gh`:
  - `/ship` accepts an issue reference (`#123`, a bare number, or an URL) and
    builds from the full issue thread; the human closes the issue (attended flow).
  - `/ship-overnight` with no argument pulls the oldest open, unassigned
    `ready-for-agent` issue (skipping assigned or `Blocked by: #n`-blocked ones),
    claims it by assignment, comments + closes on ship, and unassigns + leaves it
    open when blocked. It never pulls `needs-triage`/`needs-info` issues.
  - `/suggest-features` (the scout) files proposals as `needs-triage` issues,
    dedupes against open and recently closed issues, and never applies
    `ready-for-agent` — promotion stays a human act.
  - Repos without the tracker file keep the exact existing `FEATURES.md`
    behavior; `gh` is never required there.

## 1.6.0 and earlier

See git history.
