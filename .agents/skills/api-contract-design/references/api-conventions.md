---
name: API Conventions
description: Behaviour rules for e-commerce API specs: endpoint naming, HTTP and bizCode tables, upsert, batch and inquiry semantics, permission and public API patterns, order of checks, prototypes to copy. Read before writing or reviewing any spec.
---

# API conventions

## The three endpoints of a table

| Endpoint | Folder | Purpose |
|---|---|---|
| `POST v1/<group>/<name>/upsert` | `NN-upsert-<name>` | insert, update, delete or archive one row |
| `POST v1/<group>/<name>/upsert/batch` | `NN-upsert-<name>-batch` | the same for 1–100 rows in one transaction |
| `GET v1/<group>/<name>` | `NN-inquiry-<name>` | list or fetch rows |

Folder: `e-commerce/doc/api/<group>/<NN>-<name>/` with `spec.md` and an empty `sequence.wsd`; the number continues the group's numbering. Not every table needs all three (a table the system fills itself has only an inquiry; a customer-owned row like a review has no batch). Say why in the spec when you leave one out.

## Upsert

- No `id` = insert. `id` = update. `rowStatus: "DELETED"` = soft delete. `rowStatus: "ARCHIVED"` = archive. Rows are never removed.
- HTTP: insert **201**, update **200**, delete **204 with no body**, archive **200**. **Batch always answers 200**, also when an item deletes; each item reports `index`, its id and `action` (`INSERT`, `UPDATE`, `DELETE`, `ARCHIVE`).
- `DELETED` is final: an id that is deleted counts as not found (404). `INACTIVE`, `LOCKED`, `ARCHIVED` can go back to `ACTIVE`. A request that inserts with `rowStatus` `DELETED` is a 400.
- Nested children (images, lots, members): without `id` = insert, with `id` = update, `rowStatus` `DELETED` = delete, children that are not listed are **kept**. The exception is a child list that defines a complete set (product option levels); say so in the spec and in the example.
- The caller (user) always comes from the access token, never from the body.
- Unchangeable fields (`shopId`, `userId`, parent keys) must be sent again on update and a different value is a 400.

## Batch

1–100 items, one transaction, all or nothing. Validate the whole request first (400, in item order), then existence (404), then permission (403), then conflicts (409), then write. Every error message starts with the position, `skus[2]: ...`. Check duplicate ids and duplicate unique values inside the request (400). A rule that depends on the final state (the last admin of a shop, a 100-line cart) is checked once after all items are applied.

## Inquiry

Query parameters: `id` (a list with one item), `pageIndex` (from 1, default 1), `pageSize` (default 10, max 100), `search` (ILIKE), plus the filters the screen needs. Rows with `DELETED` are never returned. The response is `data.<items>[]`, `pageIndex`, `pageSize`, `totalItems`, `totalPages`; nothing found is **200 with an empty list**, unless the thing asked for (a shop page) must exist. Every `ORDER BY` ends in a unique column (`id`) so pages never repeat or skip a row; say the sort in a rule sentence.

## Error codes

| HTTP | bizCode | Use |
|---|---|---|
| 400 | E10001 | missing or malformed field, duplicate in one request, too many items |
| 401 | E10002 | access token invalid or expired |
| 403 | E10009 | the caller may not do this (not a member of the shop, not the owner, not a platform administrator) |
| 404 | E10004 | the row named by `id` (or the requested resource) does not exist |
| 404 | E10005 | a row the request refers to (a foreign key) does not exist |
| 409 | E10003 | the name or code already exists |
| 409 | E10006 | cannot delete or change because it is in use, or because of the row's status |
| 409 | E10007 | stock is not enough, or the item is not on sale |
| 409 | E10008 | the cart is full |
| 408 | E90001 | timeout |

A bizCode has **one** HTTP status in the whole project (`check_docs.py biz-codes` enforces it). Before you invent a code, read the table in the checker's data: `grep -rhn '"bizCode"' e-commerce/doc/api | sort | uniq -c`. Success is `S10000`.

## Order of checks

validate the request (400) → existence (404) → permission (403) → conflict, duplicate and in-use checks (409) → write, in one transaction. Write this line in the spec's rule section.

## Permission patterns

- Customer APIs: the user of the token owns the data; another user's row is "not found" (404), not 403.
- Shop APIs: the caller must be an ACTIVE member of the shop (`shop.t_shop_user`, role `ADMIN` or `STAFF`) or a platform administrator (a user with the role `PLATFORM_ADMIN` in `author.t_user_role`), else 403 `E10009`. Reuse the same three SQL queries by their names ("Check shop member", "Get the platform administrator role", "Check platform administrator") so they stay identical everywhere.
- A field the caller may not see (the platform's margin) stays in the response as `null`, so the shape does not change; say who sees it in a rule and make the example match.
- Public (storefront) APIs have no `authorization` header and no 401/403, never return cost, margins or private people data, and treat a shop that is not ACTIVE as not found.
- Sentences that record approval: "approved by the product owner" once the owner answered, "decided by the lead SA, pending product owner confirmation" before.

## Prototypes to copy

| Need | Copy |
|---|---|
| master table (name, description) | `doc/api/product/04`–`06` or `doc/api/shop/05`–`07` |
| table with a parent | `doc/api/product/07`–`09` |
| nested children (images) | `doc/api/product/01`–`03`, `doc/api/shop/08`–`10` |
| members / roles with a last-admin rule | `doc/api/shop/11`–`13` |
| lots, price and stock | `doc/api/shop/01`–`03` |
| public page | `doc/api/shop/04`, `14`, `16` |
| customer-owned row from the token | `doc/api/consent/04`, `doc/api/shop/15` |
| cart / checkout / order flow | `doc/api/cart/01`–`03`, `doc/api/sales/01`–`05` |
