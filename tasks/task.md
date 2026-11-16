---
name: Pending task list
description: Every task that is still open across the owner, Josh, Tommy, Marry, Peter and the legacy root file, checked against main and GitHub on 2026-11-16; read before planning dev.
---

# Pending tasks

Checked on 2026-11-16 against `main` (c190f70) and the pull requests on GitHub. The team is frozen and no pull request is open.

| Group | Tasks |
|---|---|
| 1. Owner decisions and actions | 7 |
| 2. Shop roles rollout (blocked on approval) | 12 |
| 3. Deferred work and backlog | 10 |
| **Real work still open** | **29** |
| 4. Records to close (work done, box not ticked) | 27 |

## 1. Owner decisions and actions

- [ ] Approve the 83 API specs in `e-commerce/doc/api/` (all `status: in-review`).
- [ ] Approve the 8 design documents in `docs/superpowers/specs/` that are `in-review`: product SKU multi-level, author, authen, payment, order, cart, shop lot pricing and storefront, shop roles.
- [ ] Approve the detailed Redis/MongoDB policy documents of Jinny's diagrams before any backend, collection/outbox schema or endpoint work (`tasks/todo.md`).
- [ ] Decide whether the target-row queries of shop SKU, shop and shop user get `FOR UPDATE` (the lock decision of 2026-11-15 covered only consent type and shop type).
- [ ] Set the branch protection of `main` in GitHub: required check `checks`, branches must be up to date.
- [ ] Run `run_db_tests.sh` locally before the API work; CI no longer runs it (owner order of 2026-11-15).
- [ ] Have Barry (Head of Technology) review the final report of the JWT round; his session is not running.

## 2. Shop roles rollout (Peter, blocked until the shop roles design is approved)

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

- [ ] WP5b: author specs 13–17 (role permission upsert and inquiry, user permission upsert and inquiry, check); deferred until an API enforces permissions.
- [ ] Remove `ADMIN_WRITE_LIVE_QUERIES` from `check_docs.py`; no spec uses the live role queries any more.
- [ ] Merge the two `er_name_rows` helpers of `check_docs.py` (both still exist).
- [ ] Extend `audit_all.py` to a column without an alias in the `WHERE` of an `UPDATE`.
- [ ] Retrofit the plain `UNIQUE` and `CASCADE` of the older master tables.
- [ ] Rewrite the team protocol in `docs/handoff/` to match the named-agent rule.
- [ ] Record the Head of Technology answer in `docs/superpowers/specs/2026-11-07-api-review-design.md`.
- [ ] Owner: verify the resource registry and the diagram role after Jinny's scope is released (`tasks/owner/todo.md`).
- [ ] Owner: resolve every legacy task of `tasks/todo.md` with evidence or closure (blocked).
- [ ] Owner: move the closed legacy records to the owner folders and turn `tasks/todo.md` into an index (blocked by the item above).

## 4. Records to close (work is merged, the box was never ticked)

Each item needs only its record ticked and moved to the owner's `success-task.md`. The evidence is the merged pull request.

- [ ] Josh (1): CI without the database tests, #157 merged.
- [ ] Marry (5): product/03, product/04, the `check_docs.py` repair #156, product/10 #155, product/13 #161.
- [ ] Tommy (10): frontmatter of cart, payment, sales, shipping and campaign; template of shop 01–04, 05–10, 11–16; JWT shipping 01–04; JWT campaign 01 #149 and 03 #154.
- [ ] Legacy root `tasks/todo.md` (11): WP7 campaign (#15), WP3b shipping auto-complete (#26) and its gate 2 review, WP5c admin-only writes (#20), Peter review items scope upsert, Q24 batch, Q24 single and the permission matrix (#92), M3 GitHub Actions (#91), the payment/05 JWT wording question (fixed on main), M6 roles as objects (no spec left).
