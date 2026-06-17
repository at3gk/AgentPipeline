---
description: Autonomously take a feature from request to a pushed branch — Map, Plan, Code, Test, Review with a bounded auto-fix loop, then Explain. Built for overnight and scheduled cloud runs.
---

Autonomously ship this feature end to end, without stopping to ask me: $ARGUMENTS

You are running unattended (overnight, or in a scheduled cloud session). Make reasonable decisions and keep going. Your job is to leave a clean, pushed branch and a morning report — never to merge.

## 0. Pick the work and prepare

1. **Determine the feature.**
   - If `$ARGUMENTS` is non-empty, that is the feature.
   - If it is empty, read `FEATURES.md` at the repo root and take the **first unchecked item** (`- [ ] ...`). That is the feature. If there is no backlog file or no unchecked item, write a short note saying there was nothing to do and stop.
2. **Pre-flight.** Run `git status`. If the working tree is **not clean**, stop and report it — do not mix unrelated uncommitted changes into an autonomous run. (In a fresh cloud session the tree is always clean.) Never run on `main`/`master` as the working branch; you will create your own branch next.
3. **Create the branch.** Make and switch to `claude/overnight-<slug>-<date>`, where `<slug>` is a short kebab-case summary of the feature and `<date>` is `YYYYMMDD`. The `claude/` prefix keeps it pushable under default cloud branch-push policies. Branch from the current HEAD.
4. **Clean handoffs.** Delete any files in `.pipeline/` and recreate the empty directory.

## 1. Map (optional precursor)

If `.understand-anything/knowledge-graph.json` exists, leave it for the Planner. If it is missing or stale and the [Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) plugin is installed, run `/understand` to build a fresh codebase map first. If that plugin is not installed, skip silently.

## 2. Plan

Delegate to the **planner** subagent with the feature. Wait for `.pipeline/spec.md`.

- If the spec contains **OPEN QUESTIONS**, you cannot ask me — so make the most reasonable assumption for each, write your chosen answers into `.pipeline/spec.md` under a **"Assumptions made (unattended run)"** heading, and continue. These assumptions go in the morning report.

## 3. Build, test, review — with a bounded auto-fix loop

Run this loop. Let `ROUND = 0` and `MAX_ROUNDS = 2`.

1. Delegate to the **coder** subagent. On the first pass it implements the spec; on later passes, point it at `.pipeline/review.md` and tell it to address that feedback only. Wait for `.pipeline/changes.md`.
2. Delegate to the **tester** subagent. Wait for `.pipeline/test-results.md`.
3. Delegate to the **reviewer** subagent. Wait for `.pipeline/review.md`. Read its **first line**.
4. Decide:
   - First line is `VERDICT: SHIP` **and** tests passed → checkpoint-commit (see below) and go to step 4, Ship.
   - Otherwise, if `ROUND < MAX_ROUNDS` → checkpoint-commit the attempt, increment `ROUND`, and repeat the loop from step 1, feeding back the failures (test results and/or review feedback).
   - Otherwise (out of rounds, still not shipping) → go to step 5, Blocked.

**Checkpoint commit:** after each round, `git add -A` and commit with a message like `wip(overnight): <feature> — round <ROUND> (<verdict or test state>)`. These intermediate commits let me see how the feature came together.

## 4. Ship (verdict was SHIP)

1. Delegate to the **explainer** subagent in pipeline mode (Mode A), pointed at `.pipeline/`. Wait for `.pipeline/explanation.md`.
2. Write the morning report (see below) with status **SHIPPED**.
3. If the feature came from `FEATURES.md`, check its box (`- [ ]` → `- [x]`).
4. Final commit: `git add -A` then commit `feat(overnight): <feature>`.

## 5. Blocked (ran out of rounds)

1. Delegate to the **explainer** subagent in blocker mode (Mode C). Wait for `.pipeline/explanation.md`.
2. Write the morning report with status **BLOCKED — needs a human**, including the explainer's smallest-next-step.
3. Do **not** check off the backlog item.
4. Final commit: `git add -A` then commit `wip(overnight): <feature> — blocked, see report`. The branch still gets pushed so I can pick up where it stopped.

## 6. Finish

1. Write the morning report to a **committed** file at `reports/<branch-name>.md` (create `reports/` if needed). `.pipeline/` is gitignored, so this committed report is how the results travel with the branch — essential for cloud runs where I only see the branch. Include: status, the feature, any assumptions made, the review verdict, a short summary of what was built (or where it's stuck), the test outcome, and a one-line pointer to read `.pipeline/explanation.md` for the full walkthrough if running locally. Commit it as part of the final commit.
2. **Push** the branch: `git push -u origin <branch-name>`. If the push fails due to a network error, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).
3. **Do not open a pull request. Do not merge.** Leave the branch for my review.
4. End with a one-paragraph summary: branch name, status, and the headline of the morning report.
