# Model tiers — Fable routes per stage (when available)

This plugin keeps model selection **simple and delegated**. Each agent carries a
sensible default in its `model:` frontmatter (the tester is Sonnet). On top of
that:

- **When `claude-fable-5` is available, the orchestrator assigns each stage the
  model that stage actually needs** — using this page as *guidance*, not a fixed
  mandate. It does **not** blanket-force Fable onto everything.
- **When Fable is unavailable, every agent uses its frontmatter default**,
  exactly as it would with no Fable at all. Nothing to configure.

## Detecting availability (no config)

Discover it from the first Fable delegation, not a probe: request
`model: claude-fable-5` on the first stage you'd route to Fable. If that spawn is
**refused/unavailable** (not accessible to the org, or a zero-data-retention
`400`), re-run that stage on its default and treat Fable as absent for the rest
of the run. If it succeeds, Fable is available to route to for the run.

Escape hatch: `POCOCK_FABLE=0` forces defaults even when Fable is available
(e.g. to cap cost on a run).

## Recommended routing (guidance)

| Stage | When Fable is available | Default |
|---|---|---|
| planning / scoping | Fable — better spec + acceptance criteria | Opus |
| tdd-tester (design tests, confirm) | usually Sonnet; Fable only for genuinely subtle test design | Sonnet |
| implement | Pocock `implement` skill — **user-typed**, runs on the session model; not routed here | — |
| review | Pocock `/code-review` skill — **user-typed**; not routed here | — |

Implementation and review lean on the Matt Pocock skills, which are
`disable-model-invocation: true` (user-typed only) and run on the session model —
this plugin composes around them and does not pick their model.

## Hard rule

Any **security-focused** analysis (if you ever add such a step) stays off Fable —
its safety classifiers false-positive on security/cyber work. Not applicable to
the default lean flow, but the pin is non-negotiable if added.
