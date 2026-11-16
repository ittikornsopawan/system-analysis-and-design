---
name: Peter Completed Tasks
description: Verified completed task records of the System Analyst Peter, moved from todo.md.
---

# Peter Completed Tasks

## e-commerce: migrate 12 consent and shop specs to the verified JWT claims (one API per pull request)

Owner: peter
Status: Complete
Created at: 2026-11-15T08:38:49+07:00
Started at: 2026-11-15T08:38:49+07:00
Completed at: 2026-11-15T14:21:29+07:00

Authority: the owner decisions of `docs/superpowers/specs/2026-11-07-api-review-design.md` (Q2, Q4, Q10, Q13; `PLATFORM_ADMIN` is the exact role name in the `roles` claim, payload of 2026-11-13), assigned by Josh (SA Lead) with `delivery: open-pr`, `authorized_by: josh`. Shop roles design (OWNER) is not approved and not implemented here; shop membership is still read from `shop.t_shop_user`. Specs stay `in-review`.

- [x] `consent/06-upsert-consent-type` (PR #138; also leaves `LEGACY_SEQUENCES` and `LEGACY_TOKEN_SEQUENCES`)
- [x] `consent/07-upsert-consent-type-batch` (PR #144; with the `FOR UPDATE` lock of the existing consent types, lead decision of 2026-11-15)
- [x] `consent/08-inquiry-consent-type` (PR #146; leaves `LEGACY_TOKEN_SEQUENCES`, now empty)
- [x] `shop/05-upsert-shop-type` (PR #151), [x] `shop/06-upsert-shop-type-batch` (PR #153; both with the shop type `FOR UPDATE` lock)
- [x] `shop/01-upsert-shop-product-sku` (PR #158), [x] `shop/02-upsert-shop-product-sku-batch` (PR #160)
- [x] `shop/08-upsert-shop` (PR #163), [x] `shop/09-upsert-shop-batch` (PR #164), [x] `shop/10-inquiry-shop` (PR #165)
- [x] `shop/11-upsert-shop-user` (PR #166), [x] `shop/12-upsert-shop-user-batch` (PR #167), [x] `shop/13-inquiry-shop-user` (PR #168)
- [x] Park every merged record, then stop (design freeze): the 13 records of these pull requests are parked, the workspace is clean on `main`.

Verification: every pull request passed the CI check `checks` and the review of the SA Lead, was merged, and was verified locally on the tree merged with `origin/main`: `check_docs.py` 69/69 sub-commands, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED, `test_sequence_skeleton.py` OK, and the mutation tests of what each PR added (all caught). `agent_workspace.py park` succeeded for #138, #144, #146, #151, #153, #158, #160, #163, #164, #165, #166, #167 and #168. Not verified: the diagrams were not rendered (PlantUML is not installed in the workspace) and no SQL was executed against concurrent sessions (no backend exists).

Findings recorded in the pull requests: the existence queries of the shop product SKU, shop and shop user specs are still not locked (the lock of the lead decision of 2026-11-15 covers the consent type and shop type rows only); the merge of #160 into main had dropped its checker hookup, restored in #163; `ADMIN_WRITE_LIVE_QUERIES` in `check_docs.py` can be removed when the last spec that copies the live role queries has migrated.

## e-commerce: shop roles rollout plan (owner, admin, staff)

Owner: peter
Status: Complete
Created at: 2026-11-14T18:17:55+07:00
Blocked at: 2026-11-14T18:17:55+07:00
Unblocked at: 2026-11-16T09:24:57+07:00
Started at: 2026-11-16T14:42:29+07:00
Completed at: 2026-11-16T15:04:36+07:00

Authority: the shop roles design `docs/superpowers/specs/2026-11-14-shop-roles-design.md`, approved by the owner on 2026-11-16 (D1–D7); assignment from Josh (SA Lead), delivery `open-pr` authorized by ittikorn. Reviews by Josh; merges by the owner.

- [x] PR 1, schema and test: `shop.t_shop_user.role` accepts `OWNER` in the `CREATE TABLE` (no `ALTER TABLE`, default `STAFF`), schema document, DB test 3 (two OWNER rows, unknown role rejected), `shop-user-schema` requires the OWNER constraint (PR #179, merged 2026-11-16T07:45:08Z). The plan's ADMIN-rule DB test did not exist; the domain sources were refreshed by Jinny in #182.
- [x] PR 2, `shop/11-upsert-shop-user`, and PR 3, `shop/12-upsert-shop-user-batch`, in one PR: fixed tiers of D2, at least one ACTIVE OWNER (409 E10006) replaces the ADMIN rule, OWNER only by promotion (insert as OWNER 400 E10001, promoting a member that is not ACTIVE 409 E10006), an ADMIN cannot change their own role (PR #181, merged 2026-11-16T07:50:29Z; the owner accepted the three decisions through Josh).
- [x] PR 4, `shop/08-upsert-shop`, and PR 5, `shop/09-upsert-shop-batch`, in one PR: the creator becomes OWNER, update OWNER or ADMIN, delete and archive OWNER (403 E10009), `Check shop administrator` returns the role instead of a separate OWNER query (PR #185, merged 2026-11-16T07:56:49Z; Josh accepted both decisions).
- [x] PR 6, the member checks of `shop/01`, `02`, `10`, `13` include `OWNER`; the shop/13 caller example is an OWNER (PR #188, merged 2026-11-16T07:59:13Z).
- [x] PR 7–10 (Tommy): `sales/04`, `05` (PR #180), `payment/04`, `05` with the OWNER-or-ADMIN refund (PR #183), `shipping/01–04` (PR #186), `campaign/02` (PR #187), all merged on 2026-11-16; recorded in Tommy's own task file.
- [x] PR 11, `e-commerce/doc/permission-scope.md`: shop role note (database, not a JWT claim, no `owner:*`), `shop:*` definition, role conditions of shop/01, 02, 08–13 and the payment/05 refund row; the matrix stays `in-review` (PR #190, merged 2026-11-16T08:03:02Z, merge commit `9243b8f`).
- [x] Final check on main `c5c601e` (all rollout PRs except #190, which changes only the matrix): no `role IN ('ADMIN', 'STAFF')`, `role = 'ADMIN'`, `Count the ADMIN`, `as ADMIN of the new shop` or `at least one ADMIN` left in `e-commerce/doc/api`, the migrations or the schema documents (the only match is the intended "replaces the former rule of at least one ACTIVE ADMIN" in shop/11 and shop/12); all 70 `check_docs.py` sub-commands OK, `audit_all.py` 0 findings, `test_sequence_skeleton.py` OK, `test_agent_workspace.py` OK, `run_db_tests.sh` ALL PASSED, `generate_domain_diagrams.py --check` PASS. Accepted by Josh. CI of main at `9243b8f`: success.

Verification: every PR above had green CI before review; the workspace records of #179, #181, #185, #188 and #190 are parked.
