---
name: Josh task list
description: Pending and in-progress tasks of Josh (SA Lead); read before assigning or resuming Josh's work.
---

# Josh tasks

## repository-wide: CI without the database tests; repair the admin-write lists after the merges

- Owner: josh
- Created at: 2026-11-15T13:47:27+07:00
- Started at: 2026-11-15T13:47:27+07:00
- Status: In progress

Owner order of 2026-11-15: remove "Install PostgreSQL 17 and the locale" and "run_db_tests.sh" from CI; the database tests run again when the API work starts. Main also failed `admin-write-spec` because the merges of #148 and the update of #145 put `product/06` and `product/07` (already on JWT claims) back into `ADMIN_WRITE_RULE_IN_DIAGRAM`.

- [x] Remove the two steps and the `psql`/`initdb` version lines from `.github/workflows/checks.yml`; say why in the header comment.
- [x] Remove `product/06` and `product/07` from `ADMIN_WRITE_RULE_IN_DIAGRAM`; every `check_docs.py` sub-command passes on the branch.
- [ ] CI `checks` green on the pull request; the owner merges.
