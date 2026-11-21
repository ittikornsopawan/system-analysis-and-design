#!/usr/bin/env python3
"""Mutation-test a checker: break a file on purpose, run the checker, expect it to fail, restore the file.

A checker that has never failed cannot be trusted. Each case replaces the first occurrence of `old` with
`new` in `file`, runs `check`, and reports CAUGHT when the checker exits non-zero. The file is always
restored, also when the checker crashes. Exit code 0 only when every case was caught.

Usage: python3 mutation_harness.py cases.json [--cwd <repo root>]

cases.json is a list of objects:
  {"file": "e-commerce/doc/api/sales/02-create-order/spec.md",
   "old": "\\"status\\": \\"WAIT_PAYMENT\\"", "new": "\\"status\\": \\"PAYMENT_CONFIRMED\\"",
   "check": ["python3", "e-commerce/db/tests/check_docs.py", "order-spec"]}
`file` and `check` paths are relative to --cwd (default: the current directory).
"""
import json
import subprocess
import sys


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cwd = argv[argv.index("--cwd") + 1] if "--cwd" in argv else "."
    cases = json.load(open(argv[1], encoding="utf-8"))
    caught = 0
    for case in cases:
        path = f"{cwd}/{case['file']}"
        original = open(path, encoding="utf-8").read()
        if case["old"] not in original:
            print(f"BAD CASE (text not found) {case['file']}: {case['old'][:50]!r}")
            continue
        open(path, "w", encoding="utf-8").write(original.replace(case["old"], case["new"], 1))
        try:
            result = subprocess.run(case["check"], capture_output=True, text=True, cwd=cwd)
            ok = result.returncode != 0
        finally:
            open(path, "w", encoding="utf-8").write(original)
        caught += ok
        print(("CAUGHT" if ok else "MISSED"), case["file"].split("/")[-2] if "/" in case["file"] else case["file"], repr(case["old"][:50]))
    print(f"{caught}/{len(cases)} caught")
    return 0 if caught == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
