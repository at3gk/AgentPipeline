# Repo Contract

A short, curated index of this codebase's canonical files and patterns. The
Planner reads it before writing a spec; the Coder reads it before writing code.
The point is **reuse over reinvention** — every entry points at a real file (and
ideally a real symbol) you can open right now.

Generate or refresh this file with `/map-repo`. It is meant to be **committed**
so it travels with the repo. This is a filled-in example showing the expected
shape (a hypothetical Python/FastAPI service) — replace it with your own.

> Entries are an index, not prose. Write "`src/errors.py` — raise
> `AppError(code, msg)`", not "handle errors carefully".

## Schemas & data models
- `src/models/` — Pydantic v2 models, one module per resource. Canonical: `src/models/user.py` (`User`, `UserCreate`).
- DB rows: SQLAlchemy declarative models in `src/db/tables.py` (`UserRow`).

## Validators
- Field-level: Pydantic validators on the models above; e.g. `EmailStr` + `@field_validator` in `src/models/user.py:22`.
- Cross-cutting request validation: `src/api/deps.py` dependencies (`require_json`, `valid_page`).

## Shared utils / helpers
- `src/utils/time.py` — `utcnow()`, `iso(ts)`. Use these, don't call `datetime.now()` directly.
- `src/utils/ids.py` — `new_id(prefix)` for public IDs.

## Naming conventions
- Files: `snake_case.py`. Modules named by resource (`user.py`, `order.py`).
- Functions: `snake_case`; async handlers prefixed by verb (`create_user`, `list_orders`).
- Classes: `PascalCase`; request/response models suffixed `Create` / `Out` (`UserCreate`, `UserOut`).

## Error-handling patterns
- Raise domain errors from `src/errors.py` — `AppError(code: str, message: str, status: int)`. Example: `UserNotFound` at `src/errors.py:18`.
- Never raise bare `HTTPException` in services; the handler in `src/api/errors.py:9` maps `AppError` → JSON response.

## Auth patterns
- Bearer-token auth via the `current_user` dependency in `src/api/deps.py:40`. Put `user = Depends(current_user)` on protected routes.
- Role checks: `require_role("admin")` from `src/api/deps.py:58`.

## Tests
- Framework: `pytest`. Tests live in `tests/`, mirroring `src/` (`tests/api/test_users.py`).
- Factories/fixtures: `tests/factories.py` (`make_user()`), shared fixtures in `tests/conftest.py` (`client`, `db`).
- Run: `pytest -q` (or `pytest tests/api/test_users.py -q` for one module).

## Package / dependency policy
- Current key deps: `fastapi`, `pydantic>=2`, `sqlalchemy`, `pytest`, `httpx` (test client).
- A new dependency requires a written justification of why the deps above don't cover the need. Adding one is a **stop rule** — surface it, don't just install it.

---
_Generated against commit `abc1234` on 2026-06-18. Refresh with `/map-repo` when the codebase drifts._
