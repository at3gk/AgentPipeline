---
description: Explain a file, module, or feature so you can learn it. Delegates to the read-only explainer agent.
---

Help me understand: $ARGUMENTS

Delegate to the **explainer** subagent in standalone mode, asking it to produce a learning-focused walkthrough of the target above. It should read the target and enough surrounding code to explain it in context, write the explanation to `.pipeline/explanation.md`, and give me the key points directly in the reply.

If `$ARGUMENTS` is empty, explain the most recent changes instead: run `git diff` (falling back to the last commit) and have the explainer walk me through what changed and why.

Do not modify any source code.
