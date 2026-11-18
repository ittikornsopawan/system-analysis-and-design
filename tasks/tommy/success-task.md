---
name: Tommy Completed Tasks
description: Verified completed task records of Tommy, moved from todo.md.
---

# Tommy Completed Tasks

## e-commerce: spec frontmatter, cart, payment, sales, shipping and campaign

Owner: tommy
Status: Complete
Created at: 2026-11-14T17:30:00+07:00
Started at: 2026-11-14T17:40:00+07:00
Completed at: 2026-11-14T18:09:43+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-frontmatter`, scopes `e-commerce/doc/api/cart`, `e-commerce/doc/api/payment`, `e-commerce/doc/api/sales`, `e-commerce/doc/api/shipping`, `e-commerce/doc/api/campaign`, `e-commerce/db/tests/check_docs.py`, `.agents/skills/data-modeling/SKILL.md`, `tasks/tommy`.

- [x] Add the frontmatter (`name`, `description`, `status: in-review`, `approved_by: null`, `approved_at: null`) to the 18 specs of the five groups that had none, as the owner decided on 2026-11-14; `name` is the Name of the API table, `description` states the purpose and when to read the spec. Evidence: `git diff --numstat` shows only added lines in `e-commerce/doc/api`, and `md-frontmatter` passes with the 18 specs removed from `MD_FRONTMATTER_PENDING`.
- [x] Make `md-frontmatter` print a readable FAIL instead of a traceback outside a git checkout. Evidence: a copy of `check_docs.py` in a temporary folder without `.git` printed `FAIL: md-frontmatter needs a git checkout`.
- [x] Correct the line of `.agents/skills/data-modeling/SKILL.md` that said the files copied from `assets/` have no frontmatter.
- [x] Run every check. Evidence: `check_docs.py` 69/69 OK, `audit_all.py` 53 tables audited and 0 findings, `run_db_tests.sh` ALL PASSED.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: the five specs of `docs/superpowers/specs` that still have no frontmatter, when the owner decides their status. Evidence: pull request #130 merged at 2026-11-14T18:09:43+07:00, CI `checks` passed.

## e-commerce: spec template and frontmatter, shop 05 to 10

Owner: tommy
Status: Complete
Created at: 2026-11-14T18:15:43+07:00
Started at: 2026-11-14T18:15:43+07:00
Completed at: 2026-11-14T18:50:16+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-shop-2`, scopes `e-commerce/doc/api/shop/05-upsert-shop-type` to `10-inquiry-shop`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the second of three shop PRs.

- [x] Remove `### Shop Type Rules` (shop/05, shop/06), `### Shop Rules` (shop/08, shop/09) and `### Shop Inquiry Rules` (shop/10); the rules are short bullets under `## Domain`, the order of the checks is a note of `sequence.wsd`; the links to the single upsert become plain words; no SQL and no behavior is changed (the platform administrator check of the shop APIs stays as it is). Evidence: `verify_seq.py` OK for the six folders, strict SQL parity and render.
- [x] Add the frontmatter (`status: in-review`) to the six specs; remove them from `LEGACY_SPEC_TEMPLATE` and `MD_FRONTMATTER_PENDING`; the shop type, shop and admin write checkers search the spec and its sequence note.
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: shop 11 to 16. Evidence: pull request #133 merged at 2026-11-14T18:50:16+07:00, CI `checks` passed.

## e-commerce: spec template and frontmatter, shop 11 to 16

Owner: tommy
Status: Complete
Created at: 2026-11-14T18:19:38+07:00
Started at: 2026-11-14T18:19:38+07:00
Completed at: 2026-11-14T18:47:16+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-shop-3`, scopes `e-commerce/doc/api/shop/11-upsert-shop-user` to `16-inquiry-storefront-product-review`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the last of three shop PRs.

- [x] Remove `### Shop User Rules` (shop/11, shop/12), `### Shop User Inquiry Rules`, `### Shop Product List Rules`, `### Review Rules` and `### Review Inquiry Rules`; the rules and the approval sentence of each section are short bullets under `## Domain`, the lock rule and the order of the checks are notes of `sequence.wsd`; the links to other specs become plain words; no SQL and no behavior is changed. Evidence: `verify_seq.py` OK for the six folders, strict SQL parity and render; every removed line is found again in the spec or its note.
- [x] Add the frontmatter (`status: in-review`) to the six specs; remove them from `LEGACY_SPEC_TEMPLATE` and `MD_FRONTMATTER_PENDING`; the shop user and review checkers look for each rule in the file where it lives (the moved rules in the sequence only).
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Evidence: pull request #136 merged at 2026-11-14T18:47:16+07:00, CI `checks` passed.

## e-commerce: spec template and frontmatter, shop 01 to 04

Owner: tommy
Status: Complete
Created at: 2026-11-14T18:12:52+07:00
Started at: 2026-11-14T18:12:52+07:00
Completed at: 2026-11-14T18:43:06+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-shop-1`, scopes `e-commerce/doc/api/shop/01-upsert-shop-product-sku`, `02-upsert-shop-product-sku-batch`, `03-inquiry-shop-product-sku`, `04-inquiry-storefront-product`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the first of three shop PRs (01 to 04, 05 to 10, 11 to 16).

- [x] Remove `### Lot Rules` (shop/01, shop/02) and `### Page Rules` (shop/04); the rules are short bullets under `## Domain`, the order of the checks is a note of `sequence.wsd`; no SQL and no behavior is changed. Evidence: `verify_seq.py` OK for the four folders (175, 175, 45 and 84 SQL lines), strict SQL parity and render.
- [x] Add the frontmatter (`status: in-review`) to the four specs; remove them from `LEGACY_SPEC_TEMPLATE` and `MD_FRONTMATTER_PENDING`; the shop checker searches the spec and its sequence note.
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: shop 05 to 10. Evidence: pull request #132 merged at 2026-11-14T18:43:06+07:00, CI `checks` passed.

## e-commerce: JWT claims, shipping 01 create shipping

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:39:20+07:00
Started at: 2026-11-15T08:39:20+07:00
Completed at: 2026-11-15T08:42:24+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-shipping-create`, scopes `e-commerce/doc/api/shipping/01-create-shipping`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the first of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user` after BEGIN; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of `shipping-spec`: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both; mutation test 17/17 caught plus 3 injected faults rejected.
- [x] Run every check. Evidence: `check_docs.py` 69/69 OK, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: shipping 02. Evidence: pull request #139 merged at 2026-11-15T08:42:24+07:00, CI `checks` passed.

## e-commerce: JWT claims, shipping 02 update shipping status

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:41:51+07:00
Started at: 2026-11-15T08:41:51+07:00
Completed at: 2026-11-15T08:47:57+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-shipping-status`, scopes `e-commerce/doc/api/shipping/02-update-shipping-status`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the second of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user`; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of the checker: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both. Mutation test: 15/15 mutations of the added needles caught, plus the order, the order sentence and the permission rule (3/3); three injected faults rejected (second 401 removed, the administrator query back in the spec, an m_role read back in the sequence)
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: shipping 03. Evidence: pull request #141 merged at 2026-11-15T08:47:57+07:00, CI `checks` passed.

## e-commerce: JWT claims, shipping 04 shop shipping inquiry

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:46:45+07:00
Started at: 2026-11-15T08:46:45+07:00
Completed at: 2026-11-15T08:54:22+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-shipping-inquiry`, scopes `e-commerce/doc/api/shipping/04-inquiry-shop-shipping`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the fourth of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user`; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of the checker: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both. Mutation test: 18/18 mutations of the added needles caught (spec and sequence separately, plus the order of the checks and the permission rule); three injected faults rejected (second 401 removed, the administrator query back in the spec, an m_role read back in the sequence)
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: campaign 01. Evidence: pull request #147 merged at 2026-11-15T08:54:22+07:00, CI `checks` passed.

## e-commerce: JWT claims, shipping 03 shipping stop write

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:42:44+07:00
Started at: 2026-11-15T08:42:44+07:00
Completed at: 2026-11-15T08:52:10+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-shipping-stop`, scopes `e-commerce/doc/api/shipping/03-upsert-shipping-stop`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the third of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user`; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of the checker: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both. Mutation test: 15/15 mutations of the added needles caught, plus the order, the order sentence and the permission rule (3/3); three injected faults rejected (second 401 removed, the administrator query back in the spec, an m_role read back in the sequence)
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: shipping 04. Evidence: pull request #143 merged at 2026-11-15T08:52:10+07:00, CI `checks` passed.

## e-commerce: JWT claims, campaign 02 campaign inquiry

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:50:50+07:00
Started at: 2026-11-15T08:50:50+07:00
Completed at: 2026-11-15T14:04:03+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-campaign-inquiry`, scopes `e-commerce/doc/api/campaign/02-inquiry-campaign`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the sixth of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

## e-commerce: JWT claims, campaign 03 campaign ledger inquiry

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:52:26+07:00
Started at: 2026-11-15T08:52:26+07:00
Completed at: 2026-11-15T13:56:42+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-campaign-ledger`, scopes `e-commerce/doc/api/campaign/03-inquiry-campaign-ledger`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the seventh of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user`; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of the checker: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both. Mutation test: 18/18 mutations of the added needles caught (spec and sequence separately, plus the order of the checks and the permission rule); three injected faults rejected (second 401 removed, the administrator query back in the spec, an m_role read back in the sequence)
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: campaign 03. Evidence: pull request #154 merged at 2026-11-15T13:56:42+07:00, CI `checks` passed.

## e-commerce: JWT claims, campaign 01 campaign upsert

Owner: tommy
Status: Complete
Created at: 2026-11-15T08:48:11+07:00
Started at: 2026-11-15T08:48:11+07:00
Completed at: 2026-11-15T08:57:36+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-jwt-campaign-upsert`, scopes `e-commerce/doc/api/campaign/01-upsert-campaign`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the fifth of seven JWT PRs (shipping 01 to 04, campaign 01 to 03), by the owner decisions Q2/Q4/Q10/Q13 of `docs/superpowers/specs/2026-11-07-api-review-design.md`.

- [x] Remove `Get the platform administrator role` and `Check platform administrator` from the spec and the sequence; the administrator is the exact role `PLATFORM_ADMIN` in the verified `roles` claim; add the roles claim to the JWT verify and the 401, the caller lock and `Check current credential and user`; the shop member check stays on `shop.t_shop_user`; no other SQL is changed. Evidence: strict SQL parity, render with every SQL line visible, plantuml check.
- [x] Update the needles of the checker: the JWT needles are searched in the spec and in the sequence separately, the removed queries must be gone from both. Mutation test: 15/15 mutations of the added needles caught, plus the order of the checks, the order sentence and the permission rule (3/3); three injected faults rejected (second 401 removed, the administrator query back in the spec, an m_role read back in the sequence)
- [x] Run every check. Evidence: see the pull request.
- [x] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: campaign 02. Evidence: pull request #149 merged at 2026-11-15T08:57:36+07:00, CI `checks` passed.

## e-commerce: shop roles rollout, PR 7 to PR 10 (OWNER in the shop member checks)

Owner: tommy
Status: Complete
Created at: 2026-11-16T14:46:28+07:00
Started at: 2026-11-16T14:46:28+07:00
Completed at: 2026-11-16T14:58:06+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/tommy`, one branch and one pull request per folder, each from the latest `origin/main`. Governing design: `docs/superpowers/specs/2026-11-14-shop-roles-design.md` (approved 2026-11-16, D1 and the fixed table of D2). Plan: `tasks/peter/todo.md`, "shop roles rollout", PR 7 item. This record is kept in PR 7 only, so that the four branches do not edit the same file.

- [x] PR 7, `sales/04`, `sales/05`: `role IN ('ADMIN', 'STAFF')` becomes `role IN ('OWNER', 'ADMIN', 'STAFF')` in the spec and `sequence.wsd`, the member text names OWNER, `order-spec` requires the new role set and rejects the old one. Evidence: pull request #180 merged at 2026-11-16T14:49:14+07:00, CI `checks` passed; it was merged before the report reached the SA Lead, so later links were sent when the PR opened.
- [x] PR 8, `payment/04` (member check, same change) and `payment/05` (the refund row of D2 stays: OWNER or ADMIN only, a STAFF member gets 403 E10009, with a 403 example); `payment-spec` needles. Evidence: pull request #183 merged at 2026-11-16T14:54:27+07:00, CI `checks` passed; the SA Lead kept the one existing `Fail - Forbidden` example (no variant).
- [x] PR 9, `shipping/01–04`: the member check, same change; shipping needles. Evidence: pull request #186 merged at 2026-11-16T14:57:05+07:00, CI `checks` passed.
- [x] PR 10, `campaign/02`: the member check, same change; campaign needles. Evidence: pull request #187 merged at 2026-11-16T14:57:25+07:00, CI `checks` passed; after it, `grep "role IN ('ADMIN', 'STAFF')"` finds nothing in the sales, payment, shipping and campaign specs and sequences.
- [x] Before each PR: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py` and `preflight.py`; after CI is green, the link to Josh, then `suspend`. Evidence: before every PR `check_docs.py` 70/70 OK, `audit_all.py` 53 tables and 0 findings, both skill tests OK, preflight no blockers, and one deliberate fault caught per folder; `run_db_tests.sh` not run (no SQL touched); all four workspaces suspended and parked.

## F8: Stripe webhook amount and currency check

- Owner: Tommy
- Created at: 2026-11-17
- Started at: 2026-11-17
- Status: Complete
- Completed at: 2026-11-17T13:27:58+07:00

- [x] Spec: domain rule, body parameters, `p.currency` in the query
- [x] Sequence: mismatch branch, amount-check note
- [x] Checker needles for 02-stripe-webhook
- [x] Regenerate `api-contract.json` with `gen_contract.py`
- [x] Run all checks and preflight, open PR, send link to Josh Evidence (closed by Josh, 2026-11-18): PR #212 merged 2026-11-17T13:27:58+07:00 (merge commit a1216af), CI `checks` passed.

## OpenAPI 3.1 validator in CI

- Owner: Tommy
- Created at: 2026-11-17
- Started at: 2026-11-17
- Status: Complete
- Completed at: 2026-11-17T13:21:54+07:00

- [x] Validate current main contract: `openapi-spec-validator` 0.9.0 reports OK (no errors to route to Josh)
- [x] Add pinned install, validate and deliberate-fault steps to `.github/workflows/checks.yml`
- [x] Add optional validator pass to `check_docs.py api-contract`
- [x] Run all checks and preflight, open PR, send link to Josh Evidence (closed by Josh, 2026-11-18): PR #210 merged 2026-11-17T13:21:54+07:00 (merge commit 1a53cf5), CI `checks` passed.

## Parameter APIs 01-03 (public.m_parameter)

- Owner: Tommy
- Created at: 2026-11-18
- Started at: 2026-11-18
- Status: Complete
- Completed at: 2026-11-18T08:06:58+07:00

- [x] Questions Q1-Q7 answered by Josh (delegated by the owner, 2026-11-18); Q6 changed to a public inquiry
- [x] Spec and sequence 01-upsert-parameter
- [x] Spec and sequence 02-upsert-parameter-batch
- [x] Spec and sequence 03-inquiry-parameter (public, 60 requests per minute)
- [x] `parameter-spec` checker, admin-write/upsert/limits lists, `API_CONTRACT_DOMAINS`, skeleton count 91, conventions rate-limit line, regenerate `api-contract.json`
- [x] Run all checks, `run_db_tests.sh` and preflight, open PR #226, send link to Josh
- [x] CI green after approval commit, send link to Josh Evidence (closed by Josh, 2026-11-18): PR #226 merged 2026-11-18T08:06:58+07:00 (merge commit e00138b), CI `checks` passed.
- [x] Approved by Josh (SA Lead, delegated by Ittikorn 2026-11-17) at 2026-11-18T07:49:47+07:00: approval fields set, contract regenerated (91 operations, inquiry `security: []`)

Completed records are in `success-task.md`.
