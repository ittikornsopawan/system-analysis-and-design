---
name: Josh Completed Tasks
description: Verified completed task records of Josh, moved from todo.md.
---

# Josh Completed Tasks

## repository-wide: CI without the database tests; repair the admin-write lists after the merges

- Owner: josh
- Created at: 2026-11-15T13:47:27+07:00
- Started at: 2026-11-15T13:47:27+07:00
- Completed at: 2026-11-15T13:49:31+07:00
- Status: Complete

Owner order of 2026-11-15: remove "Install PostgreSQL 17 and the locale" and "run_db_tests.sh" from CI; the database tests run again when the API work starts. Main also failed `admin-write-spec` because the merges of #148 and the update of #145 put `product/06` and `product/07` (already on JWT claims) back into `ADMIN_WRITE_RULE_IN_DIAGRAM`.

- [x] Remove the two steps and the `psql`/`initdb` version lines from `.github/workflows/checks.yml`; say why in the header comment.
- [x] Remove `product/06` and `product/07` from `ADMIN_WRITE_RULE_IN_DIAGRAM`; every `check_docs.py` sub-command passes on the branch.
- [x] CI `checks` green on the pull request; the owner merges. Evidence: pull request #157 merged at 2026-11-15T13:49:31+07:00, CI `checks` passed.
