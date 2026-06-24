---
name: security-review
description: Audit code for real, exploitable vulnerabilities through an OWASP Top 10 lens — injection, broken access control, secrets, SSRF, insecure deserialization, crypto misuse — and produce a severity-rated, parseable verdict. Use when asked to security-review a change, gate a feature before merge, or audit a high-risk surface (auth, input handling, data access).
---

# Security review and hardening

A security review asks one question of every line that touches a trust boundary:
**"what can an attacker make this do?"** Not "is this clean" — clean code ships
holes all the time. You trace untrusted input to a dangerous sink, check that
authority is enforced where it's claimed, and rate what you find by how badly it
can be abused.

The output is a **gate**: a parseable verdict plus findings precise enough that
the fix is obvious. Findings must be *real* — a plausible attacker and a
plausible consequence — not style notes wearing a security badge.

## The OWASP lens — where the bugs actually are

Walk these systematically; most real findings are here:

1. **Broken access control** — the #1 category. Authentication proves *who*;
   authorization proves *allowed*. Check authz on **every** state-changing or
   data-returning path — IDOR (can user A pass user B's id?), missing role
   checks, client-trusted permissions, path traversal.
2. **Injection** — untrusted input reaching an interpreter: SQL (use
   parameterized queries, never string-built), OS command, NoSQL, LDAP, XPath,
   and **XSS** (untrusted data into HTML without escaping). Trace input → sink.
3. **Secrets & cryptographic failures** — hardcoded keys/passwords/tokens in
   code, config, or git history; secrets in logs; weak/rolled-your-own crypto;
   `http` where `https` is required; predictable tokens; passwords not hashed
   with a slow KDF (bcrypt/argon2, not MD5/SHA1).
4. **SSRF & outbound requests** — user-controlled URLs fetched server-side;
   unvalidated redirects; requests that can reach internal metadata endpoints.
5. **Insecure deserialization & unsafe parsing** — `pickle`/`yaml.load`/`eval`
   on untrusted data; XML external entities (XXE).
6. **Security misconfiguration** — debug mode on in prod, permissive CORS (`*`
   with credentials), verbose error pages leaking stack traces, default creds,
   overly broad file permissions.
7. **Input validation & resource limits** — unvalidated size/shape (DoS via huge
   payloads), missing rate limits on auth endpoints, integer/path edge cases.

## Severity rubric — exploitability × impact

| Severity | Bar |
|---|---|
| **Critical** | Remote exploit, auth bypass, RCE, or secret/PII exposure reachable by an attacker now. → `VERDICT: BLOCK` |
| **High** | Serious issue exploitable with some precondition (auth'd user escalates, stored XSS). |
| **Medium** | Real weakness, limited impact or hard precondition (info leak, weak defaults). |
| **Low / Info** | Hardening / defense-in-depth; not directly exploitable. |

Rate by what an attacker gets, **not** by how easy it is to fix. A one-line SQL
concat that dumps the user table is Critical, not Low.

## Confirm before flagging

For each candidate, verify the sink is **reachable with attacker-controlled
data** and not already mitigated upstream (a framework that auto-escapes, a
validator at the boundary). Anything you can't fully confirm goes in as **needs
manual verification** with the exact check — don't state maybes as facts. A
report full of false positives gets ignored, which is its own security failure.

## The verdict

First line of `reports/security/REPORT.md`, exactly one of:
`VERDICT: PASS` · `VERDICT: FINDINGS` · `VERDICT: BLOCK`. Then per finding:
`file:line`, severity, OWASP category, the attack, and the concrete fix.

## Checklist

- [ ] Every state-changing / data-returning path checked for **authorization**, not just login.
- [ ] Untrusted input traced to each sink (SQL, shell, HTML, FS, deserializer, outbound URL).
- [ ] Secrets scanned in code, config, and history; crypto and transport checked.
- [ ] Each finding has `file:line`, severity (by impact), category, and a concrete fix.
- [ ] Unconfirmed items marked "needs manual verification", not asserted.
- [ ] First line of the report is a parseable `VERDICT:`.

See `reference.md` for the per-category attack patterns, secret-scanning tactics,
and the anti-rationalization / red-flags / verification-gates discipline.
