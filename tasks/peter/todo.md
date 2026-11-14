---
name: Peter Task Plan
description: Active plans and task records of the System Analyst Peter, resolved from the workspace key peter in the agent registry.
---

# Peter Tasks

## e-commerce: shop roles design (owner, admin, staff; draft for the owner's decision)

Owner: peter
Status: In progress
Created at: 2026-11-14T18:03:13+07:00
Started at: 2026-11-14T18:03:13+07:00

Authority: the owner's answers of 2026-11-14 (relayed by Josh, SA Lead): the shop owner is a separate identity and not the shop ADMIN, a shop can have several owners, and owner, admin and staff are separate roles with fixed permissions; the SA Lead asked for a design draft first. Assignment `authorized_by: josh`, delivery `open-pr`. Nothing is approved and no schema, specification, checker, test or matrix row is changed by this task.

- [x] Collect the evidence: the `shop.t_shop_user` role constraint and unique index, the ADMIN and creator rules of `shop/08`, `shop/09`, `shop/11`, `shop/12`, the seventeen specs whose SQL checks the member role, the matrix rows of the shop APIs, the tests and the seed.
- [x] Write `docs/superpowers/specs/2026-11-14-shop-roles-design.md` with status draft (revised for the several-owner answer): D1 storage (role OWNER in `t_shop_user`, alternative `is_owner`), D2 the fixed permission table per shop API, D3 minimum rules, D4 creator, D5 who changes owners and leaving, D6 JWT or API check, D7 impact and order of work; each with a recommendation, the cost if wrong and a question (Q1–Q7).
- [x] The SA Lead put the questions to the owner and returned the answers (2026-11-14): Q1 `OWNER` as a third role value, Q2 the permission table as written, Q3 at least one ACTIVE OWNER replaces the ADMIN rule, Q4 the creator is OWNER, Q5 owners are added by promoting members and an owner leaves only while another ACTIVE owner remains, Q6 the role is checked in the database and not in the JWT; Q7 follows the order of work of D7 (SA Lead). Recorded in the document, renamed to `shop-roles-design`, status `in-review`.
- [ ] The owner changes the status of the document to approved; only then is a schema or specification change planned (work not started, held for the owner's approval).

Verification: `md-frontmatter` check OK for the new design file and this task file; no other file is changed.

## e-commerce: shop roles rollout plan (owner, admin, staff)

Owner: peter
Status: Blocked
Created at: 2026-11-14T18:17:55+07:00
Blocked at: 2026-11-14T18:17:55+07:00

Blocked: the design `docs/superpowers/specs/2026-11-14-shop-roles-design.md` is `in-review`; the owner has answered Q1–Q6 and approves the document by changing its status to approved. Waiting on: the owner (through the SA Lead). Next action: when the status is approved, start PR 1 below from the then current main. No schema, specification, sequence, checker or test is changed before that.

Plan (draft; one pull request per step, each from main, each with its own `todo` entry, tests and review by the SA Lead; the order follows D7 of the design; Tommy and Marry own the payment, sales, shipping, campaign and product files unless the SA Lead reassigns them):

- [ ] PR 1, schema and test: `e-commerce/db/migrations/up/04-shop.schema.up.sql` (`CREATE TABLE shop.t_shop_user`: `CHECK (role IN ('OWNER', 'ADMIN', 'STAFF'))`, default stays `STAFF`; no `ALTER TABLE`; the down file is unchanged), `e-commerce/doc/schema/shop/t_shop_user.md` (role values and constraint row), `e-commerce/doc/schema/README.md` if it lists the values, the domain model sources that describe the role (`diagram/domain/domain-model.md`, `domain-merchandising-model.md/.html/.drawio`, `domain-source-inventory.json` hashes, `scripts/diagrams/domain_model_content.py`, `db/er-diagram.drawio`) with Jinny, and `db/tests/04-shop-user.test.sql` (test 3 accepts `OWNER` and rejects another value; the ADMIN rule test becomes the OWNER rule). Checks: `shop-user-schema`, `er`, the schema/audit checks, `run_db_tests.sh`, the domain-model checks.
- [ ] PR 2, `shop/11-upsert-shop-user` (spec + sequence + SQL): the fixed table of D2 for member management (OWNER manages every role, ADMIN manages STAFF only, STAFF only leaves), `role` accepts `OWNER`, the rule "at least one ACTIVE OWNER" replaces "at least one ACTIVE ADMIN" (`QUERY - Count the ADMIN members of the shop after the write` becomes the owner count), leaving or demoting the last owner is 409 E10006, owners are added only by promoting an existing ACTIVE member, the member and administrator checks use the new role sets; lock order caller user → shop row → member rows; checker `shop-user-spec` and the shop-user flow needles; slim flow check if the shop group has none.
- [ ] PR 3, `shop/12-upsert-shop-user-batch`: the same rules for the batch (final-state owner rule checked once after all items), paired with PR 2.
- [ ] PR 4, `shop/08-upsert-shop`: insert writes an OWNER row (`INSERT - Add the caller as ADMIN of the new shop` becomes an OWNER row), update stays ADMIN or OWNER, delete and archive need an OWNER or a platform administrator (404/403 order unchanged), `QUERY - Check shop administrator` covers `OWNER` and `ADMIN`, an OWNER-only query for delete and archive; checker needles.
- [ ] PR 5, `shop/09-upsert-shop-batch`: the same for the batch, paired with PR 4.
- [ ] PR 6, the mechanical role-set change of the member checks: `shop/01`, `shop/02`, `shop/10`, `shop/13` (`role IN ('ADMIN', 'STAFF')` becomes `role IN ('OWNER', 'ADMIN', 'STAFF')`, sequence copied from the spec), one PR for the shop folder.
- [ ] PR 7, the same change in `sales/04`, `sales/05` (Tommy), PR 8 `payment/04` and, if the refund row of D2 stays, `payment/05` with the OWNER-or-ADMIN check and a 403 example (Tommy), PR 9 `shipping/01–04` (Tommy), PR 10 `campaign/02` (Tommy): each folder its own PR with its needles.
- [ ] PR 11, `e-commerce/doc/permission-scope.md`: the role conditions of the shop rows (OWNER, ADMIN, STAFF per row) and the note that the role is read from the database and is not a JWT claim.
- [ ] Final check after PR 11: `grep` for `role IN ('ADMIN', 'STAFF')` and `role = 'ADMIN'` in the specs finds no old role set; all documentation commands, the audit and the database tests pass on main.

Verification of this plan: not applicable yet; the inventory behind it is 21 queries in 17 specs (`campaign/02`, `payment/04`, `payment/05`, `sales/04`, `sales/05`, `shipping/01–04`, `shop/01`, `02`, `08`, `09`, `10`, `11` (3), `12` (3), `13`), the checker functions `check_shop_spec`, `check_shop_profile_spec`, `check_order_spec`, `check_shop_user_spec`, `check_shop_user_schema`, `check_shop_product_spec`, `check_payment_spec`, `check_shipping_schema`, `check_campaign_schema`, `check_campaign_data` and `check_campaign_spec`, and the test `04-shop-user.test.sql`.
Progress (2026-11-14T18:15:55+07:00): the owner answers are recorded and the document is in review.

Verification: `md-frontmatter` check OK for the design file and this task file; no other file is changed.
