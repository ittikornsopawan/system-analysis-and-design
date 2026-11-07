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

Folder: `e-commerce/doc/api/<group>/<NN>-<name>/` with `spec.md` and `sequence.wsd` (the diagram, built from the spec with `scripts/sequence_skeleton.py` and finished by the author, see "Sequence diagram" below); the number continues the group's numbering. Not every table needs all three (a table the system fills itself has only an inquiry; a customer-owned row like a review has no batch). Say why in the spec when you leave one out.

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

## Sequence diagram (`sequence.wsd`)

The diagram is the picture of the same behaviour that the spec states in words and SQL, so it must repeat every SQL block of the spec exactly: the table, the heading and the SQL letter for letter. The order is the order in which the work runs, not the order of the spec, and a block may appear in more than one branch (for example a row that is written in both branches). Build it, do not type it:

1. Run `python3 .agents/skills/api-contract-design/scripts/sequence_skeleton.py <spec.md> --write`. It writes `sequence.wsd` next to the spec (without `--write` it prints on the screen; it refuses to overwrite a file that already has content unless you add `--force`). The skeleton has the header of the login diagram, the participants (one `database` per table, in the order of the spec, which is also the order of first use because the skeleton keeps the blocks in the order of the spec), the handler line (`<Name>CommandHandler` when the spec has an INSERT, UPDATE or DELETE, `<Name>QueryHandler` when it only reads), and one block per SQL copied letter for letter. A write API has `BEGIN READ COMMITTED`, `COMMIT`, `ROLLBACK` and the 400 E10001, 408 E90001 and 500 branches; an inquiry has no transaction.
2. Replace every `' TODO(author): ...` comment with what only the author can decide: the checks in the order of the spec (400 -> 404 -> 403 -> 409 -> write) as `alt` / `else` branches, which database block runs on which branch, the lock (`SELECT ... FOR UPDATE`), the values that pass between steps and one response for each outcome. The comments under each marker list the execution order and the success and failure examples of the spec as hints. Keep the SQL in the notes exactly as the spec has it (a line that starts with a quote is written `&#39;` and the checker decodes it). Move each block to the place where the work runs it (the spec orders the SQL by table, not by execution, so for example a permission check that is written after an UPDATE in the spec runs before it) and copy a block into every branch that needs it. Every block of the spec must stay in the diagram at least once, no block may be added that the spec does not have, and the checker reads a block by its table, heading and SQL, so a changed heading or a changed letter counts as a missing block. When you move blocks, move the `database` participant lines too: they must be the tables of the spec, declared in the order in which the diagram uses each table for the first time.
3. Run `python3 e-commerce/db/tests/check_docs.py api-sequence-spec`. No `' TODO(author)` marker may stay in a finished diagram (`grep -rn "TODO(author)" e-commerce/doc/api` must print nothing).
4. Two things only the picture shows: a SQL line with two `--` (a comment after a commented-out line) is drawn struck through by PlantUML, and the script prints a warning for it; render the diagram when the warning appears and ask the lead SA whether to reword the spec line.

`python3 .agents/skills/api-contract-design/scripts/test_sequence_skeleton.py` tests the script against every spec of the repository and against the hand-written diagrams; run it after you change the script, and mutation-test the script with `../data-modeling/scripts/mutation_harness.py` (the check is that test file).
