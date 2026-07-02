# Model tiers — automatic Fable upgrade

The pipeline runs on a **reason-in-Opus / generate-in-Sonnet** split by default
(see each agent's `model:` frontmatter). On top of that, the hardest-reasoning
stages **automatically run on `claude-fable-5` — Anthropic's most capable model —
whenever Fable is available, and silently fall back to their default model when it
isn't.** No flags, no setup: run the command as normal and it does the right thing.

## Auto-detection (no config)

An orchestrator command (`/ship`, `/ship-overnight`) or a standalone command
(`/debug`, `/perf`, `/code-simplify`) resolves Fable availability **once per run,
by attempting the first Fable-eligible delegation on Fable and watching the
result** — no separate probe call:

1. When delegating to the **first** Fable-eligible stage, request
   `model: claude-fable-5` (the per-spawn model override takes precedence over the
   agent's frontmatter).
2. **If that delegation fails because Fable is unavailable** — the model isn't
   accessible to this org, or the request is refused for data-retention reasons
   (Fable requires 30-day retention; a zero-data-retention org gets a `400`) —
   re-run that same stage on its **default** model, record that Fable is
   unavailable for the rest of this run, and delegate every remaining stage
   normally. The run continues seamlessly; the only cost is one failed-then-retried
   spawn on the first eligible stage.
3. **If it succeeds**, Fable is available: use `claude-fable-5` for every
   Fable-eligible stage this run.

So availability is discovered from the first real delegation, not a config value —
"use Fable if it's there, otherwise default back" happens on its own. Because Opus
stays the committed frontmatter default, the fallback path is always safe: a
Fable-less environment degrades to today's Opus/Sonnet behaviour with no error.

**Optional override (not required).** If you ever want to *force* the default
tier — e.g. to cap cost on a run even though Fable is available — set
`AGENT_PIPELINE_FABLE=0`, and the commands skip the Fable attempt entirely.
Unset (the normal case) means auto-detect. There is nothing to set to *get* Fable;
it's automatic.

## Fable-eligible agents (auto-run on Fable when it's available)

Chosen for what Fable is documented to be best at — the most demanding reasoning,
code review and debugging, first-shot implementation of well-specified systems,
and long-horizon agentic work — where the capability gain justifies the premium:

| Agent | Why Fable earns its cost here |
|---|---|
| `planner` | The spec drives every downstream stage; better planning compounds. |
| `coder` | First-shot implementation of a well-specified spec is Fable's headline strength. It is Sonnet by default (throughput, gated by review); the tier only fires once the operator has accepted Fable's premium, so the cost reason to keep it cheap no longer applies — Sonnet → Fable is the biggest single-stage quality jump available. |
| `reviewer` | Last-line correctness + simplicity gate; the strongest catcher pays for itself. |
| `debugger` | Root-causing novel failures is the hardest reasoning, with no gate after it. |
| `simplifier` | Behaviour-preservation proofs (Chesterton's Fence) are subtle and high-stakes. |
| `perf-auditor` | Measure→diagnose→justify reasoning about why a hot path is hot. |

## Pinned to Opus — do NOT run on Fable

| Agent | Reason |
|---|---|
| `security-auditor` | **Fable is the wrong tool for security work.** Its safety classifiers target bio/cyber and **false-positive on security tooling and cyber analysis** (a benign audit can return `stop_reason: "refusal"`), and its documented bug-finding gains **explicitly exclude security-focused analysis**. Keep it on Opus. |

## Unchanged (frontmatter model stands)

- `tester` → **Sonnet**. High-volume test generation, gated by the Opus `mutation-grader`. The tokens live here; keep them cheap. (`coder` is Sonnet by default too, but is Fable-eligible — see the table above.)
- `cartographer`, `scout`, `explainer`, `clarifier`, `mutation-grader`, `storm-researcher` → **Opus**. Extraction, ideation, teaching, and interviewing — Fable's premium is not justified, and these run infrequently.

## Summary

```
Fable available (auto)  →  planner, coder, reviewer, debugger,
                             simplifier, perf-auditor                              ⇒ claude-fable-5
                           security-auditor                                       ⇒ claude-opus-4-8 (pinned)
                           tester                                                 ⇒ sonnet
                           cartographer, scout, explainer, clarifier,
                             mutation-grader, storm-researcher                     ⇒ opus
Fable unavailable       →  every agent uses its frontmatter model (coder/tester Sonnet, rest Opus)
  (auto-fallback)            — discovered from the first eligible delegation, no error
Force default: AGENT_PIPELINE_FABLE=0 (optional; caps cost even when Fable is available)
```
