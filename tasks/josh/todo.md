---
name: Josh task list
description: Pending and in-progress tasks of Josh (SA Lead); read before assigning or resuming Josh's work.
---

# Josh tasks

## e-commerce: view consent.v_applicable_consent for the four consent reads

- Owner: josh
- Created at: 2026-11-20T15:53:10+07:00
- Started at: 2026-11-20T15:53:10+07:00
- Status: In review (pull request open; only the owner merges)

Drake (Backend Developer) proposed the view while building 01 register: four APIs repeat the rule "ACTIVE consent of an ACTIVE consent type". Accepted by Josh under the owner's delegation of 2026-11-17, authorized by Ittikorn. Drake keeps the two-query SQL until this merges, then maps the view as a keyless entity.

- [x] DB test `00-consent-view.test.sql` written first and seen failing (view missing), then passing.
- [x] `CREATE OR REPLACE VIEW consent.v_applicable_consent` after both tables in migration 00 up; `DROP VIEW IF EXISTS` first in 00 down. No ALTER TABLE.
- [x] Schema doc `consent/v_applicable_consent.md`, README row (type View), ER on pages 0 Overview, 1 Common · Authen and 7 All Tables; rendered and checked.
- [x] Specs 01-register, consent/01, 04, 05 read the view; each `sequence.wsd` in SQL parity; re-approved by Josh (SA Lead, delegated by Ittikorn 2026-11-17).
- [x] `audit_all.py` knows views; `check_docs.py` needles moved to the new SQL and a shared guard pins the view's two ACTIVE predicates.
- [x] Evidence: every `check_docs.py` sub-command OK (73), `audit_all.py` 0 findings, `gen_contract.py --check` exit 0 (no drift), `run_db_tests.sh` ALL PASSED on PostgreSQL 17.11.
- [ ] Owner merges the pull request; then `park` and move this record to `success-task.md`.
