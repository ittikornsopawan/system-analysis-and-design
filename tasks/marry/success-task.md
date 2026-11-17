---
name: Marry Completed Tasks
description: Verified completed task records of Marry, moved from todo.md.
---

# Marry Completed Tasks

## e-commerce: OpenAPI contract, payment domain

Owner: marry
Status: Complete
Created at: 2026-11-17T13:10:00+07:00
Started at: 2026-11-17T13:10:00+07:00
Completed at: 2026-11-17T13:11:42+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-payment`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 8 of the contract rollout.

- [x] Publish the 5 approved operations of `payment`; the Stripe webhook body nests its dotted names (a parent is required when a child is MANDATORY) and marks the external payload `additionalProperties: true` (lead decision of Josh, 2026-11-17); 3/3 deliberate faults rejected.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, both test suites OK, `preflight.py` no blockers; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #208, CI `checks` passed (35s), merged at 2026-11-17T13:11:42+07:00 (91624c0).

## e-commerce: OpenAPI contract, sales domain

Owner: marry
Status: Complete
Created at: 2026-11-17T12:45:00+07:00
Started at: 2026-11-17T12:45:00+07:00
Completed at: 2026-11-17T13:08:05+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-sales`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 7 of the contract rollout.

- [x] Publish the 5 approved operations of `sales` (checkout inquiry, order create, order inquiry, shop order inquiry, order cancel); `platformProfit` is nullable because an example shows null (owner rule).
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, both test suites OK, `preflight.py` no blockers; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #207, CI `checks` passed (34s), Josh review passed, merged at 2026-11-17T13:08:05+07:00 (e31165a).

## e-commerce: OpenAPI contract, cart domain

Owner: marry
Status: Complete
Created at: 2026-11-17T12:42:00+07:00
Started at: 2026-11-17T12:42:00+07:00
Completed at: 2026-11-17T12:43:43+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-cart`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 6 of the contract rollout.

- [x] Publish the 3 approved operations of `cart`; fields shown as null in the examples are nullable (owner rule).
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, both test suites OK, `preflight.py` no blockers; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #206, CI `checks` passed (29s), merged at 2026-11-17T12:43:43+07:00 (6784db0).

## e-commerce: OpenAPI contract, shop domain

Owner: marry
Status: Complete
Created at: 2026-11-17T12:31:00+07:00
Started at: 2026-11-17T12:31:00+07:00
Completed at: 2026-11-17T12:40:34+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-shop`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 5 of the contract rollout.

- [x] Publish the 16 approved operations of `shop`; the 3 storefront inquiries are public (no security requirement), as their specs say.
- [x] Write the contract as one-line JSON (lead decision of Josh, 2026-11-17): the indented file was 1221 KB, over the 1 MB preflight limit, about 1.66 MB projected for all domains; `SKILL.md` says how to read it.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, both test suites OK, `preflight.py` no blockers after the one-line change; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #204, CI `checks` passed (24s), merged at 2026-11-17T12:40:34+07:00 (55295f5).

## e-commerce: OpenAPI contract, product domain

Owner: marry
Status: Complete
Created at: 2026-11-17T12:28:00+07:00
Started at: 2026-11-17T12:28:00+07:00
Completed at: 2026-11-17T12:30:06+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-product`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `tasks/lessons.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 4 of the contract rollout; Josh approved the lesson entry for the null-summary bug on 2026-11-17.

- [x] Publish the 15 approved operations of `product`; author 13 and 14 (in-review, now on main) stay unpublished.
- [x] `tasks/lessons.md`: lesson for the null-summary and conditional-default bug fixed in #199.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, both test suites OK, `preflight.py` no blockers; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #201, CI `checks` passed (27s), merged at 2026-11-17T12:30:06+07:00 (97ffef8).

## e-commerce: OpenAPI contract, consent domain and drift check

Owner: marry
Status: Complete
Created at: 2026-11-17T09:40:00+07:00
Started at: 2026-11-17T09:40:00+07:00
Completed at: 2026-11-17T12:26:27+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-consent`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 3 of the contract rollout; Josh asked on 2026-11-17 for a `--check` drift mode called from `api-contract`.

- [x] `gen_contract.py --check`: exits 1 when the committed contract differs from a fresh generation; `check_docs.py api-contract` runs it; hand edit and unregenerated spec change rejected.
- [x] Fix: every operation had `summary: null` and a description starting `None` (#197, #198) because the Name/Description table above the first `##` was never read; the generator now reads it and reports a spec without it; deliberate fault rejected.
- [x] Fix: a conditional default ("FALSE on insert") is no longer published as a string `default` of a boolean.
- [x] Publish the 8 approved operations of `consent`.
- [x] `SKILL.md`: the regenerate note names the drift check.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `gen_contract.py --check` up to date, `audit_all.py` 0 findings, `test_sequence_skeleton.py` OK, `test_agent_workspace.py` OK, `preflight.py` no blockers; 3/3 deliberate faults rejected; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #199, CI `checks` passed (33s), Josh review passed, merged at 2026-11-17T12:26:27+07:00 (be0812b).

## e-commerce: OpenAPI contract, author domain and owner conventions

Owner: marry
Status: Complete
Created at: 2026-11-17T09:33:00+07:00
Started at: 2026-11-17T09:33:00+07:00
Completed at: 2026-11-17T09:38:29+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-author`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 2 of the contract rollout. Owner answers of 2026-11-17 relayed by Josh: count fields (`pageIndex`, `pageSize`, `totalItems`, `totalPages`, `expiresIn`, `status.code`) are integer; commit the generator under `api-contract-design/scripts` with a regenerate note in its SKILL.md; a null in a spec example makes the field nullable. Lead decision: publish author 01-12 now, Peter's 13-17 after the owner approves them.

- [x] `gen_contract.py`: regenerates the contract from the approved specs of `API_CONTRACT_DOMAINS`, applies the owner conventions, checks every example against its schema and exits 1 on any mismatch; 4/4 deliberate faults rejected.
- [x] Regenerate `authen-and-author`: 9 count fields `number` -> `integer`, nothing else changes.
- [x] Publish the 12 approved operations of `author`.
- [x] `check_docs.py api-contract`: `author` in `API_CONTRACT_DOMAINS`, only `status: approved` specs count, so in-review specs (Peter's 13-17) do not break CI; deliberate fault (an approved spec turned in-review) rejected.
- [x] `SKILL.md`: how to regenerate the contract.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `audit_all.py` 0 findings, `test_sequence_skeleton.py` 12 OK, `test_agent_workspace.py` 27 OK, `preflight.py` no blockers; 6/6 deliberate faults rejected; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #198, CI `checks` passed (29s), Josh review passed, merged at 2026-11-17T09:38:29+07:00 (570fc32).

## e-commerce: OpenAPI contract, shared components and authen-and-author

Owner: marry
Status: Complete
Created at: 2026-11-17T09:20:00+07:00
Started at: 2026-11-17T09:20:00+07:00
Completed at: 2026-11-17T09:32:09+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-authen`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`. Owner order of 2026-11-17: the SA team publishes `e-commerce/api/api-contract.json` from the 83 approved specs before dev starts, one PR per domain (authen-and-author, author, consent, product, shop, cart, sales, payment, shipping, campaign). Role: API Documenter (`.agents/agents/api-documenter.md`).

- [x] Shared `components`: status object, error responses (400 E10001, 401 E10002, 403 E10009, 404 E10004/E10005, 408 E90001, 409 E10003/E10006/E10007/E10008, and 500 without bizCode because every spec has a 500 example), bearer JWT scheme, `timestamp` and `requestId` header parameters, tags; servers from the spec Domain table.
- [x] The 10 operations of `authen-and-author`, each with `x-spec`, fields, required state, constraints and examples copied from its spec.
- [x] `check_docs.py api-contract`: missing operation, operation without a spec, status codes different from the spec examples, wrong `x-spec`, `openapi` not 3.1.0; 5/5 deliberate faults rejected.
- [x] Verification: 71 `check_docs.py` sub-commands 0 failed, `audit_all.py` 0 findings, `test_sequence_skeleton.py` 12 OK, `test_agent_workspace.py` 27 OK, `preflight.py` no blockers; no OpenAPI 3.1 validator installed (not run).
- [x] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge. Evidence: pull request #197, CI `checks` passed (36s), Josh review passed, merged at 2026-11-17T09:32:09+07:00 (9e8479b).

## e-commerce: JWT claims, product/03 (upsert product batch)

Owner: marry
Status: Complete
Created at: 2026-11-15T09:00:00+07:00
Started at: 2026-11-15T09:00:00+07:00
Completed at: 2026-11-15T08:47:32+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/03-upsert-product-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. First of nine product write specs of the last sweep (product 03, 04, 06, 07, 09, 10, 11, 13, 14), one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS`, remove it from the in-diagram list, check spec needles in the spec and sequence needles in the sequence, and make the claims flow order generic (existence read, claims permission, conflict read, write) so the next folders only need their name added.
- [x] Verification: 69/69 `check_docs.py` sub-commands, 20 of 20 deliberate faults rejected (spec and sequence, single and batch wording).
- [x] Merge `origin/main`, run `audit_all.py`, `run_db_tests.sh` and `preflight.py`, open the pull request, tell Josh when `checks` is green, then suspend. Evidence: pull request #140 merged at 2026-11-15T08:47:32+07:00, CI `checks` passed.

## e-commerce: JWT claims, product/09-upsert-product-category-attribute-batch

Owner: marry
Status: Complete
Created at: 2026-11-15T08:49:18+07:00
Started at: 2026-11-15T08:49:18+07:00
Completed at: 2026-11-15T13:56:07+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-attribute-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/09-upsert-product-category-attribute-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

## e-commerce: JWT claims, product/07-upsert-product-category-attribute

Owner: marry
Status: Complete
Created at: 2026-11-15T08:46:50+07:00
Started at: 2026-11-15T08:46:50+07:00
Completed at: 2026-11-15T09:25:05+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-attribute-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/07-upsert-product-category-attribute`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

## e-commerce: JWT claims, product/06-upsert-product-category-batch

Owner: marry
Status: Complete
Created at: 2026-11-15T08:44:41+07:00
Started at: 2026-11-15T08:44:41+07:00
Completed at: 2026-11-15T08:55:38+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/06-upsert-product-category-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 22/22 deliberate faults rejected.

## e-commerce: JWT claims, product/04-upsert-product-category

Owner: marry
Status: Complete
Created at: 2026-11-15T08:42:17+07:00
Started at: 2026-11-15T08:42:17+07:00
Completed at: 2026-11-15T08:54:43+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-category-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/04-upsert-product-category`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 18/18 deliberate faults rejected.
- [x] Tell Josh when `checks` is green, then suspend. Evidence: pull request #142 merged at 2026-11-15T08:54:43+07:00, CI `checks` passed.

## e-commerce: repair check_docs.py after the merge of #142 and #145

Owner: marry
Status: Complete
Created at: 2026-11-15T08:56:54+07:00
Started at: 2026-11-15T08:56:54+07:00
Completed at: 2026-11-15T09:24:10+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `fix/marry-check-docs-admin-write-merge`, scopes `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Ordered by Josh (urgent): `check_docs.py` on `main` did not parse after #142 (product/04) and #145 (product/06) were merged.

- [x] Make `ADMIN_WRITE_CAMPAIGN` list product/04 and product/06 and leave only product/07 and product/09 in `ADMIN_WRITE_RULE_IN_DIAGRAM`; the claims set keeps product/01, 03, 04 and 06. No entry of either pull request is dropped.
- [x] Verification: `ast.parse` passes, 69/69 `check_docs.py` sub-commands, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED.
- [x] Tell Josh, then suspend; the open pull requests (#148, #150 and the product/10 branch) merge `main` after this lands. Evidence: pull request #156 merged at 2026-11-15T09:24:10+07:00, CI `checks` passed.

## e-commerce: JWT claims, product/11-upsert-product-type-batch

Owner: marry
Status: Complete
Created at: 2026-11-15T13:56:34+07:00
Started at: 2026-11-15T13:56:34+07:00
Completed at: 2026-11-15T14:04:56+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-type-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/11-upsert-product-type-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 20/20 deliberate faults rejected.

## e-commerce: JWT claims, product/10-upsert-product-type

Owner: marry
Status: Complete
Created at: 2026-11-15T08:55:51+07:00
Started at: 2026-11-15T08:55:51+07:00
Completed at: 2026-11-15T13:58:44+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-type-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/10-upsert-product-type`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 0/0 deliberate faults rejected.
- [x] Tell Josh when `checks` is green, then suspend. Evidence: pull request #155 merged at 2026-11-15T13:58:44+07:00, CI `checks` passed.

## e-commerce: JWT claims, product/14-upsert-product-brand-batch

Owner: marry
Status: Complete
Created at: 2026-11-15T13:59:48+07:00
Started at: 2026-11-15T13:59:48+07:00
Completed at: 2026-11-15T14:07:31+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-brand-batch-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/14-upsert-product-brand-batch`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim, checked once for the whole batch.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 20/20 deliberate faults rejected.

## e-commerce: JWT claims, product/13-upsert-product-brand

Owner: marry
Status: Complete
Created at: 2026-11-15T13:58:11+07:00
Started at: 2026-11-15T13:58:11+07:00
Completed at: 2026-11-15T14:05:52+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/marry`, branch `docs/marry-product-brand-upsert-jwt-claims`, scopes `e-commerce/doc/api/product/13-upsert-product-brand`, `e-commerce/db/tests/check_docs.py`, `tasks/marry`. Queue of the last sweep: product 03, 04, 06, 07, 09, 10, 11, 13, 14, one API per pull request, pattern of product/01. Governing decisions: Q2, Q4, Q10 and Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `QUERY - Get the platform administrator role` and `QUERY - Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified JWT `roles` claim.
- [x] Add the JWT verify with 401, `QUERY - Lock the caller user` and `QUERY - Check current credential and user` (401, ROLLBACK) right after BEGIN; all other SQL is unchanged.
- [x] `check_docs.py`: add the folder to `ADMIN_WRITE_JWT_CLAIMS` and take it out of the in-diagram list; spec needles are checked in the spec and sequence needles in the sequence.
- [x] Verification: every `check_docs.py` sub-command, `audit_all.py`, `run_db_tests.sh` and `preflight.py` pass; 18/18 deliberate faults rejected.
- [x] Tell Josh when `checks` is green, then suspend. Evidence: pull request #161 merged at 2026-11-15T14:05:52+07:00, CI `checks` passed.
