# STORM — the canonical prompts

> Single source of truth for the four-phase STORM method. The skill, the
> `/storm` command, and the `storm-researcher` agent all follow these.
> Adapted from the Stanford STORM method (Stanford OVAL Lab, NAACL 2024 —
> *Synthesis of Topic Outlines through Retrieval and Multi-perspective
> Question Asking*). Live demo: https://storm.genie.stanford.edu ·
> Code: https://github.com/stanford-oval/storm (MIT).
>
> Placeholders: `{{TOPIC}}` is the subject being researched. `{{ROLE}}` is the
> reader's role for the actionable insight (e.g. "a CTO", "a first-time
> founder", "a generalist decision-maker" if unspecified).

The method's whole edge is **multi-perspective questioning in one continuous
context**: each phase reads the output of the previous one. Run all four phases
in the same conversation/context — never start the contradiction map, synthesis,
or peer review fresh, because each depends on everything above it.

---

## The five perspectives

1. **THE PRACTITIONER** — works with this daily. What do they know that
   academics miss? What practical realities are usually ignored?
2. **THE ACADEMIC** — has studied this for years. What does the peer-reviewed
   evidence actually say? Where does the evidence contradict popular belief?
3. **THE SKEPTIC** — thinks the mainstream view is wrong. What is the strongest
   counterargument? What evidence do proponents conveniently ignore?
4. **THE ECONOMIST** — follows the money. Who profits from the current
   narrative? What financial incentives shape the research?
5. **THE HISTORIAN** — has seen similar patterns before. What historical
   parallels exist? What can we learn from how those played out?

---

## Phase 1 — The Multi-Perspective Scan

```
I need to research {{TOPIC}}.

Simulate 5 different expert perspectives on this topic:

1. THE PRACTITIONER: works with this daily.
   What do they know that academics miss?
   What practical realities are usually ignored?
2. THE ACADEMIC: has studied this for years.
   What does the peer reviewed evidence actually say?
   Where does the evidence contradict popular belief?
3. THE SKEPTIC: thinks the mainstream view is wrong.
   What is the strongest counterargument?
   What evidence do proponents conveniently ignore?
4. THE ECONOMIST: follows the money.
   Who profits from the current narrative?
   What financial incentives shape the research?
5. THE HISTORIAN: has seen similar patterns before.
   What historical parallels exist?
   What can we learn from how those played out?

For each perspective give me:
- Their core position in 2 sentences
- The strongest evidence supporting their view
- The one thing they would tell me that no other perspective would
```

## Phase 2 — The Contradiction Map

```
Based on the 5 perspectives above, map the contradictions:

1. Where do two or more perspectives directly contradict each other?
   List each conflict with the specific claims that clash.
2. Which perspective has the strongest evidence?
   Which has the weakest? Why?
3. What is the one question that, if answered, would resolve the
   biggest contradiction?
4. What does EVERY perspective agree on?
   (This is likely true. Even opponents confirm it.)
5. What topic did NONE of the perspectives address?
   (This is the blind spot in the whole field. Often the most
   valuable finding.)
```

## Phase 3 — The Synthesis

```
Synthesize everything from the 5 perspectives and the contradiction map
into a research briefing:

1. THE ONE PARAGRAPH SUMMARY: explain this topic as if briefing a CEO who
   has 60 seconds and needs nuance, not just the headline.
2. THE 5 KEY FINDINGS: most important things I now know, ranked by
   reliability. For each, note which perspectives support it and which
   challenge it.
3. THE HIDDEN CONNECTION: one non-obvious link between findings that only
   shows up when you look at all 5 perspectives together.
4. THE ACTIONABLE INSIGHT: based on all the evidence, what should
   {{ROLE}} actually DO differently? Be specific.
5. THE FRONTIER QUESTION: the one question that, if answered, would change
   everything about how we understand this topic.
```

## Phase 4 — The Peer Review

```
Now peer review your own research briefing:

1. CONFIDENCE SCORES: rate each of the 5 key findings on a 1 to 10 scale
   for reliability. Explain each score.
2. WEAKEST LINK: which claim are you least confident in? What specific
   info would you need to verify it?
3. BIAS CHECK: which perspective might be overrepresented in your
   synthesis? Did one voice dominate?
4. MISSING PERSPECTIVE: is there a 6th angle I should have included that
   would change the conclusions?
5. OVERALL GRADE: if a Stanford professor reviewed this briefing, what
   grade would they give and why? What would they tell me to fix?
```

---

## Optional grounding (makes it *sourced*, not just plausible)

STORM is a *retrieval* method — the real system reads sources before it writes.
The original four-prompt hack runs purely from the model's memory, and Stanford's
own researchers flag that source bias and fact misassociation can creep in. To
close that gap:

- **If web tools are available** (WebSearch / WebFetch) and the topic is
  empirical, current, or contested: gather 3–8 credible sources *before* Phase 1
  and have each persona cite them. Attach a **Sources** list to the briefing and
  footnote the 5 key findings.
- **If no web tools are available** (or the topic is conceptual): run from
  internal knowledge, but say so plainly at the top of the briefing and let the
  Phase 4 confidence scores carry the uncertainty. Never present an unsourced
  claim as if it were verified.

## Optional codebase grounding (makes it *actionable for one repo*)

When the research is for a decision inside a specific codebase — "rate limiting
*for this service*", "which OAuth flow *for this app*" — ground it in the repo so
the recommendation names real files and patterns instead of textbook generalities.
This is what the `/research-feature` command and the repo-grounded `storm-researcher`
mode do. Assemble a compact **Codebase constraints** block before Phase 1 from
whatever is present:

- `REPO_CONTRACT.md` at the repo root — the curated index of canonical patterns,
  the auth approach, the test setup, and the **package/dependency policy**.
- A *scoped* Grep/Glob scan of the feature-relevant area (the existing code this
  decision touches) — not the whole repo.
- `.understand-anything/knowledge-graph.json` if present.

Then thread that block through the method **without** narrowing the research:

- **Phase 1 framing:** prepend the Codebase constraints as *feasibility* context.
  The five personas still research the topic **broadly** (surface options the repo
  doesn't already use); the constraints tell them what would have to be true to
  adopt an option here. Do not let the constraints collapse the perspectives into
  a description of the existing stack — that throws away STORM's edge.
- **Role:** set `{{ROLE}}` to *"an engineer implementing this in `<repo>`"*.
- **Phase 2 blind spot:** let the codebase context inform what *none* of the
  perspectives addressed (e.g. an option that's a poor fit for this stack).
- **Phase 3 actionable insight:** make it **repo-specific** — name the files and
  patterns to reuse, cite the relevant `REPO_CONTRACT.md` entries, and honor the
  package policy: if the recommended option needs a new dependency, say so and
  justify why the existing deps don't cover it (this mirrors the Coder's stop rule,
  so the downstream `/ship` planner inherits a clean decision).

Record which repo inputs you used in the briefing's header note. Codebase and web
grounding compose — use both when both are available (external evidence + internal
constraints).
