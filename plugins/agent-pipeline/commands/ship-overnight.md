---
description: Autonomously take a feature from request to a pushed branch — Map, Plan, Code, Test, Review with a bounded auto-fix loop, then Explain. Built for overnight and scheduled cloud runs.
---

Autonomously ship this feature end to end, without stopping to ask me: $ARGUMENTS

You are running unattended (overnight, or in a scheduled cloud session). Make reasonable decisions and keep going. Your job is to leave a clean, pushed branch and a morning report — never to merge.

**Model tier (automatic — no setup).** The **planner**, **coder**, **reviewer**, and **explainer** stages run on `claude-fable-5` when Fable is available and fall back to their defaults when it isn't. Detect availability from the first eligible delegation: spawn the **planner** with `model: claude-fable-5`. If that spawn **fails because Fable is unavailable or refused** (not accessible to this org, or a zero-data-retention `400`), re-run the planner on its default and use the defaults for the coder, reviewer, and explainer this run; if it **succeeds**, use Fable for all of them. The **Tester stays Sonnet**. **Keep the security-auditor on Opus regardless** — Fable's safety classifiers false-positive on security analysis. (Optional escape hatch: `AGENT_PIPELINE_FABLE=0` forces the default tier.) See `MODEL-TIERS.md`.

## 0. Pick the work and prepare

1. **Determine the feature.**
   - If `$ARGUMENTS` references a GitHub issue (`#123`, a bare issue number, or an issue URL), fetch it with `gh issue view <n> --comments` and treat the full issue (title, body, and comments) as the feature request — pass that full text to the Planner, along with any documents the issue links (e.g. a PRD). **Remember the issue number**; you will update the issue at the end of the run.
   - Otherwise, if `$ARGUMENTS` is non-empty, that is the feature.
   - If it is empty **and** `docs/agents/issue-tracker.md` exists at the repo root (the repo tracks its backlog in GitHub Issues; labels are defined in `docs/agents/triage-labels.md`), pull from the tracker: run `gh issue list --label ready-for-agent --state open --json number,title,body,assignees,createdAt`, drop any issue that already has an assignee or an open blocker (an open issue referenced in a `Blocked by: #n` line in the body — check each referenced issue's state), and take the **oldest** remaining one. Claim it with `gh issue edit <n> --add-assignee @me`, then fetch its full text with `gh issue view <n> --comments`. That is the feature; remember the number. **Never** pull `needs-triage` or `needs-info` issues — those are ungroomed candidates, not approved work. If no issue qualifies, write a short note saying there was nothing to do and stop.
   - If it is empty and there is no `docs/agents/issue-tracker.md`, read `FEATURES.md` at the repo root and take the first unchecked item (`- [ ] ...`) under the `## Ready to build` heading (if that heading exists; otherwise the first unchecked item anywhere). That is the feature. **Never** pull from a `## Proposed` section — those are ungroomed candidates, not approved work. If there is no backlog file or no unchecked ready item, write a short note saying there was nothing to do and stop.
2. **Pre-flight.** Run `git status`. If the working tree is **not clean**, stop and report it — do not mix unrelated uncommitted changes into an autonomous run. (In a fresh cloud session the tree is always clean.) Never run on `main`/`master` as the working branch; you will create your own branch next.
3. **Create the branch.** Make and switch to `claude/overnight-<slug>-<date>`, where `<slug>` is a short kebab-case summary of the feature and `<date>` is `YYYYMMDD`. The `claude/` prefix keeps it pushable under default cloud branch-push policies. Branch from the current HEAD.
4. **Clean handoffs.** Delete any files in `.pipeline/` and recreate the empty directory.

## 1. Map (optional precursor)

If `.understand-anything/knowledge-graph.json` exists, leave it for the Planner. If it is missing or stale and the [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) plugin is installed, run `/understand` to build a fresh codebase map first. If that plugin is not installed, skip silently. If `REPO_CONTRACT.md` exists at the repo root, the Planner will read it to ground the spec in canonical patterns; do not regenerate it on an unattended run (it is meant to be committed and reviewed).

## 2. Plan

Delegate to the **planner** subagent with the feature. Wait for `.pipeline/spec.md`. (If a `.pipeline/brief.md` from a prior `/clarify` run is present, the Planner grounds the spec in it.)

- If the spec contains **OPEN QUESTIONS**, you cannot ask me — so make the most reasonable assumption for each, write your chosen answers into `.pipeline/spec.md` under a **"Assumptions made (unattended run)"** heading, and continue. These assumptions go in the morning report.

## 3. Build, test, review — with a bounded auto-fix loop

Run this loop. Let `ROUND = 0` and `MAX_ROUNDS = 2`.

1. Delegate to the **coder** subagent. On the first pass it implements the spec; on later passes, point it at `.pipeline/review.md` and tell it to address that feedback only. Wait for `.pipeline/changes.md`.
2. **Check stop-rule triggers (severity split).** Read the stop-rule triggers the coder flagged in `.pipeline/changes.md`. You are unattended, so you cannot ask me — apply this split instead:
   - **Hard block** — a new or upgraded **dependency**, a change to a **shared/public interface**, or any touch to **auth or data migrations**. Do not proceed: revert or leave the change unmade, record the trigger, and go straight to step 5, Blocked. Never silently install a dependency or alter auth.
   - **Soft** — inventing a **new convention** or **skipping a test**. Proceed, but record the choice under the **"Assumptions made (unattended run)"** heading in `.pipeline/spec.md` and call it out in the morning report.
3. Delegate to the **tester** subagent. Wait for `.pipeline/test-results.md`.
4. Delegate to the **reviewer** subagent. Wait for `.pipeline/review.md`. Read its **first line**.
5. Decide:
   - First line is `VERDICT: SHIP` **and** tests passed → checkpoint-commit (see below) and go to step 4, Ship.
   - Otherwise, if `ROUND < MAX_ROUNDS` → checkpoint-commit the attempt, increment `ROUND`, and repeat the loop from step 1, feeding back the failures (test results and/or review feedback).
   - Otherwise (out of rounds, still not shipping) → go to step 5, Blocked.

**Checkpoint commit:** after each round, `git add -A` and commit with a message like `wip(overnight): <feature> — round <ROUND> (<verdict or test state>)`. These intermediate commits let me see how the feature came together.

## 4. Ship (verdict was SHIP)

1. **Optional security gate.** If the feature touched a security-sensitive surface (auth, input handling, data access, secrets, outbound requests), delegate to the **security-auditor** subagent to audit the branch diff; it writes `reports/security/REPORT.md` with a parseable `VERDICT`. If the verdict is `BLOCK`, treat it like a failed review: if rounds remain, feed the findings back to the Coder; otherwise go to step 5, Blocked. Fold the verdict into the morning report. (Skip this for changes with no security surface.)
2. Delegate to the **explainer** subagent in pipeline mode (Mode A), pointed at `.pipeline/`. Wait for `.pipeline/explanation.md`.
3. Write the morning report (see below) with status **SHIPPED**.
4. Close out the backlog entry:
   - If the feature came from a **GitHub issue**, comment on it with the branch name and the morning-report headline (`gh issue comment <n> --body "..."`), then close it (`gh issue close <n>`). If the branch is later rejected in review, the issue gets reopened — closing here mirrors checking the box.
   - If it came from **`FEATURES.md`**, check its box (`- [ ]` → `- [x]`).
5. Final commit: `git add -A` then commit `feat(overnight): <feature>`.

## 5. Blocked (ran out of rounds)

1. Delegate to the **explainer** subagent in blocker mode (Mode C). Wait for `.pipeline/explanation.md`.
2. Write the morning report with status **BLOCKED — needs a human**, including the explainer's smallest-next-step.
3. Do **not** check off the backlog item. If the feature came from a **GitHub issue**, comment on it with the blocked headline and where it's stuck (`gh issue comment <n> --body "..."`), **remove the assignee** (`gh issue edit <n> --remove-assignee @me`), and leave the issue **open** — open and unassigned is the tracker equivalent of the unchecked box, so a future run (or a human) can pick it up.
4. Final commit: `git add -A` then commit `wip(overnight): <feature> — blocked, see report`. The branch still gets pushed so I can pick up where it stopped.

## 6. Finish

1. Write the morning report to a **committed** file at `reports/<branch-name>.md` (create `reports/` if needed). `.pipeline/` is gitignored, so this committed report is how the results travel with the branch — essential for cloud runs where I only see the branch. Include: status, the feature, any **assumptions made**, any **stop-rule triggers** that fired and how they were handled (hard-blocked vs. proceeded-with-assumption), the review verdict, a short summary of what was built (or where it's stuck), the test outcome (acceptance checks verified, plus any skipped checks or known risks from the evidence contract), and a one-line pointer to read `.pipeline/explanation.md` for the full walkthrough if running locally. Commit it as part of the final commit.
2. **Push** the branch: `git push -u origin <branch-name>`. If the push fails due to a network error, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).
3. **Do not open a pull request. Do not merge.** Leave the branch for my review.
4. End with a one-paragraph summary: branch name, status, and the headline of the morning report.
