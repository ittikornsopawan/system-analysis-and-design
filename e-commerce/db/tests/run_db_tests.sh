#!/usr/bin/env bash
# Runs every migration (up, down in reverse order, up again) and every *.test.sql in a throw-away PostgreSQL
# cluster that lives in a temp directory. Needs initdb, pg_ctl and psql on the PATH (brew install postgresql).
# Usage: bash e-commerce/db/tests/run_db_tests.sh        (exit code 0 = everything passed)
set -u
export LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
for tool in initdb pg_ctl psql; do
  command -v "$tool" >/dev/null || { echo "missing $tool: install PostgreSQL first (brew install postgresql)"; exit 2; }
done
HERE="$(cd "$(dirname "$0")" && pwd)"
MIG="$HERE/../migrations"
PGTMP="$(mktemp -d)"
cleanup() { pg_ctl -D "$PGTMP" stop -m immediate >/dev/null 2>&1; rm -rf "${PGTMP:?}"; }
trap cleanup EXIT
initdb -D "$PGTMP" -A trust >/dev/null 2>&1 || { echo "initdb failed"; exit 2; }
pg_ctl -D "$PGTMP" -o "-p 54339 -k $PGTMP" -l "$PGTMP/log" -w start >/dev/null || { echo "could not start PostgreSQL"; exit 2; }
SQL() { psql -h "$PGTMP" -p 54339 -d postgres -v ON_ERROR_STOP=1 -q "$@"; }
rc=0
run_file() { # run_file <file> <label>
  if SQL -f "$1" >/dev/null 2>"$PGTMP/err"; then echo "OK   $2"; else echo "FAIL $2: $(grep -m1 ERROR "$PGTMP/err")"; rc=1; fi
}
for f in $(ls "$MIG"/up/*.sql | sort); do run_file "$f" "up $(basename "$f")"; done
for f in $(ls "$MIG"/down/*.sql | sort -r); do run_file "$f" "down $(basename "$f")"; done
for f in $(ls "$MIG"/up/*.sql | sort); do run_file "$f" "up again $(basename "$f")"; done
for t in "$HERE"/*.test.sql; do
  echo "--- $(basename "$t")"
  out="$(SQL -f "$t" 2>&1)"
  echo "$out" | grep -E "PASS|FAIL|ERROR" | sed -E 's#^psql:[^ ]*/##'
  if echo "$out" | grep -qE "FAIL|ERROR"; then rc=1; fi
done
[ $rc -eq 0 ] && echo "ALL PASSED" || echo "SOME FAILED"
exit $rc
