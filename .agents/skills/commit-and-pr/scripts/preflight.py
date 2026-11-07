#!/usr/bin/env python3
"""Pre-send checklist for the commit-and-pr skill. Read-only: it never stages, commits or pushes.

Usage (from anywhere inside the repository):
  python3 preflight.py [--base main] [--paths <prefix> ...] [--run-checks]

  --base         the branch the PR will target (default: main), used only for the report
  --paths        limit the check to files under these path prefixes (the task's files); default: every change
  --run-checks   run the e-commerce project's checkers when the change touches specs, schema or tests

Prints the branch, the files grouped by area, and every finding. Exit code 1 when something blocks the
commit (on main/master, a secret-looking line, build output, a file over 1 MB, a whitespace error, or a
failing project checker). Exit code 0 means "nothing blocks"; the choice of files is still yours.
"""
import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys

MAX_BYTES = 1024 * 1024
JUNK = re.compile(r"(^|/)(bin|obj|node_modules|__pycache__|\.venv|dist|\.idea)/|\.pyc$|(^|/)\.DS_Store$|\.log$")
SECRETS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("JWT bearer token", re.compile(r"Bearer\s+[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("assigned secret", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"][^'\"\s<>{}$]{8,}['\"]")),
]
SPEC_AREAS = ("e-commerce/doc/api/", "e-commerce/doc/schema/", "e-commerce/db/migrations/", "e-commerce/db/tests/", "e-commerce/db/er-diagram.drawio")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git_lines(*args):
    out = run(["git", *args]).stdout
    return [l for l in out.split("\n") if l]


def changed_files():
    tracked = git_lines("diff", "--name-only", "HEAD")
    untracked = git_lines("ls-files", "--others", "--exclude-standard")
    return sorted(set(tracked)), sorted(set(untracked))


def is_text(path):
    try:
        with open(path, "rb") as f:
            return b"\0" not in f.read(8192)
    except OSError:
        return False


def area(path):
    parts = path.split("/")
    return "/".join(parts[:3]) if len(parts) > 3 else "/".join(parts[:-1]) or "."


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="main")
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--run-checks", action="store_true")
    args = ap.parse_args()

    root = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    if not root:
        sys.exit("not inside a git repository")
    os.chdir(root)
    blockers, notes = [], []

    branch = run(["git", "branch", "--show-current"]).stdout.strip() or "(detached HEAD)"
    print(f"branch: {branch}   base: {args.base}")
    if branch in ("main", "master"):
        blockers.append(f"on {branch}: create a branch first (<type>/<topic>)")

    root_path = os.path.realpath(root)
    workspace_parent = os.path.dirname(root_path)
    inferred_agent = os.path.basename(root_path) if os.path.basename(workspace_parent) == ".workspace" else ""
    configured_agent = run(["git", "config", "--get", "agent.name"]).stdout.strip()
    configured_host = run(["git", "config", "--get", "agent.workspaceHost"]).stdout.strip()
    managed_agent = inferred_agent or configured_agent
    if configured_agent and not inferred_agent:
        blockers.append("agent identity marker exists outside a managed .workspace/<agent> path")
    if configured_host and not inferred_agent:
        blockers.append("workspace host marker exists outside a managed .workspace/<agent> path")
    if inferred_agent:
        helper = ".agents/skills/agent-workspace/scripts/agent_workspace.py"
        if not os.path.isfile(helper):
            blockers.append("managed workspace is missing the agent-workspace delivery checker")
        else:
            checked = run(
                [
                    sys.executable,
                    helper,
                    "delivery-check",
                    "--agent",
                    managed_agent,
                ]
            )
            if checked.returncode != 0:
                try:
                    reason = json.loads(checked.stderr).get("reason", checked.stderr.strip())
                except (json.JSONDecodeError, AttributeError):
                    reason = checked.stderr.strip() or checked.stdout.strip()
                blockers.append(f"managed assignment delivery check failed: {reason}")
            else:
                notes.append(f"managed assignment delivery authorized for {managed_agent}")

    tracked, untracked = changed_files()
    files = tracked + untracked
    if args.paths:
        files = [f for f in files if any(f == p or f.startswith(p.rstrip("/") + "/") for p in args.paths)]
    present = [f for f in files if os.path.isfile(f)]
    deleted = [f for f in files if not os.path.exists(f)]
    print(f"\nfiles in scope: {len(files)} ({len(deleted)} deleted, {len(untracked)} untracked in the repo)")
    groups = {}
    for f in files:
        groups.setdefault(area(f), []).append(f)
    for g in sorted(groups):
        print(f"  {len(groups[g]):4d}  {g}")
    if not files:
        notes.append("nothing to commit in scope")

    for f in present:
        if JUNK.search(f):
            blockers.append(f"build output or junk: {f}")
        elif os.path.getsize(f) > MAX_BYTES:
            blockers.append(f"over 1 MB ({os.path.getsize(f) // 1024} KB): {f}")
        elif is_text(f):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    for label, rx in SECRETS:
                        if rx.search(line):
                            blockers.append(f"possible secret ({label}) at {f}:{n}")
                            break

    ws = []
    for f in present:
        if f in untracked:
            if is_text(f):
                # --no-index exits 1 whenever the files differ, so judge by the warnings it prints
                r = run(["git", "diff", "--no-index", "--check", "--", "/dev/null", f])
                if r.stdout.strip():
                    ws.append(f)
        else:
            r = run(["git", "diff", "--check", "HEAD", "--", f])
            if r.returncode != 0:
                ws.append(f)
    for f in ws:
        blockers.append(f"git diff --check reports whitespace errors: {f}")

    needs_checks = any(f.startswith(SPEC_AREAS) for f in files)
    if needs_checks:
        notes.append("the change touches specs, schema, migrations, tests or the ER diagram: the project checkers are required")
        if args.run_checks:
            blockers.extend(run_project_checks())
        else:
            notes.append("checkers not run here; re-run with --run-checks or run them by hand and paste the results")

    print("\n-- notes --" if notes else "")
    for n in notes:
        print("  " + n)
    print("\n-- blockers --" if blockers else "\nno blockers found")
    for b in blockers:
        print("  BLOCK " + b)
    sys.exit(1 if blockers else 0)


def run_project_checks():
    blockers = []
    check = "e-commerce/db/tests/check_docs.py"
    if not os.path.exists(check):
        return ["project checkers not found at " + check]
    # A file that does not parse lists no sub-commands, which used to read as "0/0 OK": say it first and stop here.
    try:
        ast.parse(open(check, encoding="utf-8").read(), check)
    except SyntaxError as error:
        return [f"{check} does not parse (line {error.lineno}: {error.msg}): no project checker can run"]
    listing = run(["python3", check]).stdout + run(["python3", check]).stderr
    subs = []
    for line in listing.split("\n"):
        if line.startswith("subcommands:"):
            subs = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
    if not subs:
        return [f"{check} lists no sub-commands, so nothing was checked"]
    print(f"\nrunning {len(subs)} check_docs.py sub-commands")
    bad = []
    for s in subs:
        r = run(["python3", check, s])
        last = (r.stdout.strip().split("\n") or [""])[-1]
        if not last.startswith("OK"):
            bad.append(f"{s}: {last[:160]}")
    print(f"  check_docs.py: {len(subs) - len(bad)}/{len(subs)} OK")
    blockers += ["check_docs.py " + b for b in bad]
    r = run(["python3", "e-commerce/db/tests/audit_all.py"])
    last = (r.stdout.strip().split("\n") or [""])[-1]
    print("  audit_all.py: " + last)
    if "0 findings" not in last:
        blockers.append("audit_all.py: " + last)
    if all(shutil.which(t) for t in ("initdb", "pg_ctl", "psql")):
        r = run(["bash", "e-commerce/db/tests/run_db_tests.sh"])
        last = (r.stdout.strip().split("\n") or [""])[-1]
        print("  run_db_tests.sh: " + last)
        if last != "ALL PASSED":
            blockers.append("run_db_tests.sh: " + last)
    else:
        print("  run_db_tests.sh: NOT RUN (initdb, pg_ctl or psql missing)")
    return blockers


if __name__ == "__main__":
    main()
