---
name: Josh Completed Tasks
description: Verified completed task records of Josh, moved from todo.md.
---

# Josh Completed Tasks

## e-commerce: view consent.v_applicable_consent for the four consent reads

- Owner: josh
- Created at: 2026-11-20T15:53:10+07:00
- Started at: 2026-11-20T15:53:10+07:00
- Status: Complete
- Completed at: 2026-11-20T21:22:23+07:00

Drake (Backend Developer) proposed the view while building 01 register: four APIs repeat the rule "ACTIVE consent of an ACTIVE consent type". Accepted by Josh under the owner's delegation of 2026-11-17, authorized by Ittikorn. Drake keeps the two-query SQL until this merges, then maps the view as a keyless entity.

- [x] DB test `00-consent-view.test.sql` written first and seen failing (view missing), then passing.
- [x] `CREATE OR REPLACE VIEW consent.v_applicable_consent` after both tables in migration 00 up; `DROP VIEW IF EXISTS` first in 00 down. No ALTER TABLE.
- [x] Schema doc `consent/v_applicable_consent.md`, README row (type View), ER on pages 0 Overview, 1 Common · Authen and 7 All Tables; rendered and checked.
- [x] Specs 01-register, consent/01, 04, 05 read the view; each `sequence.wsd` in SQL parity; re-approved by Josh (SA Lead, delegated by Ittikorn 2026-11-17).
- [x] `audit_all.py` knows views; `check_docs.py` needles moved to the new SQL and a shared guard pins the view's two ACTIVE predicates.
- [x] Evidence: every `check_docs.py` sub-command OK (73), `audit_all.py` 0 findings, `gen_contract.py --check` exit 0 (no drift), `run_db_tests.sh` ALL PASSED on PostgreSQL 17.11.
- [x] Owner merges the pull request; then `park` and move this record to `success-task.md`.

Evidence: #279 merged (2026-11-20T21:22:23+07:00); register reads the view since e-commerce-backend#26. Closed by Drake on the owner's request of 2026-11-21 ("ปิด record งานจบแล้วให้ทุกคน").

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
