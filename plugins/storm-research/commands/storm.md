---
description: Research a topic with the Stanford STORM method — 5 expert perspectives, a contradiction map, a synthesis briefing, and a peer-review reliability check — and save it to research/. Call it as /storm <topic> (optionally "as <role>").
---

Run the STORM research method for: **$ARGUMENTS**

First parse the argument:
- Everything before an optional trailing `as <role>` is the **topic**.
- If the user wrote `... as <role>` (e.g. "...as a CTO"), that's the **role** for
  the actionable insight. Otherwise use "a generalist decision-maker."
- If no topic was given at all, ask the user for one and stop.

Read the canonical STORM prompts from the reference file, then follow all four
phases **in this one context, in order** — each phase reads the output of the
previous one, so do not restart or discard earlier output between phases. That
continuity is the method. The reference file lives at
`${CLAUDE_PLUGIN_ROOT}/skills/storm-research/reference.md` when this runs as an
installed plugin, or at `.claude/skills/storm-research/reference.md` when the files
have been vendored into a repo — read whichever path exists.

1. **Ground it (if it helps).** If WebSearch / WebFetch are available and the topic
   is empirical, current, or contested, gather 3–8 credible sources first and have
   the personas cite them. If not, run from internal knowledge but note that
   plainly at the top of the briefing.
2. **Phase 1 — Multi-Perspective Scan.** All 5 personas (Practitioner, Academic,
   Skeptic, Economist, Historian).
3. **Phase 2 — Contradiction Map.** Where they clash, strongest/weakest evidence,
   the resolving question, universal agreement, and the field's blind spot.
4. **Phase 3 — Synthesis.** CEO summary · 5 findings ranked by reliability · hidden
   connection · a specific actionable insight for **the role** · frontier question.
5. **Phase 4 — Peer Review.** Confidence scores (1–10) · weakest link · bias check ·
   missing 6th perspective · overall letter grade and what to fix.

**Save the result** to `research/<slug>.md` at the repo root, where `<slug>` is the
topic lowercased and hyphenated (create the `research/` directory if needed). The
file should contain, in this order: a title and one-line date/role/grounding note,
then Phase 3 (the briefing), then Phase 4 (the peer review), then the Phase 1
perspectives and Phase 2 contradiction map as an appendix titled "Working", and a
**Sources** list if you grounded with the web.

Then, in the chat, show the **one-paragraph summary, the 5 ranked findings, the
actionable insight, and the overall grade**, and tell the user the file path. Keep
the chat reply tight — the full briefing lives in the file.

> Committing `research/<slug>.md` is what carries the briefing out of an ephemeral
> cloud session. If the user is on Claude Code on the web and wants to keep it,
> remind them to commit and push it (or do so if they ask).
