# Model tiers — optional Fable upgrade

The pipeline runs on a **reason-in-Opus / generate-in-Sonnet** split by default
(see each agent's `model:` frontmatter). This file adds an **opt-in Fable tier**:
when enabled, the hardest-reasoning stages run on `claude-fable-5` — Anthropic's
most capable model — and everything else is unchanged. It is **off by default**,
so the pipeline works verbatim in any org.

## The gate (default-safe, opt-in)

The Fable tier is gated on an environment variable, following the repo
convention of *safe default, explicit opt-in*:

| `AGENT_PIPELINE_FABLE` | Behaviour |
|---|---|
| unset / `0` (default) | Every agent uses its frontmatter `model:` (Opus / Sonnet). Nothing changes. |
| `1` | The **Fable-eligible** agents below are spawned on `claude-fable-5`; all others keep their frontmatter model. |

**Why a gate and not just `model: fable` in frontmatter.** Fable is not universally
available and is ~2× Opus's price ($10/$50 vs $5/$25 per MTok). It also requires
**30-day data retention** — an org on zero-data-retention gets a `400` on *every*
Fable request. Opus therefore stays the committed default so the pipeline runs
everywhere; opting into Fable is a deliberate per-operator choice. If the override
is ignored, or Fable is unavailable, the Opus frontmatter default is the fallback —
so a wrong opt-in degrades to Opus, it does not break the run.

**Applying it.** An orchestrator command (`/ship`, `/ship-overnight`) or a
standalone command (`/debug`, `/perf`, `/code-simplify`) checks the gate once —
e.g. `printenv AGENT_PIPELINE_FABLE` — and, when it is `1`, requests
`model: claude-fable-5` as it delegates to a Fable-eligible agent (the per-spawn
model override takes precedence over the agent's frontmatter). When the gate is
unset it delegates normally.

## Fable-eligible agents (run on Fable when the gate is on)

Chosen for what Fable is documented to be best at — the most demanding reasoning,
code review and debugging, first-shot implementation of well-specified systems,
and long-horizon agentic work — where the capability gain justifies the premium:

| Agent | Why Fable earns its cost here |
|---|---|
| `planner` | The spec drives every downstream stage; better planning compounds. |
| `reviewer` | Last-line correctness + simplicity gate; the strongest catcher pays for itself. |
| `debugger` | Root-causing novel failures is the hardest reasoning, with no gate after it. |
| `simplifier` | Behaviour-preservation proofs (Chesterton's Fence) are subtle and high-stakes. |
| `perf-auditor` | Measure→diagnose→justify reasoning about why a hot path is hot. |

## Pinned to Opus — do NOT run on Fable

| Agent | Reason |
|---|---|
| `security-auditor` | **Fable is the wrong tool for security work.** Its safety classifiers target bio/cyber and **false-positive on security tooling and cyber analysis** (a benign audit can return `stop_reason: "refusal"`), and its documented bug-finding gains **explicitly exclude security-focused analysis**. Keep it on Opus. |

## Unchanged (frontmatter model stands)

- `coder`, `tester` → **Sonnet**. High-throughput generation, gated by the Opus/Fable reviewer. The tokens live here; keep them cheap.
- `cartographer`, `scout`, `explainer`, `clarifier`, `mutation-grader`, `storm-researcher` → **Opus**. Extraction, ideation, teaching, and interviewing — Fable's premium is not justified, and these run infrequently.

## Summary

```
AGENT_PIPELINE_FABLE=1  →  planner, reviewer, debugger, simplifier, perf-auditor  ⇒ claude-fable-5
                           security-auditor                                       ⇒ claude-opus-4-8 (pinned)
                           coder, tester                                          ⇒ sonnet   (unchanged)
                           cartographer, scout, explainer, clarifier,
                             mutation-grader, storm-researcher                     ⇒ opus     (unchanged)
unset (default)         →  every agent uses its frontmatter model
```
