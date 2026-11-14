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
- [x] Write `docs/superpowers/specs/2026-11-14-shop-owner-design.md` with status draft (revised for the several-owner answer): D1 storage (role OWNER in `t_shop_user`, alternative `is_owner`), D2 the fixed permission table per shop API, D3 minimum rules, D4 creator, D5 who changes owners and leaving, D6 JWT or API check, D7 impact and order of work; each with a recommendation, the cost if wrong and a question (Q1–Q7).
- [ ] The SA Lead sends the seven questions to the owner and returns the answers; only then is a schema or specification change planned (work not started, held for the owner's approval).

Verification: `md-frontmatter` check OK for the new design file and this task file; no other file is changed.

## e-commerce: frontmatter for five design documents

Owner: peter
Status: In progress
Created at: 2026-11-14T19:00:00+07:00
Started at: 2026-11-14T19:00:00+07:00

Authority: the SA Lead's assignment of 2026-11-14 (authorized_by josh): add frontmatter with status in-review and null approval fields, because the SA Lead cannot approve for the owner; the approval evidence found in the documents goes to the pull request body for the owner to decide.

- [x] Add name, description, `status: in-review`, `approved_by: null`, `approved_at: null` to the product SKU multi-level, cart, order, payment and shop lot pricing design documents.
- [x] Remove the five paths from `MD_FRONTMATTER_PENDING` in `e-commerce/db/tests/check_docs.py`.
- [ ] The owner decides whether any of the five documents becomes `approved` (the evidence is listed in the pull request body; no status is changed here).

Verification: `md-frontmatter` check OK; every other check listed in the pull request body.
