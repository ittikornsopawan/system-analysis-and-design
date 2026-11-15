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
