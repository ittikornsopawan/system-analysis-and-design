---
name: Shop Roles Design
description: Design of the shop roles owner, admin and staff with fixed permissions, with the owner answers of 2026-11-14: where the role is stored, the fixed permission table per shop API, the minimum rules, who creates and changes owners, the form in the JWT and the impact on schema, tests and specs, with a recommendation, a cost if wrong and an owner question for each point; read before changing shop.t_shop_user, the shop APIs or the owner rows of the permission matrix.
status: in-review
approved_by: null
approved_at: null
---

# Shop roles: owner, admin, staff (in review)

Date: 2026-11-14 · Author: Peter (SA) · Reviewer: Josh (SA Lead) · Status: **in review. The owner answered the questions on 2026-11-14 as recommended; the owner changes the status to approved. No schema, specification, checker, test or matrix row is changed by this document.**

## Why this document exists

The owner asked for a scope that says "the caller must be the owner of the shop". On 2026-11-14 the owner said the shop owner is a separate identity and not the shop ADMIN, then widened the answer (the SA Lead's relay of the owner's words): **"เจ้าของร้านอ่ะ สามารถมีได้หลายคนสามารถแยก owner, staff, admin อะไรในในร้านได้เลยแต่เป็น fix permission"**. So: a shop can have several owners; owner, admin and staff are separate roles inside the shop; the permission of each role is fixed, not configurable. This replaces the first draft of this document, which assumed one owner column on `shop.m_shop`.

## What the repository says today (evidence)

- `shop.t_shop_user` has `role VARCHAR(32) NOT NULL DEFAULT 'STAFF' CHECK (role IN ('ADMIN', 'STAFF'))`, one non-DELETED row per shop and user (`uq_t_shop_user_shop_id_user_id`), and a shop may have several ADMIN rows. `shop.m_shop` has no owner and `created_by` is an audit string.
- `shop/08-upsert-shop` and `shop/09`: any caller with a token can create a shop and becomes its ADMIN in the same transaction; update, delete and archive need an ADMIN or a platform administrator; `platformMarginRate` needs a platform administrator.
- `shop/11-upsert-shop-user` and `shop/12`: an ADMIN or a platform administrator manages every member (also other ADMINs); a STAFF can only leave the shop; the shop must keep at least one ACTIVE ADMIN, also against a platform administrator.
- Seventeen specs contain a member or administrator SQL on `role`: `shop/01`, `02`, `08`, `09`, `10`, `11` (3), `12` (3), `13`, `sales/04`, `sales/05`, `payment/04`, `payment/05`, `shipping/01–04`, `campaign/02`. Their checks are `role IN ('ADMIN', 'STAFF')` (a member) or `role = 'ADMIN'` (an administrator).
- Tests: `04-shop-user.test.sql` (the role constraint and the ADMIN rule); the seed has no shop.
- JWT (decision of 2026-11-13): `scopes` are flat `<code>:*` with no shop instance, so the token cannot say which shop a user belongs to or in which role.

## Decisions

Each point has the recommendation, the reason, the cost if it is wrong and the owner answer of 2026-11-14 (relayed by the SA Lead).

### D1. Where the role is stored

- **Recommendation:** add `OWNER` to the role of `shop.t_shop_user`: `CHECK (role IN ('OWNER', 'ADMIN', 'STAFF'))`, edited in the `CREATE TABLE` (never `ALTER TABLE`). A user has one role per shop (the unique index already says one row per shop and user). Powers are cumulative in the fixed table of D2: OWNER can do what ADMIN can, ADMIN what STAFF can. A shop has any number of OWNER rows.
- **Why:** it matches the owner's words (three separate roles, several owners), keeps one table for "who belongs to the shop", and needs no new table or column.
- **Cost:** every `role IN ('ADMIN', 'STAFF')` becomes `role IN ('OWNER', 'ADMIN', 'STAFF')` and every `role = 'ADMIN'` becomes `role IN ('OWNER', 'ADMIN')` in the seventeen specs above and their sequences (mechanical SQL changes, one API per PR), plus the role constraint, the schema document and the test.
- **Alternative with a smaller blast radius:** keep `ADMIN` and `STAFF` and add `is_owner BOOLEAN NOT NULL DEFAULT FALSE` to `t_shop_user` (an owner is an ADMIN row with the flag). Member and administrator checks stay unchanged and only the owner-only checks add `AND su.is_owner`. It reads as "an admin with a flag" rather than a separate role, so it is weaker on the owner's wording.
- **If wrong:** a separate table `shop.t_shop_owner` would make owners independent of membership and add a join to every owner check; not recommended.
- **Owner answer (2026-11-14):** `OWNER` is the third value of `shop.t_shop_user.role`; the `is_owner` flag is not used.

### D2. Fixed permission of OWNER, ADMIN and STAFF per shop API

Proposed defaults. "today" is the behaviour of the delivered specs; a star marks a change. The permissions are fixed in the specs and are not configured per shop. A platform administrator keeps the access it has today and is not a shop role.

| Operation (API) | Today | OWNER | ADMIN | STAFF |
| --- | --- | --- | --- | --- |
| Create a shop (`shop/08`, `09` insert) | any token | creator becomes OWNER* | - | - |
| Update the shop profile and images (`shop/08`, `09`) | ADMIN | yes | yes | no |
| Delete or archive the shop (`shop/08`, `09`) | ADMIN | yes* (only OWNER) | no* | no |
| Platform margin rate (`shop/08`, `09`) | platform administrator | no | no | no |
| Add or change a STAFF member (`shop/11`, `12`) | ADMIN | yes | yes | no |
| Add, change or remove an ADMIN member (`shop/11`, `12`) | ADMIN | yes | no* | no |
| Add, change or remove an OWNER (`shop/11`, `12`) | not existing | yes* | no | no |
| Leave the shop (delete or archive own row) | STAFF, ADMIN under the last-ADMIN rule | yes, if another ACTIVE OWNER remains* | yes | yes |
| Shop product SKU and lot upsert (`shop/01`, `02`) | ADMIN or STAFF | yes | yes | yes |
| Shop inquiry incl. margin fields (`shop/10`), member inquiry (`shop/13`) | member | yes | yes | yes |
| Order inquiry, cancel (`sales/04`, `05` shop side) | member | yes | yes | yes |
| Payment inquiry (`payment/04`) | member | yes | yes | yes |
| Refund (`payment/05`) | member | yes | yes* | no* |
| Shipping create, status, stop, inquiry (`shipping/01–04`) | member | yes | yes | yes |
| Campaign inquiry of the shop (`campaign/02`) | member | yes | yes | yes |

- **Why these defaults:** keep today's behaviour wherever the owner has not asked for a difference; the starred rows are the ones that need a role difference to exist at all: only owners delete a shop and manage owners, admins no longer manage other admins, and a refund (money) needs OWNER or ADMIN.
- **If wrong:** each row is one condition in one API (text, SQL and sequence of that API); a flatter table (admins keep managing admins) removes the star on that row.
- **Owner answer (2026-11-14):** the table above is used as written: only owners delete a shop and manage owners, admins manage staff and not other admins, a refund needs an owner or an admin, everything else stays as today.

### D3. Minimum rules

- **Recommendation:** a shop must keep **at least one ACTIVE OWNER** (409 E10006, rolled back), checked on the state after the write, with the shop row locked as the ADMIN rule is today; a platform administrator cannot skip it. The old rule "at least one ACTIVE ADMIN" becomes redundant, because an ACTIVE OWNER always has admin power, so it is **replaced** by the owner rule.
- **If wrong:** keeping both rules adds one count query to `shop/11` and `shop/12`; dropping the owner rule lets a shop have no owner.
- **Owner answer (2026-11-14):** a shop must keep at least one ACTIVE OWNER and this replaces the rule of at least one ACTIVE ADMIN.

### D4. Who is the owner when a shop is created

- **Recommendation:** the caller of the insert (the verified `sub`) becomes an OWNER in the same transaction, in place of the ADMIN row of today (`INSERT - Add the caller as ADMIN of the new shop` becomes an OWNER row). The request never carries a role. No existing shop needs a backfill: the project has no production data and the seed has no shop.
- **If wrong:** creating a shop for another user needs an optional member list in the insert, which is a new body field of `shop/08` and `shop/09`.
- **Owner answer (2026-11-14):** the creator of a shop is its OWNER, in place of ADMIN.

### D5. Who adds or removes an owner, and can an owner leave

- **Recommendation:** an OWNER (any ACTIVE owner of the shop) or a platform administrator adds an owner, and only by changing the role of an **existing ACTIVE member** (admin or staff) to OWNER, so ownership is never given to someone who is not already in the shop; no acceptance step. An ADMIN cannot create or remove owners. An OWNER can change another owner to ADMIN or remove another owner, and **can leave the shop or demote themselves only while another ACTIVE OWNER remains** (409 E10006 otherwise).
- **If wrong:** an acceptance step needs a pending state (columns or a table) and one more endpoint; letting a platform administrator alone manage owners moves the owner check from the owner to the platform.
- **Owner answer (2026-11-14):** owners and platform administrators add an owner only by promoting an existing member, and an owner can leave or demote themselves only while another ACTIVE owner remains.

### D6. Role in the JWT or checked at the API

- **Recommendation:** **checked at the API**, not in the token. The role is per shop and changes while a 15-minute token lives, and the new payload has no shop instance (`shop:*` only). Every shop API already reads `shop.t_shop_user` inside its transaction for the member check; it will read the role from the same row and apply the fixed table of D2. The matrix keeps the data boundary `shop` and gets a **role condition** on the rows of D2 (for example "OWNER of the target shop"); no `owner:*` claim is issued.
- **If wrong:** putting roles in the token needs per-shop values (`owner:<shopId>`), which the owner excluded when choosing `<code>:*`, grows the token with the number of shops and goes stale at a role change; that is a new JWT decision.
- **Owner answer (2026-11-14):** the shop role is checked in the database by each API and is not carried in the JWT.

### D7. Impact if the design is approved

- **Schema:** `04-shop.schema.up.sql` (`CREATE TABLE shop.t_shop_user`: the role CHECK gains `'OWNER'`; no `ALTER TABLE`; `04-shop.schema.down.sql` unchanged); the schema document `e-commerce/doc/schema/shop/t_shop_user.md` (role values and the constraint); the domain model document; the checks that read them (`audit_all.py`, `shop-user-schema`).
- **Seed:** none (the seed has no shop). **Database tests:** `04-shop-user.test.sql` (the role constraint, the ADMIN rule becomes the OWNER rule, the new role).
- **Specifications and sequences, one API per PR:** the mechanical role-set change in the seventeen specs of D1; real rule changes in `shop/08` and `shop/09` (insert writes an OWNER; delete and archive owner-only), `shop/11` and `shop/12` (the tiers of D2, the owner rule, who changes owners), `payment/05` only if the refund row of D2 is accepted; the matrix rows (role conditions).
- **Not touched:** `author`, `consent`, `authen`, the seed, the login and refresh payload, `sales/01–03`, `payment/01–03`, `cart`, `campaign/01`, `campaign/03`.
- **Order of work after approval:** schema and tests, then `shop/11` and `shop/12`, then `shop/08` and `shop/09`, then the mechanical SQL changes of the other fourteen specs (grouped by folder, one PR each), then `payment/05` if accepted, then the matrix.
- **Decision of the SA Lead (2026-11-14):** the question was not asked separately; the impact and the order of work above are followed.

## Owner answers (2026-11-14)

The owner answered Q1 to Q6 as recommended; the answers are recorded under each decision above and summarised here. Q7 follows the SA Lead's decision.

1. Q1: `OWNER` is the third value of `shop.t_shop_user.role`.
2. Q2: the permission table of D2 is used as written.
3. Q3: at least one ACTIVE OWNER replaces at least one ACTIVE ADMIN.
4. Q4: the creator of a shop is its OWNER.
5. Q5: owners and platform administrators add owners by promoting existing members; an owner leaves or demotes themselves only while another ACTIVE owner remains.
6. Q6: the shop role is checked in the database, not in the JWT.
7. Q7: the order of work of D7 is followed (SA Lead).

## What this document does not do

It does not change `shop.t_shop_user`, a specification, a sequence, a checker, a test, the seed or the matrix, and it does not start the order of work above: the work starts only after the owner approves this document. It is read together with [the review design record](2026-11-07-api-review-design.md), whose decisions it does not change.
