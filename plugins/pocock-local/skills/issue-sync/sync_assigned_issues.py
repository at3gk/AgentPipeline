#!/usr/bin/env python3
"""Mirror GitHub issues assigned to you into the local Pocock tracking area.

Read-only toward GitHub. The only `gh` subcommand this runs is `gh issue list`
(plus `gh --version` / `gh auth status` for preflight). It never comments,
labels, closes, or touches a Project board. See the write-back TODO at the very
bottom — it is intentionally inert.

Design (see SKILL.md):
  - Config precedence, no hardcoded repo/path:
      1. CLI flags (--repo / --dir), then
      2. env POCOCK_ISSUE_REPO / POCOCK_ISSUE_DIR, then
      3. best-effort parse of docs/agents/issue-tracker.md (the Pocock
         LOCAL-FILES config), then
      4. repo: give up and flag (never guess someone's enterprise repo);
         dir:  fall back to .scratch/issues and flag that it guessed.
  - Snapshot + notes split, per issue <dir>/<number>/:
      snapshot.md  machine-owned, OVERWRITTEN each run so the mirror tracks
                   upstream.
      notes.md     human-owned working scratch, CREATED IF ABSENT and NEVER
                   overwritten — in-progress notes are never clobbered.
  - Worktree-safe: a *relative* tracking dir is anchored at the MAIN worktree
    root (git common dir), so every linked `git worktree` shares one mirror and
    one set of notes instead of fragmenting a copy into each worktree. Pass an
    absolute --dir / POCOCK_ISSUE_DIR to pin an explicit shared location. This
    tool never creates branches or PRs, so it can't collide with your own
    branch/PR naming.
  - stdout lists what was newly pulled (and, separately, what was refreshed);
    that text lands in session context when run from a SessionStart hook.

Exit codes: 0 ok, 2 config/preflight problem (non-destructive), 1 unexpected.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_DIR = ".scratch/issues"
TRACKER_CONFIG = Path("docs/agents/issue-tracker.md")
REPO_ENV = "POCOCK_ISSUE_REPO"
DIR_ENV = "POCOCK_ISSUE_DIR"

# A GitHub owner/repo slug, optionally host-qualified for enterprise
# (e.g. github.example.com/org/repo). Kept deliberately narrow.
_SLUG_RE = re.compile(r"\b([A-Za-z0-9._-]+/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)?)\b")


def _flag(msg: str) -> None:
    """Print a one-line advisory to stderr (does not abort)."""
    print(f"issue-sync: {msg}", file=sys.stderr)


def _fail(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"issue-sync: {msg}", file=sys.stderr)
    sys.exit(code)


# --------------------------------------------------------------------------- #
# Config resolution
# --------------------------------------------------------------------------- #
def _parse_tracker_config() -> tuple[str | None, str | None]:
    """Best-effort read of docs/agents/issue-tracker.md for repo + local dir.

    Conservative: only returns a value it is reasonably confident about, so a
    malformed config degrades to env/flag rather than syncing the wrong repo.
    """
    if not TRACKER_CONFIG.is_file():
        return None, None
    repo = local_dir = None
    for raw in TRACKER_CONFIG.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        low = line.lower()
        if repo is None and "repo" in low:
            m = _SLUG_RE.search(line)
            if m and "/" in m.group(1):
                repo = m.group(1)
        if local_dir is None and ("local" in low or "scratch" in low or "path" in low):
            # a bare path token like `.scratch/issues` or `./work/issues`
            m = re.search(r"(?<![\w/])(\.?/?[\w.-]+(?:/[\w.-]+)+/?)", line)
            if m and ("/" in m.group(1)):
                cand = m.group(1)
                # avoid mistaking a repo slug for a path
                if not _SLUG_RE.fullmatch(cand.strip("/")):
                    local_dir = cand.rstrip("/")
    return repo, local_dir


def resolve_repo(cli_repo: str | None) -> str:
    if cli_repo:
        return cli_repo
    if os.environ.get(REPO_ENV):
        return os.environ[REPO_ENV].strip()
    repo, _ = _parse_tracker_config()
    if repo:
        return repo
    _fail(
        f"could not determine the issues repo. Set {REPO_ENV}=ORG/REPO "
        f"(host-qualified as HOST/ORG/REPO for GitHub Enterprise), or declare it "
        f"in {TRACKER_CONFIG}. Not guessing."
    )


def _main_worktree_root() -> Path | None:
    """Root of the MAIN worktree, shared across all linked `git worktree`s.

    `git-common-dir` points at the primary `.git` even from inside a linked
    worktree, so anchoring here keeps one mirror instead of one-per-worktree.
    """
    r = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    common = Path(r.stdout.strip())          # .../<main>/.git (or a bare dir)
    return common.parent if common.name == ".git" else None


def resolve_dir(cli_dir: str | None) -> Path:
    raw, guessed = cli_dir, False
    if raw is None:
        raw = os.environ.get(DIR_ENV, "").strip() or None
    if raw is None:
        _, raw = _parse_tracker_config()
    if raw is None:
        raw, guessed = DEFAULT_DIR, True

    path = Path(raw)
    # Anchor a relative dir at the main worktree so linked worktrees share it.
    if not path.is_absolute():
        anchor = _main_worktree_root()
        if anchor is not None:
            path = anchor / path
    if guessed:
        _flag(
            f"local tracking dir not set; defaulting to '{path}'. "
            f"Set {DIR_ENV} (or declare it in {TRACKER_CONFIG}) to override."
        )
    return path


# --------------------------------------------------------------------------- #
# gh (read-only)
# --------------------------------------------------------------------------- #
def preflight() -> None:
    if not _which("gh"):
        _fail("the GitHub CLI `gh` is not installed or not on PATH.")
    status = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True
    )
    if status.returncode != 0:
        _fail(
            "`gh` is not authenticated. Run `gh auth login` (against your "
            "enterprise host if applicable). Details:\n" + status.stderr.strip()
        )


def _which(name: str) -> str | None:
    for d in os.environ.get("PATH", "").split(os.pathsep):
        cand = Path(d) / name
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return None


def fetch_assigned(repo: str) -> list[dict]:
    """gh issue list --assignee @me (read-only). Returns parsed JSON list."""
    cmd = [
        "gh", "issue", "list",
        "--repo", repo,
        "--assignee", "@me",
        "--state", "open",
        "--json", "number,title,body,labels,url",
        "--limit", "200",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip()
        hint = ""
        if "Could not resolve" in err or "not found" in err.lower() or "HTTP 404" in err:
            hint = (
                f"\n  → check the repo slug and host. For GitHub Enterprise, "
                f"host-qualify it ({REPO_ENV}=HOST/ORG/REPO) or set GH_HOST. "
                f"Not guessing a host."
            )
        _fail(f"`gh issue list` failed for '{repo}':\n{err}{hint}")
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as e:
        _fail(f"could not parse `gh` output as JSON: {e}", code=1)


# --------------------------------------------------------------------------- #
# Mirror writing
# --------------------------------------------------------------------------- #
def _render_snapshot(issue: dict, repo: str) -> str:
    labels = ", ".join(l.get("name", "") for l in issue.get("labels", [])) or "—"
    body = (issue.get("body") or "").strip() or "_(no description)_"
    return (
        f"<!-- MACHINE-OWNED SNAPSHOT — do not edit; refreshed by issue-sync each "
        f"run. Put your own notes in notes.md (never overwritten). -->\n"
        f"# #{issue['number']} — {issue.get('title', '').strip()}\n\n"
        f"- repo: `{repo}`\n"
        f"- url: {issue.get('url', '')}\n"
        f"- labels: {labels}\n\n"
        f"---\n\n{body}\n"
    )


def _notes_stub(issue: dict) -> str:
    return (
        f"<!-- HUMAN-OWNED — your working notes for #{issue['number']}. "
        f"issue-sync created this once and will NEVER overwrite it. -->\n"
        f"# Working notes — #{issue['number']} {issue.get('title', '').strip()}\n\n"
        f"## Scope (from `grilling`)\n\n"
        f"## Plan / acceptance criteria\n\n"
        f"## Decisions & open questions\n\n"
    )


def mirror(issues: list[dict], repo: str, root: Path) -> tuple[list[int], list[int]]:
    newly, refreshed = [], []
    for issue in issues:
        num = issue["number"]
        issue_dir = root / str(num)
        is_new = not issue_dir.exists()
        issue_dir.mkdir(parents=True, exist_ok=True)

        # snapshot.md — machine-owned, always refreshed.
        (issue_dir / "snapshot.md").write_text(_render_snapshot(issue, repo), encoding="utf-8")

        # notes.md — human-owned, create-if-absent, NEVER overwrite.
        notes = issue_dir / "notes.md"
        if not notes.exists():
            notes.write_text(_notes_stub(issue), encoding="utf-8")

        (newly if is_new else refreshed).append(num)
    return newly, refreshed


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help=f"ORG/REPO (overrides {REPO_ENV} and config)")
    ap.add_argument("--dir", help=f"local tracking dir (overrides {DIR_ENV} and config)")
    ap.add_argument("--dry-run", action="store_true", help="resolve + fetch, but write nothing")
    args = ap.parse_args()

    repo = resolve_repo(args.repo)
    root = resolve_dir(args.dir)
    preflight()
    issues = fetch_assigned(repo)

    if args.dry_run:
        print(f"issue-sync (dry run): {len(issues)} assigned issue(s) in {repo}; "
              f"would mirror into {root}/")
        return 0

    newly, refreshed = mirror(issues, repo, root)

    # "What's new" — the note that lands in session context via the hook.
    if newly:
        print(f"issue-sync: {len(newly)} new issue(s) pulled into {root}/:")
        by_num = {i["number"]: i for i in issues}
        for n in newly:
            print(f"  • #{n} {by_num[n].get('title', '').strip()}")
    else:
        print(f"issue-sync: no new issues ({len(refreshed)} snapshot(s) refreshed).")
    if refreshed:
        print(f"issue-sync: refreshed snapshots for #{', #'.join(map(str, refreshed))}.")
    return 0


# --------------------------------------------------------------------------- #
# OPT-IN TODO (OFF by default — this is documentation, not live code):
# A future write-back mode could push local `notes.md` back to the issue as a
# comment. It is intentionally NOT implemented: this tool is read-only toward
# GitHub. Turning it on would be an explicit, separately-reviewed change that
# adds a `gh issue comment` path here, gated behind an off-by-default flag.
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
