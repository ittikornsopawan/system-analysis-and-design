---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

## e-commerce: JWT claims, product/03 (upsert product batch)

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T09:00:00+07:00
Started at: 2026-11-15T09:00:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/03-upsert-product-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. First of nine product write specs of the last sweep (product 03, 04, 06, 07, 09, 10, 11, 13, 14), one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS`, remove it from the in-diagram list, check spec needles in the spec and sequence needles in the sequence, and make the claims flow order generic (existence read, claims permission, conflict read, write) so the next folders only need their name added.
- [x] Verification: 69/69 `check_docs.py` sub-commands, 20 of 20 deliberate faults rejected (spec and sequence, single and batch wording).
- [ ] Merge `origin/main`, run `audit_all.py`, `run_db_tests.sh` and `preflight.py`, open the pull request, tell Josh when `checks` is green, then suspend.

## e-commerce: JWT claims, product/09-upsert-product-category-attribute-batch

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T08:49:18+07:00
Started at: 2026-11-15T08:49:18+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-attribute-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/09-upsert-product-category-attribute-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.
## e-commerce: JWT claims, product/07-upsert-product-category-attribute

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T08:46:50+07:00
Started at: 2026-11-15T08:46:50+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-attribute-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/07-upsert-product-category-attribute`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.
## e-commerce: JWT claims, product/06-upsert-product-category-batch

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T08:44:41+07:00
Started at: 2026-11-15T08:44:41+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/06-upsert-product-category-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 22/22 deliberate faults rejected.
## e-commerce: JWT claims, product/04-upsert-product-category

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T08:42:17+07:00
Started at: 2026-11-15T08:42:17+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/04-upsert-product-category`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 18/18 deliberate faults rejected.
- [ ] Tell Josh when `checks` is green, then suspend.

## e-commerce: repair check_docs.py after the merge of #142 and #145

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T08:56:54+07:00
Started at: 2026-11-15T08:56:54+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `fix/marry-check-docs-admin-write-merge`, scopes `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Ordered by Josh (urgent): `check_docs.py` on `main` did not parse after #142 (product/04) and #145 (product/06) were merged.

- [x] Make `ADMIN_WRITE_CAMPAIGN` list product/04 and product/06 and leave only product/07 and product/09 in `ADMIN_WRITE_RULE_IN_DIAGRAM`; the claims set keeps product/01, 03, 04 and 06. No entry of either pull request is dropped.
- [x] Verification: `ast.parse` passes, 69/69 `check_docs.py` sub-commands, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED.
- [ ] Tell Josh, then suspend; the open pull requests (#148, #150 and the product/10 branch) merge `main` after this lands.

## e-commerce: JWT claims, product/11-upsert-product-type-batch

Owner: marry
Status: In review (pull request pending)
Created at: 2026-11-15T13:56:34+07:00
Started at: 2026-11-15T13:56:34+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-type-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/11-upsert-product-type-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 20/20 deliberate faults rejected.
- [ ] Tell Josh when `checks` is green, then suspend.
