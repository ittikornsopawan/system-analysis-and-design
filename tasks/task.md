---
name: Pending task list
description: Every task that is still open across the owner, Josh, Tommy, Marry, Peter and the legacy root file, checked against main and GitHub on 2026-11-16; read before planning dev.
---

# Pending tasks

Checked on 2026-11-16 against `main` (c190f70) and the pull requests on GitHub. The team is frozen and no pull request is open.

| Group                                           | Tasks  |
| ----------------------------------------------- | ------ |
| 1. Owner decisions and actions                  | 1      |
| 2. Shop roles rollout (unblocked 2026-11-16)    | 12     |
| 3. Deferred work and backlog                    | 4      |
| **Real work still open**                        | **17** |
| 4. Records closed on 2026-11-16                 | 27     |

## 1. Owner decisions and actions

- [x] Approve the 83 API specs in `e-commerce/doc/api/` (all `status: in-review`). Approved by the owner on 2026-11-16; `status: approved` in every spec.
- [x] Approve the 8 design documents in `docs/superpowers/specs/` that are `in-review`: product SKU multi-level, author, authen, payment, order, cart, shop lot pricing and storefront, shop roles. Approved by the owner on 2026-11-16.
- [x] Approve the detailed Redis/MongoDB policy documents of Jinny's diagrams before any backend, collection/outbox schema or endpoint work (`tasks/todo.md`). Approved by the owner on 2026-11-16: the 19 in-review documents of `e-commerce/diagram/`.
- [x] Decide whether the target-row queries of shop SKU, shop and shop user get `FOR UPDATE` (the lock decision of 2026-11-15 covered only consent type and shop type). Owner decision of 2026-11-16: add `FOR UPDATE`; the work is in group 3.
- [ ] Set the branch protection of `main` in GitHub: required check `checks`, branches must be up to date.
- [x] Run `run_db_tests.sh` before the API work; CI no longer runs it (owner order of 2026-11-15). Owner decision of 2026-11-16: the SA Lead runs it on main and reports. Done 2026-11-16 by the SA Lead on main c453316 (PostgreSQL 17.11): `ALL PASSED`, 82 PASS lines: migrations up, down and up again with every SQL test.
- [x] Have Barry (Head of Technology) review the final report of the JWT round; his session is not running. Owner decision of 2026-11-16: no Barry review for this round; the owner approves directly.

## 2. Shop roles rollout (Peter; unblocked, the design was approved on 2026-11-16)

Source: `tasks/peter/todo.md`, design `docs/superpowers/specs/2026-11-14-shop-roles-design.md`. Today 30 spec and sequence files still use the old role set `role IN ('ADMIN', 'STAFF')`.

- [ ] PR 1: schema and test, `t_shop_user.role` accepts `OWNER`.
- [ ] PR 2: `shop/11-upsert-shop-user`, fixed permission table, at least one ACTIVE OWNER.
- [ ] PR 3: `shop/12-upsert-shop-user-batch`, the same rules for the batch.
- [ ] PR 4: `shop/08-upsert-shop`, the creator becomes OWNER; delete and archive need an OWNER or a platform administrator.
- [ ] PR 5: `shop/09-upsert-shop-batch`, the same for the batch.
- [ ] PR 6: member checks of `shop/01`, `shop/02`, `shop/10`, `shop/13` include `OWNER`.
- [ ] PR 7: `sales/04`, `sales/05` (Tommy).
- [ ] PR 8: `payment/04`, and `payment/05` if the refund row stays (Tommy).
- [ ] PR 9: `shipping/01–04` (Tommy).
- [ ] PR 10: `campaign/02` (Tommy).
- [ ] PR 11: `e-commerce/doc/permission-scope.md`, the shop role rows.
- [ ] Final check: no old role set left in the specs; every check, the audit and the database tests pass on main.

## 3. Deferred work and backlog

- [ ] WP5b: author specs 13–17 (role permission upsert and inquiry, user permission upsert and inquiry, check); deferred until an API enforces permissions (owner confirmed on 2026-11-16).
- [x] Remove `ADMIN_WRITE_LIVE_QUERIES` from `check_docs.py`; no spec uses the live role queries any more. Done in the checker cleanup pull request of 2026-11-16: `admin-write-spec` now checks only the JWT claims path.
- [x] Merge the two `er_name_rows` helpers of `check_docs.py`. Done in the same pull request: the first one, which the second overrode, is removed.
- [x] Extend `audit_all.py` to a column without an alias in the `WHERE` of an `UPDATE`. Done 2026-11-16: 129 UPDATE statements are now checked, 0 findings; a subquery or `UPDATE ... FROM` is skipped.
- [x] Retrofit the plain `UNIQUE` and `CASCADE` of the older master tables (owner approved on 2026-11-16). Done 2026-11-16: `product.m_product_category` and `product.m_product_category_attribute` have a partial unique name (not DELETED) and the 5 foreign keys into them are RESTRICT; `03-product-category.test.sql` and `product-category-schema` guard it.
- [x] Add `FOR UPDATE` to the target-row queries of shop SKU (01, 02), shop (08, 09) and shop user (11, 12), after the credential check and before the permission decision (owner decision of 2026-11-16). Done 2026-11-16: the six specs lock their target rows; batches 02 and 09 first lock their existing rows in ascending id order; the shop SKU check keeps the membership check before the lock; `shop-spec` guards it.
- [x] Rewrite the team protocol in `docs/handoff/` to match the named-agent rule. Done 2026-11-16: `docs/handoff/2026-11-16-team-protocol.md`; the 2026-11-06 protocol points to it as superseded.
- [x] Record the consent/02 answer in `docs/superpowers/specs/2026-11-07-api-review-design.md` (the root item was misread as a Head of Technology answer). Already done: section "Consent type of a consent (2026-11-14)" of that file.
- [ ] Owner: verify the resource registry and the diagram role after Jinny's scope is released (`tasks/owner/todo.md`).
- [ ] Owner: resolve every legacy task of `tasks/todo.md` with evidence or closure (blocked).
- [ ] Owner: move the closed legacy records to the owner folders and turn `tasks/todo.md` into an index (blocked by the item above).

## 4. Records closed on 2026-11-16

The 27 records whose work was merged are closed, on the owner's order of 2026-11-16. Each record has its pull request, merge time and CI result as evidence.

- [x] Josh (1): moved to `tasks/josh/success-task.md` (#157).
- [x] Marry (5 open boxes, 10 records): moved to `tasks/marry/success-task.md` (#140, #142, #145, #148, #150, #155, #156, #159, #161, #162).
- [x] Tommy (10 open boxes, 11 records): moved to `tasks/tommy/success-task.md` (#130, #132, #133, #136, #139, #141, #143, #147, #149, #152, #154).
- [x] Legacy root `tasks/todo.md` (11): ticked in place with evidence (#15, #20, #26, #83, #85, #86, #88, #91, #105, #129); the legacy records are not moved until its 4 open items (in groups 1 and 3 above) are resolved.

#145 and #148 merged while `checks` failed on stale `check_docs.py` lists; #156 and #157 repaired the lists, and `checks` passes on main.
