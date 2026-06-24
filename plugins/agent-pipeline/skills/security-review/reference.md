# Security review and hardening — reference

The companion to `SKILL.md`. Per-category attack patterns to look for, how to
scan for secrets, and the discipline that keeps a review from being either a
rubber stamp or a wall of false positives.

## Tracing input to sink

Almost every injection/XSS/SSRF finding is the same shape: **untrusted source →
no sanitization → dangerous sink.** Build the map:

- **Sources** (attacker-controlled): request params/body/headers/cookies, URL
  path segments, file uploads, query strings, env vars in some contexts, and —
  often forgotten — **responses from third-party services** and data read back
  from the database that was attacker-influenced earlier (stored XSS).
- **Sinks** (dangerous): SQL/ORM raw queries, `os.system`/`subprocess` with
  shell, `eval`/`exec`, template rendering into HTML, filesystem paths,
  deserializers (`pickle`, `yaml.load`, XML), outbound HTTP URLs, redirects.
- **Finding** = a source reaching a sink with no escaping/parameterization/
  validation between them. Read the path; don't assume a framework saves you —
  confirm it does.

## Per-category patterns

**Access control (check first, it's the most common real bug).**
- IDOR: `GET /orders/{id}` that loads by id without checking the id belongs to
  the caller. Look for object lookups keyed on a request param with no ownership
  filter.
- Missing function-level authz: an admin action whose only guard is that the UI
  doesn't show the button.
- Trusting client-supplied role/permission fields.
- Path traversal: user input in a file path without normalization (`../`).

**Injection.**
- SQL built with string concatenation / f-strings instead of parameters.
- `subprocess` with `shell=True` and interpolated input.
- HTML built by concatenation, or a template with autoescape disabled.

**Secrets & crypto.**
- Grep history and tree for high-entropy strings and obvious names:
  `password`, `secret`, `api[_-]?key`, `token`, `BEGIN PRIVATE KEY`,
  `AKIA[0-9A-Z]{16}` (AWS). Check config files and committed `.env`.
- Passwords hashed with MD5/SHA1/SHA256-plain instead of bcrypt/scrypt/argon2.
- Home-rolled crypto, ECB mode, static IVs, predictable/sequential tokens.
- Secrets written to logs or error responses.

**SSRF / outbound.** User-controlled URL passed to an HTTP client; no allowlist;
reachable internal addresses (169.254.169.254, localhost, RFC1918).

**Deserialization / parsing.** `pickle.loads`, `yaml.load` (vs `safe_load`),
`eval`/`exec` on untrusted data; XML parser with external entities enabled.

**Misconfiguration.** `DEBUG=True`, `CORS allow_origin="*"` with credentials,
stack traces returned to clients, default admin creds, broad file perms.

## Severity, applied

The mistake to avoid is rating by fix-effort. Examples rated by *impact*:

- `f"SELECT ... WHERE id = {request.args['id']}"` → **Critical** (BLOCK): trivial
  data exfiltration / auth bypass. One-line fix, still Critical.
- Stored XSS in a comment field rendered to other users → **High**.
- Verbose 500 page leaking a stack trace with file paths → **Medium**.
- Missing `SameSite` on a non-session cookie → **Low/Info**.

A single Critical (or directly exploitable High) means `VERDICT: BLOCK`.

## False positives are a failure too

A review that cries wolf gets muted, and the real finding dies with it. So:
confirm reachability, account for upstream mitigations, and when you're not sure,
say "needs manual verification: run X to confirm" instead of asserting a breach.
Precision is part of the job, not a softening of it.

## Anti-rationalizations

| Excuse | Reality |
|---|---|
| "It's an internal endpoint, no attacker can reach it." | Internal is one SSRF, one compromised account, one misconfig away. Defense in depth assumes the perimeter fails. |
| "The input comes from our own frontend." | Anyone can craft the request directly. The frontend is not a trust boundary. |
| "We validate it on the client." | Client validation is UX, not security. Re-validate on the server. |
| "It's just an internal tool / low traffic." | Impact, not popularity, sets severity. Internal tools hold the keys. |
| "We'll add auth later." | "Later" ships. An unauthenticated state-changing endpoint is a finding now. |
| "The framework probably escapes that." | Probably isn't a control. Confirm the escaping happens on this path, or flag it. |
| "Rolling our own crypto is fine, it's simple." | It isn't, and it never is. Flag any non-standard crypto. |

## Red flags

- The review reports only style/naming and no trust-boundary analysis.
- Authentication was checked but **authorization** wasn't.
- A finding has no `file:line` or no concrete attack — it's a vibe, not a finding.
- Severity was assigned by how hard the fix is.
- The report asserts vulnerabilities that were never confirmed reachable.
- No verdict line, or a verdict that doesn't match the findings (Critical + PASS).

## Verification gates

Before writing the verdict:
- [ ] Every changed state-changing / data-returning path was checked for authz.
- [ ] Each injection/XSS/SSRF candidate was traced source→sink and confirmed reachable.
- [ ] Secrets scanned across code, config, and history.
- [ ] Each finding: `file:line` + severity-by-impact + category + concrete fix.
- [ ] Unconfirmed items labelled "needs manual verification".
- [ ] First line of `reports/security/REPORT.md` is a parseable `VERDICT:` consistent with the findings.
