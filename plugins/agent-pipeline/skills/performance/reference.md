# Performance optimization — reference

The companion to `SKILL.md`. How to get a trustworthy measurement, the
optimization catalogue ordered by typical payoff, and the discipline that keeps
"faster" honest.

## Getting a measurement you can trust

- **Measure a realistic workload.** A 10-element input won't reveal the O(n²)
  that hurts at 10k. Use representative size and shape.
- **Profile, don't guess.** CPU: `python -m cProfile -s cumtime script.py`, or
  `py-spy top --pid <pid>` for a live process. Wall clock: `time`, `timeit`, or a
  small benchmark loop. DB: turn on query logging and count queries per request.
  Memory: `tracemalloc` / a memory profiler.
- **Control the environment.** Warm vs cold caches, other load, debug builds, and
  logging all skew results. Measure before and after the *same* way, same input,
  same machine state. Run a few times; watch the variance.
- **Record the command and the number.** "~40% faster" with no command is not
  evidence. `before: 1.83s, after: 1.10s, via `python -m timeit ...`` is.

## Optimization catalogue (roughly by payoff)

1. **Fix the algorithm / data structure.** The biggest, most durable wins.
   - Membership test in a loop over a `list` (O(n)) → `set`/`dict` (O(1)). Turns
     O(n²) into O(n).
   - Sorting once instead of repeatedly; using a heap for top-k; precomputing an
     index/map instead of repeated linear scans.
2. **Kill N+1 queries.** One query in a loop over rows → a single batched query,
   `JOIN`, or `IN (...)` / `prefetch`. Often 10–100× on real workloads.
3. **Hoist and memoize repeated work.** Move loop-invariant computation out of
   the loop; cache a pure expensive result (with a clear invalidation story).
4. **Batch I/O.** Coalesce per-item network/disk/syscalls into one call. Stream
   instead of buffering huge results.
5. **Reduce allocation churn.** Avoid building large intermediate lists where a
   generator works; reuse buffers in hot loops. (Lower priority; measure that it
   matters.)
6. **Micro-optimizations last.** Local variable caching, avoiding attribute
   lookups in tight loops — small, often readability-negative, only with a number.

## When the answer is "don't"

Sometimes the right outcome of a perf audit is **no change**:

- The hot path is already optimal for the workload.
- The slow thing runs rarely / off the critical path (Amdahl says it won't
  matter).
- The only available speedup badly hurts readability for a few percent.
- You can't measure it in this environment — report the gap, don't guess.

Reporting "measured, and it's not worth changing" is a successful audit. A
clarity-destroying change for an unmeasured gain is the failure.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "This loop is obviously the slow part." | Obvious is wrong about half the time. Profile before you touch it. |
| "This is clearly faster, I don't need to benchmark it." | Then the benchmark is free and confirms you. Without it, you might have made it slower. |
| "Let me optimize this while I'm here." | Optimizing a cold path adds complexity for zero user-visible gain. Measure that it's hot first. |
| "Caching will fix it." | Caching adds invalidation bugs. Do the algorithmic fix first; cache only with a measured need and a clear invalidation story. |
| "It's a micro-optimization but every bit counts." | Not if it's 2% of runtime and costs readability. Amdahl's law says spend effort on the 80%. |
| "The numbers moved, ship it." | Same input, same way, behaviour preserved, tests green? A faster wrong answer isn't faster. |

## Red flags

- Code was changed before anything was measured.
- "Faster" is claimed with one number, or none, or different inputs before/after.
- The optimized function is a small fraction of total runtime.
- Readability dropped sharply for a single-digit-percent gain.
- A cache was added before the algorithmic cause was addressed.
- Tests weren't run, or behaviour/edge cases changed to hit the number.

## Verification gates

Before optimizing:
- [ ] A baseline number exists, taken on a realistic workload, with the command recorded.
- [ ] The bottleneck is identified from profile data, and it's actually hot (Amdahl).

Before claiming "faster":
- [ ] A measured before→after on the same workload, same method.
- [ ] Tests green; behaviour and edge cases unchanged.
- [ ] Any readability cost is named and justified by the measured gain.
- [ ] `reports/perf/REPORT.md` records the baseline, bottleneck, cause, and numbers.
