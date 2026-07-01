---
description: Read-only security audit of the branch changes (or a named scope) through an OWASP lens, writing a parseable VERDICT and a findings report to reports/security/REPORT.md.
---

Security review: $ARGUMENTS

**Model tier.** The security-auditor is **pinned to Opus** — do not run it on Fable even when `AGENT_PIPELINE_FABLE` is `1`. Fable's safety classifiers false-positive on security/cyber work (a benign audit can come back as a `refusal`), and its bug-finding gains exclude security-focused analysis. See `MODEL-TIERS.md`.

Delegate to the **security-auditor** subagent. Ask it to read the bundled
`security-review` skill, then audit for real, exploitable issues — not style.

Scope:
- If `$ARGUMENTS` is empty, review **this branch's diff vs the default branch**
  (`git diff` against `main`/`master`), the same way the pipeline Reviewer reads
  the diff. This is the common case: gate a feature before merge.
- If `$ARGUMENTS` names a path, module, or area, scope the audit there.
- If `$ARGUMENTS` is `full` or `repo`, audit the whole codebase's high-risk
  surfaces (auth, input handling, secrets, data access).

The auditor is **read-only** — it does not edit code. It writes
`reports/security/REPORT.md` whose **first line is a machine-readable verdict**:

- `VERDICT: PASS` — no findings above the noted threshold.
- `VERDICT: FINDINGS` — issues to fix, each with `file:line`, severity, and the fix.
- `VERDICT: BLOCK` — a critical/exploitable issue; do not ship until fixed.

When it finishes, show me the verdict and the highest-severity finding first.
This composes with `/ship`: run it after the Review stage for security-sensitive
features as an extra gate. It never merges and never fixes — fixes go through
`/ship` or `/debug`.
