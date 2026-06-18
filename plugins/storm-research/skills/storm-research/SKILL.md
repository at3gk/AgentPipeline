---
name: storm-research
description: Research a topic in depth using the Stanford STORM method — simulate 5 expert perspectives, map their contradictions, synthesize a briefing, and peer-review it for reliability. Use when the user wants to genuinely UNDERSTAND a topic (not a quick fact), weigh a decision, do due diligence, or prepare for an interview, negotiation, investment, or presentation — or when they say "STORM", "research briefing", "multi-perspective", or "research this properly". Skip for simple lookups with one right answer.
---

# STORM multi-perspective research

A single prompt gives you the majority view — the surface. STORM (Stanford OVAL
Lab, NAACL 2024) gets you the *practitioner*, the *skeptic*, the *economist*, the
*historian*, and the *academic* all at once, then makes the disagreements between
them do the work. In Stanford's peer-reviewed testing this produced articles ~25%
more organized and ~10% broader than single-prompt research. This skill runs that
method inside one Claude context.

**The exact prompts for all four phases live in [`reference.md`](reference.md)**
(same folder). Read it, then run the phases below in order, in this same context —
each phase reads everything the previous phases produced. Do not restart or
summarize-away the earlier output between phases; that continuity *is* the method.

## Inputs

- **Topic** — what to research (the user's subject).
- **Role** — who the actionable insight is for. If the user gave one ("as a CTO",
  "I'm a founder"), use it; otherwise use "a generalist decision-maker."

## Step 0 — Ground it (only if it helps)

If WebSearch / WebFetch are available **and** the topic is empirical, current, or
contested, gather 3–8 credible sources first and have the personas cite them; end
with a **Sources** list. If web tools aren't available or the topic is conceptual,
run from internal knowledge but **say so at the top of the briefing** and let the
Phase 4 confidence scores carry the uncertainty. Never dress an unsourced claim as
verified — that's the exact failure mode STORM's authors warn about.

## The four phases (run all four, in order, here)

1. **Multi-Perspective Scan** — produce all 5 expert reads (Practitioner,
   Academic, Skeptic, Economist, Historian). For each: core position in 2
   sentences, strongest supporting evidence, and the one thing only that
   perspective would tell you.
2. **Contradiction Map** — where do perspectives directly clash? Strongest vs.
   weakest evidence and why. The one question that would resolve the biggest
   conflict. What *every* perspective agrees on (likely true). What *none* of them
   addressed (the field's blind spot — often the most valuable finding).
3. **Synthesis** — a 60-second CEO summary; 5 key findings ranked by reliability
   (note which perspectives back/challenge each); one hidden connection visible
   only across all 5; a specific **actionable insight** for the role; and the
   frontier question.
4. **Peer Review** — confidence scores (1–10) for each finding with reasons;
   weakest link + what would verify it; bias check (did one voice dominate?);
   missing 6th perspective that might change the conclusions; and an overall
   letter grade with what to fix. This self-critique is mandatory — it's the step
   that catches the source bias STORM is known to let through.

## Output

Deliver the result of **Phase 3 (the briefing) followed by Phase 4 (the peer
review)** as the answer — that's the deliverable. Show the Phase 1 perspectives
and Phase 2 contradiction map if the user wants the full working, or keep them as
the reasoning that produced the briefing. Lead with the one-paragraph summary so a
skimming reader gets the nuance in 60 seconds.

If the user wants this saved to a file or run for several topics in parallel /
in the background, that's what the `/storm` command and the `storm-researcher`
agent in this plugin are for.
