---
name: Pre-send Checklist
description: What to verify before committing and opening a PR, which findings block, and how the preflight script maps to the project's checkers. Read when running or interpreting preflight.py.
---

# Pre-send checklist

Run `python3 .agents/skills/commit-and-pr/scripts/preflight.py --base main [--run-checks]` from the repository root. It prints the state and exits 1 when something blocks.

| # | Check | Blocks the commit? | If it fails |
|---|---|---|---|
| 1 | The branch is not `main`/`master` | yes | create a branch first |
| 2 | The files you are about to commit are the task's files (the script lists changed and untracked files by top-level area) | yes, until you chose | stage by name; list the rest as excluded |
| 3 | No secret-looking content (private key headers, `AKIA...` keys, `password=`/`secret=`/`token=` with a value, bearer tokens) in a file you will commit | yes | remove it, or confirm with the user that it is a harmless example |
| 4 | No build output or junk (`bin/`, `obj/`, `node_modules/`, `__pycache__/`, `*.pyc`, `.DS_Store`, `*.log`) | yes | leave it out or add it to `.gitignore` after asking |
| 5 | No file over 1 MB | yes, unless the user confirms | ask, or leave it out |
| 6 | `git diff --check` is clean (no trailing whitespace or conflict markers) in what you will commit | yes | fix the whitespace |
| 7 | Project checkers pass when the change touches specs, schema, migrations, SQL tests or the ER diagram | yes | fix the cause; never edit a checker to make it pass |

## Project checkers (the e-commerce project)

Required when the change includes any of `e-commerce/doc/api/`, `e-commerce/doc/schema/`, `e-commerce/db/migrations/`, `e-commerce/db/tests/`, `e-commerce/db/er-diagram.drawio`:

- every `python3 e-commerce/db/tests/check_docs.py <sub-command>` listed by running the script with no arguments: each must print `OK`
- `python3 e-commerce/db/tests/audit_all.py`: must end with `0 findings`
- `bash e-commerce/db/tests/run_db_tests.sh`: must end with `ALL PASSED` (needs PostgreSQL tools; if they are missing, say it was not run and why)

`--run-checks` runs all three and pastes their last lines for the PR's Verification section. Other projects: run that project's own build and tests instead, and say which.
