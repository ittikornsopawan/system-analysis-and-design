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
| 6 | `git diff --check` is clean (no trailing whitespace, conflict markers or extra blank lines at EOF) in what you will commit | yes | fix whitespace; after scripted text edits, normalize each file to one final newline before preflight |
| 7 | Project checkers pass when the change touches specs, schema, migrations, SQL tests or the ER diagram | yes | fix the cause; never edit a checker to make it pass |
| 8 | In a managed named-agent workspace, active assignment metadata authorizes `open-pr` and every changed path is inside its recorded scope | yes | resume through `agent-workspace` with the original assignment or remove out-of-scope changes; never edit local metadata to bypass the check |

## Verify requested artifact coverage

Before staging documentation or diagram changes, map every explicitly requested topic and child topic to substantive artifact coverage. For a layered code guide, each requested layer and sub-layer needs its purpose, owned work, input/output, boundaries, collaborators, a concrete source example and implementation/design status. A label, folder list, summary row or passing link/render check alone does not satisfy this gate.

When owner review changes or clarifies scope, reconcile the title, introduction and detailed sections against the complete request before publication. Record the coverage evidence alongside technical checks; missing requested coverage blocks delivery until corrected.

## Integrate the latest base before publication

This gate runs after the task commit and before push/PR creation or update. `<base>` is the PR target, default `main`; run every merge while on the task branch. The preflight script checks uncommitted files and uses `--base` only as a report label: it does not fetch, merge, prove ancestry or validate the full committed PR diff.

1. **Preserve work and fetch.** Confirm the task branch and inventory local changes. Keep excluded work out of the merge; preserve it before proceeding if it would be overwritten. Run `git fetch origin <base>`, require success, and record `git rev-parse origin/<base>` as the integrated base SHA. A stale local main or a mergeability preview is insufficient.
2. **Merge into the task branch.** Run `git merge --no-commit origin/<base>`. If already up to date, record that result. If a merge is pending, inspect the combined changes and resolve every path reported by `git diff --name-only --diff-filter=U`. Preserve both sides' valid requirements, consumers and task records; use the governing spec to settle behavior. Resolve routine conflicts directly. Stage resolved files explicitly, inspect the staged diff, and finish with `git commit -F <merge-message-file>` using the repository's Conventional Commit format. Fetching the base does not authorize modifying it.
3. **Prove integration and scope.** `git merge-base --is-ancestor <integrated-base-sha> HEAD` must exit 0; `git ls-files -u` must print nothing, and no merge may remain in progress. Check `git diff --check origin/<base>...HEAD`, inspect `git diff --name-status origin/<base>...HEAD` and review that full diff. Incoming base changes belong to integration history; the final PR diff must contain only the task's authorized changes. Recheck excluded local work against its saved state.
4. **Verify the result.** Repeat the preflight and run the checks required by the final branch diff and any conflict resolution, including affected callers/imports and paired specs/sequences. A post-commit preflight reporting zero files is not evidence that the branch diff passed its project checks; run those checks directly as needed. Capture actual commands/results, the base SHA, merge commit (or already-up-to-date result), conflicted paths and resolution evidence in the PR. Failed integration, unresolved conflicts or failed required checks block publication.
5. **Publish only the verified state.** Push the task branch normally, then create/update the PR. If a newly fetched base moves before publication or remote mergeability reports a new conflict, merge the updated base into the same task branch and repeat affected verification. Preserve published commits; this workflow does not require a force push.

## Project checkers (the e-commerce project)

Required when the change includes any of `e-commerce/doc/api/`, `e-commerce/doc/schema/`, `e-commerce/db/migrations/`, `e-commerce/db/tests/`, `e-commerce/db/er-diagram.drawio`:

- every `python3 e-commerce/db/tests/check_docs.py <sub-command>` listed by running the script with no arguments: each must print `OK`
- before that, `check_docs.py` must parse (a file that does not parse lists no sub-commands, and the preflight reports it as a blocker instead of `0/0 OK`); the sub-command `check-registry` fails when a check function does not end with `return` or `raise` or is neither registered in `COMMANDS` nor called, which is what a merge that cuts the end of a checker leaves behind
- `python3 e-commerce/db/tests/audit_all.py`: must end with `0 findings`
- `bash e-commerce/db/tests/run_db_tests.sh`: must end with `ALL PASSED` (needs PostgreSQL tools; if they are missing, say it was not run and why)

`--run-checks` runs all three and pastes their last lines for the PR's Verification section. Other projects: run that project's own build and tests instead, and say which.
