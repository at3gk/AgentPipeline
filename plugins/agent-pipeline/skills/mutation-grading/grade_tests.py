#!/usr/bin/env python3
"""grade_tests.py — grade a pytest suite with mutation testing (cosmic-ray).

Mutation testing injects small faults into your code ("mutants": ``<`` -> ``<=``,
``and`` -> ``or``, ``True`` -> ``False``, deleting a statement) and reruns the
tests. A mutant the tests *catch* is **killed**; one they miss is a **survivor**
— a precise, actionable pointer to a missing assertion. Line coverage proves a
line ran; the mutation score proves a test would *fail if that line were wrong*.

This is a thin, dependency-light (stdlib-only) driver around **cosmic-ray**. It
is engine-of-choice for conventional ``src/``-layout repos whose tests import
with a package prefix (e.g. ``from src.x import y``) — mutmut 3.x's trampoline
rejects that prefix, while cosmic-ray runs your real ``pytest`` command in place.

Strategy (see SKILL.md / reference.md): scope tightly to a hand-picked allowlist
of pure-logic, deterministic, dependency-light modules; never mutate the whole
repo. Gate PRs on the diff; trend a score; ratchet a baseline of accepted
(equivalent) survivors rather than chasing 100%.

Config — a standalone ``mutation_grading.toml`` (default) or ``--config PATH``::

    [mutation_grading]
    test_command  = "python -m pytest -x -q"   # base pytest command
    timeout       = 30.0                          # per-mutant seconds
    report_path   = "reports/mutation/REPORT.md"
    trend_path    = "reports/mutation/trend.jsonl"
    baseline_path = "reports/mutation/baseline.json"
    session_dir   = ".mutation/sessions"

    [[mutation_grading.modules]]
    path  = "src/video/zoompan_presets.py"
    tests = ["tests/test_zoompan_presets.py"]    # covering tests (keep lean = fast)

Commands::

    grade_tests.py run                 # full scoped run -> report + trend
    grade_tests.py run --module src/x.py
    grade_tests.py diff --base origin/main   # PR gate: only mutate changed lines
    grade_tests.py baseline            # accept current survivors as the baseline
    grade_tests.py report              # re-render the report from existing sessions

Exit status: ``run``/``diff`` exit non-zero when a survivor appears that is not
in the baseline (the ratchet). ``baseline`` rewrites the accepted set.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

try:  # py3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - older hosts
    tomllib = None

DEFAULT_CONFIG = "mutation_grading.toml"


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
class Config:
    def __init__(self, data: dict, root: Path):
        mg = data.get("mutation_grading", data)
        self.root = root
        self.test_command = mg.get("test_command", "python -m pytest -x -q")
        self.timeout = float(mg.get("timeout", 30.0))
        self.report_path = root / mg.get("report_path", "reports/mutation/REPORT.md")
        self.trend_path = root / mg.get("trend_path", "reports/mutation/trend.jsonl")
        self.baseline_path = root / mg.get("baseline_path", "reports/mutation/baseline.json")
        self.session_dir = root / mg.get("session_dir", ".mutation/sessions")
        self.modules = []
        for m in mg.get("modules", []):
            if isinstance(m, str):
                m = {"path": m}
            self.modules.append({"path": m["path"], "tests": m.get("tests", [])})
        if not self.modules:
            raise SystemExit(
                "error: no modules configured. Add [[mutation_grading.modules]] "
                "entries (a scoped allowlist of pure-logic files) to your config."
            )


def load_config(path: Path) -> Config:
    if not path.exists():
        raise SystemExit(f"error: config not found: {path}\nSee SKILL.md for the format.")
    if tomllib is None:
        raise SystemExit("error: need Python 3.11+ (tomllib) to read TOML config.")
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    # Module paths and output paths are resolved against the working directory
    # (the repo root you invoke from), not where the config file happens to live.
    return Config(data, Path.cwd())


# --------------------------------------------------------------------------- #
# cosmic-ray driver
# --------------------------------------------------------------------------- #
def _require_cosmic_ray() -> None:
    if shutil.which("cosmic-ray") is None:
        raise SystemExit(
            "error: cosmic-ray not installed. Install with:\n"
            "  SETUPTOOLS_USE_DISTUTILS=stdlib pip install cosmic-ray\n"
            "(the stdlib flag works around a yattag/Debian build quirk on some hosts)."
        )


def _stem(path: str) -> str:
    return Path(path).stem


def _write_session_config(cfg: Config, module: dict, dest: Path) -> Path:
    tests = " ".join(module["tests"])
    test_command = cfg.test_command + (f" {tests}" if tests else "")
    toml = (
        "[cosmic-ray]\n"
        f'module-path = "{module["path"]}"\n'
        f"timeout = {cfg.timeout}\n"
        "excluded-modules = []\n"
        f'test-command = "{test_command}"\n'
        "\n[cosmic-ray.distributor]\n"
        'name = "local"\n'
    )
    dest.write_text(toml)
    return dest


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(kw.pop("cwd", None) or os.getcwd()),
                          capture_output=True, text=True, **kw)


def run_module(cfg: Config, module: dict, diff_base: str | None) -> dict:
    """Init + (filter) + exec a cosmic-ray session for one module; return parsed result."""
    _require_cosmic_ray()
    cfg.session_dir.mkdir(parents=True, exist_ok=True)
    stem = _stem(module["path"])
    toml_path = cfg.session_dir / f"{stem}.toml"
    sqlite_path = cfg.session_dir / f"{stem}.sqlite"
    if sqlite_path.exists():
        sqlite_path.unlink()
    _write_session_config(cfg, module, toml_path)

    init = _run(["cosmic-ray", "init", str(toml_path), str(sqlite_path)], cwd=cfg.root)
    if init.returncode != 0:
        raise SystemExit(f"cosmic-ray init failed for {module['path']}:\n{init.stderr}")

    if diff_base:
        # PR mode: keep only mutations on lines changed vs the base ref.
        filt = _run(["cr-filter-git", "--branch", diff_base, str(sqlite_path)], cwd=cfg.root)
        if filt.returncode != 0:  # tool/flag drift: fall back to full run, don't crash
            sys.stderr.write(f"warning: cr-filter-git skipped for {stem}: {filt.stderr.strip()}\n")

    exec_ = _run(["cosmic-ray", "exec", str(toml_path), str(sqlite_path)], cwd=cfg.root)
    if exec_.returncode != 0:
        raise SystemExit(f"cosmic-ray exec failed for {module['path']}:\n{exec_.stderr}")

    return parse_session(cfg, sqlite_path)


@lru_cache(maxsize=None)
def _annotation_union_lines(module_path: str) -> frozenset[int]:
    """Line numbers where a ``|`` sits inside a PEP-604 type annotation
    (``x: A | B``, ``-> A | B``, ``x: A | B = ...``).

    Under ``from __future__ import annotations`` the annotation is never
    evaluated, so cosmic-ray's ``ReplaceBinaryOperator_BitOr_*`` on it is an
    **equivalent mutant** that can never be killed. We exclude those from the
    score rather than nag about them forever. (A real bitwise/dict-merge ``|``
    is *not* in an annotation, so it is unaffected.)
    """
    try:
        src = Path(module_path).read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return frozenset()
    has_future = any(
        isinstance(n, ast.ImportFrom) and n.module == "__future__"
        and any(a.name == "annotations" for a in n.names)
        for n in ast.walk(tree)
    )
    if not has_future:
        return frozenset()  # union is evaluated -> mutant is real, keep it

    lines: set[int] = set()

    def collect(annotation) -> None:
        for n in ast.walk(annotation):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                lines.add(n.lineno)

    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation:
            collect(node.annotation)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            collect(node.returns)
        elif isinstance(node, ast.AnnAssign) and node.annotation:
            collect(node.annotation)
    return frozenset(lines)


def _is_equivalent_annotation_mutant(cfg: Config, mut: dict, line) -> bool:
    op = mut.get("operator_name") or ""
    if "ReplaceBinaryOperator_BitOr" not in op:
        return False
    module = mut.get("module_path")
    if not module or line is None:
        return False
    return line in _annotation_union_lines(str(cfg.root / module))


def parse_session(cfg: Config, sqlite_path: Path) -> dict:
    """Parse a cosmic-ray session via `cosmic-ray dump` (JSONL of [workitem, result])."""
    dump = _run(["cosmic-ray", "dump", str(sqlite_path)], cwd=cfg.root)
    killed = survived = incompetent = pending = equivalent = 0
    survivors = []
    for line in dump.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pair = json.loads(line)
        if not isinstance(pair, list):
            continue
        wi = pair[0]
        res = pair[1] if len(pair) > 1 else None
        mut = (wi.get("mutations") or [{}])[0]
        if res is None:  # un-executed work item
            pending += 1
            continue
        outcome = res.get("test_outcome")
        worker = res.get("worker_outcome")
        if worker == "timeout":
            killed += 1
        elif outcome == "killed":
            killed += 1
        elif outcome == "survived":
            line = (mut.get("start_pos") or [None])[0]
            if _is_equivalent_annotation_mutant(cfg, mut, line):
                equivalent += 1   # PEP-604 annotation union -> can't be killed
                continue
            survived += 1
            survivors.append({
                "module": mut.get("module_path"),
                "line": line,
                "operator": mut.get("operator_name"),
                "function": mut.get("definition_name"),
            })
        else:  # incompetent / no-test / skipped -> excluded from the score
            incompetent += 1
    scored = killed + survived
    score = round(100.0 * killed / scored, 1) if scored else 100.0
    return {
        "killed": killed, "survived": survived, "incompetent": incompetent,
        "equivalent": equivalent, "pending": pending,
        "total": killed + survived + incompetent + equivalent,
        "score": score, "survivors": survivors,
    }


# --------------------------------------------------------------------------- #
# Baseline (ratchet + equivalent-mutant ignore-list)
# --------------------------------------------------------------------------- #
def survivor_sig(s: dict) -> str:
    return f"{s['module']}::{s['line']}::{s['operator']}"


def load_baseline(cfg: Config) -> set[str]:
    if cfg.baseline_path.exists():
        data = json.loads(cfg.baseline_path.read_text())
        return set(data.get("accepted", []))
    return set()


def save_baseline(cfg: Config, survivors: list[dict]) -> None:
    cfg.baseline_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": "Accepted (equivalent or knowingly-tolerated) survivors. "
                    "New survivors NOT listed here fail the ratchet. Re-run "
                    "`grade_tests.py baseline` to accept the current set.",
        "accepted": sorted(survivor_sig(s) for s in survivors),
    }
    cfg.baseline_path.write_text(json.dumps(payload, indent=2) + "\n")


# --------------------------------------------------------------------------- #
# Report + trend
# --------------------------------------------------------------------------- #
def write_report(cfg: Config, per_module: dict, baseline: set[str]) -> dict:
    all_survivors = [s for r in per_module.values() for s in r["survivors"]]
    killed = sum(r["killed"] for r in per_module.values())
    survived = sum(r["survived"] for r in per_module.values())
    incompetent = sum(r["incompetent"] for r in per_module.values())
    equivalent = sum(r.get("equivalent", 0) for r in per_module.values())
    scored = killed + survived
    score = round(100.0 * killed / scored, 1) if scored else 100.0
    new_survivors = [s for s in all_survivors if survivor_sig(s) not in baseline]

    lines = [
        "# Mutation grading report",
        "",
        f"_Generated {date.today().isoformat()} · engine: cosmic-ray · "
        "a **scoped** score over the allowlist below — a biased estimate of the "
        "whole suite, read it as such._",
        "",
        "## Overall (scoped)",
        "",
        f"- **Mutation score: {score}%**  (killed {killed} / {scored} scored mutants)",
        f"- Survivors: {survived}  ·  of which **new (not in baseline): {len(new_survivors)}**",
        f"- Excluded: {incompetent} incompetent/no-test · "
        f"{equivalent} equivalent (PEP-604 annotation `|`, auto-detected)",
        "",
        "| Module | Score | Killed | Survived | New |",
        "|---|---:|---:|---:|---:|",
    ]
    for path, r in sorted(per_module.items()):
        nnew = sum(1 for s in r["survivors"] if survivor_sig(s) not in baseline)
        lines.append(f"| `{path}` | {r['score']}% | {r['killed']} | {r['survived']} | {nnew} |")

    lines += ["", "## Survivors — each is a missing assertion", ""]
    if not all_survivors:
        lines.append("None. Every mutant was killed. 🎯")
    else:
        lines.append(
            "Each row is a fault no test caught. Read it as: _\"no test failed "
            "when this operator was mutated → add an assertion that pins the "
            "behaviour.\"_ Survivors marked **(baseline)** are accepted "
            "(usually equivalent mutants).")
        lines += ["", "| New? | Module:Line | Function | Mutated operator |",
                  "|---|---|---|---|"]
        for s in sorted(all_survivors, key=survivor_sig):
            tag = "🆕" if survivor_sig(s) not in baseline else "(baseline)"
            fn = f"`{s['function']}()`" if s["function"] else "_module-level_"
            lines.append(f"| {tag} | `{s['module']}:{s['line']}` | {fn} | `{s['operator']}` |")

    lines += ["", "## How to act", "",
              "1. For each 🆕 survivor, add/strengthen an assertion in its covering "
              "test so the mutated operator would fail.",
              "2. If a survivor is a genuine **equivalent mutant** (e.g. an "
              "`except ImportError` fallback, a log-only branch) it cannot be "
              "killed — accept it with `grade_tests.py baseline`.",
              "3. Re-run to confirm the score moved and no 🆕 survivors remain.",
              ""]

    cfg.report_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.report_path.write_text("\n".join(lines))

    # trend
    cfg.trend_path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"date": date.today().isoformat(), "score": score, "killed": killed,
           "survived": survived, "new_survivors": len(new_survivors),
           "modules": len(per_module)}
    with open(cfg.trend_path, "a") as fh:
        fh.write(json.dumps(rec) + "\n")

    return {"score": score, "new_survivors": new_survivors, "all_survivors": all_survivors}


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_run(cfg: Config, args) -> int:
    modules = cfg.modules
    if args.module:
        modules = [m for m in cfg.modules if m["path"] == args.module]
        if not modules:
            raise SystemExit(f"error: {args.module} is not in the configured allowlist.")
    diff_base = getattr(args, "base", None)
    per_module = {}
    for m in modules:
        print(f"• mutating {m['path']} ...", file=sys.stderr)
        per_module[m["path"]] = run_module(cfg, m, diff_base)
    baseline = load_baseline(cfg)
    summary = write_report(cfg, per_module, baseline)
    n_new = len(summary["new_survivors"])
    print(f"\nMutation score (scoped): {summary['score']}%  ·  "
          f"new survivors: {n_new}  ·  report: {cfg.report_path}")
    if n_new:
        print("FAIL: new survivors not in baseline (ratchet). See the report; add "
              "assertions or accept equivalents with `baseline`.", file=sys.stderr)
        return 1
    return 0


def cmd_baseline(cfg: Config, args) -> int:
    per_module = {}
    for m in cfg.modules:
        print(f"• mutating {m['path']} ...", file=sys.stderr)
        per_module[m["path"]] = run_module(cfg, m, None)
    survivors = [s for r in per_module.values() for s in r["survivors"]]
    save_baseline(cfg, survivors)
    write_report(cfg, per_module, {survivor_sig(s) for s in survivors})
    print(f"Baseline written with {len(survivors)} accepted survivor(s): {cfg.baseline_path}")
    return 0


def cmd_report(cfg: Config, args) -> int:
    per_module = {}
    for m in cfg.modules:
        sqlite_path = cfg.session_dir / f"{_stem(m['path'])}.sqlite"
        if sqlite_path.exists():
            per_module[m["path"]] = parse_session(cfg, sqlite_path)
    if not per_module:
        raise SystemExit("error: no existing sessions. Run `grade_tests.py run` first.")
    summary = write_report(cfg, per_module, load_baseline(cfg))
    print(f"Re-rendered report ({summary['score']}%): {cfg.report_path}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Grade a pytest suite with mutation testing.")
    p.add_argument("--config", default=DEFAULT_CONFIG, help=f"config TOML (default {DEFAULT_CONFIG})")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="full scoped run -> report + trend (ratchets on baseline)")
    pr.add_argument("--module", help="run a single configured module")

    pd = sub.add_parser("diff", help="PR gate: mutate only lines changed vs --base")
    pd.add_argument("--base", default="origin/main", help="base ref (default origin/main)")
    pd.add_argument("--module", help="run a single configured module")

    sub.add_parser("baseline", help="accept current survivors as the baseline ignore-list")
    sub.add_parser("report", help="re-render the report from existing sessions")

    args = p.parse_args(argv)
    cfg = load_config(Path(args.config))
    if args.cmd == "run":
        return cmd_run(cfg, args)
    if args.cmd == "diff":
        return cmd_run(cfg, args)
    if args.cmd == "baseline":
        return cmd_baseline(cfg, args)
    if args.cmd == "report":
        return cmd_report(cfg, args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
