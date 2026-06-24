# Code simplification — reference

The companion to `SKILL.md`. Concrete before/after patterns, and the discipline
that keeps "cleanup" from quietly changing behaviour or sprawling into a rewrite.

## Patterns worth applying

**Flatten with early returns.**
```python
# before — arrow code, the happy path is buried
def handle(req):
    if req.user:
        if req.user.active:
            if req.body:
                return process(req)
            else:
                return error("empty")
        else:
            return error("inactive")
    else:
        return error("no user")

# after — guards first, happy path last and obvious
def handle(req):
    if not req.user:        return error("no user")
    if not req.user.active: return error("inactive")
    if not req.body:        return error("empty")
    return process(req)
```
Behaviour identical; the reader sees the preconditions, then the work.

**De-duplicate toward what exists.** Two copies of the same validation → call the
canonical validator named in `REPO_CONTRACT.md`. Don't write a third, more
general validator to "unify" them — reuse the one that's already canonical.

**Delete dead code outright.** An unreachable `else`, an unused helper, a
commented-out block. Don't keep it "just in case" — git is the just-in-case.

**Collapse needless indirection.**
```python
# before — a wrapper that only forwards
def get_user_name(u): return fetch_name(u)
# after — call fetch_name directly; delete the wrapper
```
But confirm there are no other callers and no intended seam (a wrapper that
exists as a documented extension point is a fence — leave it).

**Name the boolean thicket.**
```python
# before
if (u.role == "admin" or u.role == "owner") and not u.suspended and u.verified:
# after
if u.can_manage():   # defined once on the model, reused everywhere
```

## When NOT to simplify (fences to leave standing)

- A branch with a comment like `# handle the 2019 legacy format` — load-bearing
  history you can't see in the types.
- A defensive copy before mutation — removing it aliases shared state.
- An "unnecessary" `await`/lock/ordering — concurrency correctness rarely looks
  necessary until it breaks.
- A redundant validation at a trust boundary — defense in depth is intentional.
- Anything whose only justification you can muster is "looks unnecessary."

The tell: if your reason to change it is about how it *looks* rather than what it
*does and who depends on it*, you haven't found the fence's purpose yet.

## Behaviour preservation, concretely

Same behaviour means **all** of:
- Same return values for the same inputs, including edge cases (empty, null,
  boundary).
- Same exceptions/error types raised in the same conditions.
- Same public interface — signatures, names other modules import, response shapes.
- Same observable side effects (writes, calls, logs that something asserts on).

The proof is the existing suite passing **with its assertions untouched**. If you
found yourself editing a test to keep it green, you changed behaviour — revert
the simplification or route it through `/ship` as an intentional change.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "This code looks redundant, I'll remove it." | Looks ≠ is. Find why it exists first (Chesterton's Fence) or leave it. |
| "Fewer lines is simpler." | Fewer lines can be *denser* and harder to read. Optimize for understanding, not length. |
| "I'll make it generic so it's reusable later." | YAGNI. One caller needs the concrete version. Abstract at the third repetition, not the first. |
| "I'll just fix this bug while I'm in here." | Out of scope, untested, unreviewed. Note it for `/debug`; keep cleanup behaviour-preserving. |
| "I had to tweak the test, but it's basically the same." | A changed assertion means changed behaviour. That's not a simplification anymore. |
| "It's obviously safe, I don't need to run the tests." | "Obvious" is exactly what regressions are made of. Run before and after. |

## Red flags

- A construct was removed without an articulated reason for why it was safe.
- A new abstraction appeared to serve a single caller.
- Tests were edited to stay green.
- The diff includes a behaviour change, feature, or bug fix alongside the cleanup.
- Line count dropped but the code got harder to follow.
- The suite wasn't run before and after an applied change.

## Verification gates

Before applying any change:
- [ ] The suite is green (baseline established).
- [ ] Each change has an explicit Chesterton's-Fence justification.

Before claiming "simplified":
- [ ] The **same** tests pass, assertions unchanged.
- [ ] Public interface, error types, and edge-case outputs verified unchanged.
- [ ] No feature/bugfix smuggled in; uncertain items left as proposals.
- [ ] `.pipeline/simplification.md` records each change with its safety reasoning.
