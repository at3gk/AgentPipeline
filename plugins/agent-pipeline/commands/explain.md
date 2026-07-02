---
description: Explain a file, module, or feature so you can learn it. Delegates to the read-only explainer agent.
---

Help me understand: $ARGUMENTS

**Model tier (automatic — no setup).** The explainer auto-uses `claude-fable-5` when Fable is available (clearer mental models and better-chosen gotchas). Delegate with `model: claude-fable-5`; if that spawn **fails because Fable is unavailable or refused**, re-run it on its default Opus. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces Opus.) See `MODEL-TIERS.md`.

Delegate to the **explainer** subagent in standalone mode, asking it to produce a learning-focused walkthrough of the target above. It should read the target and enough surrounding code to explain it in context, write the explanation to `.pipeline/explanation.md`, and give me the key points directly in the reply.

If `$ARGUMENTS` is empty, explain the most recent changes instead: run `git diff` (falling back to the last commit) and have the explainer walk me through what changed and why.

Do not modify any source code.
