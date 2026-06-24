---
name: performance
description: Speed up code the disciplined way — measure first to find the real bottleneck, diagnose why it's hot, then optimize only what a before/after number justifies, keeping behaviour intact. Use when asked to make something faster, profile a slow path, fix a latency/throughput/memory problem, or audit performance. Refuses to optimize without a measurement.
---

# Performance optimization

> "Premature optimization is the root of all evil." — Knuth

The expensive mistake in performance work is not slow code; it's **fast guessing**
— rewriting the function you *assume* is slow, trading clarity for a change that
moves a number you never measured. This skill inverts that: **measure first,
optimize the proven bottleneck, prove the gain.** The rule is short — *no number,
no change.*

## Why measure first

Programmer intuition about where time goes is famously wrong. Time concentrates
in a few hot spots; everything else is rounding error. Two laws govern the work:

- **Amdahl's law.** Speeding up code that's 5% of runtime by 10× saves ~4.5%
  total. Speeding up the 80% hot path by 2× saves 40%. **Find the 80%.**
- **The 90/10 rule.** ~90% of time is in ~10% of the code. Optimizing the other
  90% of the code is wasted effort that just makes it harder to read.

So you cannot know what to optimize until you measure. A change without a baseline
isn't an optimization — it's a hopeful edit.

## The loop

1. **Baseline.** Pick a **realistic workload** and measure it before touching
   anything: `cProfile`/`py-spy` for CPU, `time`/a benchmark for wall clock,
   query logs for DB, a memory profiler for allocations — whatever fits the stack
   and is at hand. Record concrete numbers and the exact command, so "after" is
   comparable. Can't measure it? Report what's needed; don't optimize blind.
2. **Locate.** Read the profile, not your hunch. Name the hot path from the data.
3. **Diagnose the cause** (this dictates the fix):
   - **Algorithmic** — O(n²) where O(n) or O(n log n) exists; the biggest wins
     live here, not in micro-tweaks.
   - **N+1 queries** — a query per row instead of one batched query/join. Classic,
     huge, common.
   - **Repeated work** — recomputing inside a loop what could be hoisted or
     memoized.
   - **I/O / allocation in a tight loop** — syscalls, network, or object churn
     where one batched op would do.
4. **Optimize, then re-measure.** Apply highest value-to-risk first. Measure
   **after** on the *same* workload, the *same* way. Keep only changes with a
   real measured win; revert the rest. Run the tests — behaviour must be unchanged.

## Correctness and clarity are constraints, not afterthoughts

- **A faster wrong answer is not faster.** The optimization must preserve
  behaviour and edge cases; the suite stays green.
- **Readability is a real cost.** Prefer the algorithmic win (better data
  structure, batched query) over clever micro-optimizations that obscure the
  code. If a change hurts readability, the measured gain has to justify it — and
  you state the trade.
- **Cache last, and carefully.** Caching adds invalidation bugs. Reach for it
  after the algorithmic fixes, not before.

## Checklist

- [ ] Baseline measured on a realistic workload, with the command recorded.
- [ ] Bottleneck identified from profile data, not intuition.
- [ ] Cause diagnosed (algorithmic / N+1 / repeated work / I/O) before fixing.
- [ ] Each applied change has a **measured** before→after on the same workload.
- [ ] Changes with no measured win were reverted.
- [ ] Tests green; behaviour and edge cases preserved.
- [ ] Readability cost named where a change traded clarity for speed.

See `reference.md` for profiling tactics, the optimization catalogue, and the
anti-rationalization / red-flags / verification-gates discipline.
