---
name: Schema Conventions
description: Rules for writing and documenting tables in the e-commerce project: standard columns, foreign keys, unique rules, checks, naming, and the four places that must agree. Read while designing or changing a table.
---

# Schema conventions

## Where each fact lives (all four must agree)

| Place | File | What the checker compares |
|---|---|---|
| Migration | `e-commerce/db/migrations/up/NN-<schema>.schema.up.sql` (down: `.../down/NN-<schema>.schema.down.sql`) | the source of truth |
| Schema doc | `e-commerce/doc/schema/<schema>/<table>.md` | column table, constraint table and the SQL block equal the migration |
| README | `e-commerce/doc/schema/README.md` | header "N tables in M schemas" and per table `Columns` and `FKs` counts |
| ER diagram | `e-commerce/db/er-diagram.drawio` | every column is drawn, every FK has an edge |

`audit_all.py` reads all four and reports every difference. Edit the migration first, then the other three.

## Table rules

- **Standard columns** on every table, in this order: `id UUID` primary key (`GEN_RANDOM_UUID ()`), `created_by`, `created_at`, `updated_by`, `updated_at`, `row_status` (`ACTIVE`, `INACTIVE`, `DELETED`, `LOCKED`, `ARCHIVED`, default `ACTIVE`). Rows are never removed: delete is `row_status = 'DELETED'`.
- **No `ALTER TABLE`.** Add the column or constraint to the `CREATE TABLE`. The audit rejects an `ALTER` in a doc, and a DO block that adds a constraint later is the same thing in disguise.
- **Foreign keys** use `ON DELETE CASCADE`, except where deleting the parent must not erase history: `RESTRICT` (examples: `sales.t_order_item.lot_id`, `sales.t_order.address_id`, `shop.m_shop.type_id`). Test the rule through `pg_constraint.confdeltype`.
- **Unique but reusable after a soft delete**: a partial unique index `CREATE UNIQUE INDEX IF NOT EXISTS uq_<table>_<columns> ON <schema>.<table> (<columns>) WHERE row_status <> 'DELETED'`. A plain `UNIQUE (...)` makes the second row with that value impossible forever. A row that is `INACTIVE`, `LOCKED` or `ARCHIVED` still holds its value; only `DELETED` frees it.
- **Rules between columns of one row** are a named table level check: `CONSTRAINT ck_<table>_<rule> CHECK (...)` (examples: margin rates add up to at most 100, `total_amount = total_price - total_discount + total_tax + total_shipping`, `selling_price >= cost_price`).
- **No circular foreign keys.** Two NOT NULL references pointing at each other cannot be created; cut one direction and let the other table point to the owner (a campaign has many budgets, so the budget points at the campaign).
- **Reserved words** cannot be schema or table names (`order` became `sales`).
- **Types**: money `NUMERIC(16, 2)`, rates `NUMERIC(8, 2)`, personal data that must be encrypted `BYTEA`, free text `TEXT`.
- **Configuration is not schema.** Limits such as "at most 100 cart lines" or "a payment window of 30 minutes" live in the spec as a config value, not in a column or a check.
- **Copy of data that must not change later** (the shipping address of an order) is stored on the row, not read through the foreign key.
- A trailing comma before `);` kills the migration and happened twice. Run `run_db_tests.sh` after every SQL edit.

## Schema doc (`e-commerce/doc/schema/<schema>/<table>.md`)

Start from `assets/schema-doc.md.tmpl` or copy a neighbouring table's file.

- `Columns` table: one row per column, key (`PK`, `FK`, `UQ`), reference link for a foreign key, type, length, nullability, description, example. Put a rule that a column carries (range, default) in its description.
- The constraint table is headed `## Constain` in the template. Keep that spelling, the checker matches it. Name inline constraints descriptively (`ck_<table>_<column>`); for a partial unique index use the index name.
- The SQL block is the exact `CREATE TABLE` statement plus the `CREATE INDEX` statements of the migration (whitespace is normalised, nothing else). Paste it from the migration after the migration is final. A statement that is in the doc but not in the migration is a finding.
- Realign the tables with `scripts/realign_tables.py`; do not pad by hand.

## README (`e-commerce/doc/schema/README.md`)

The header sentence holds the table count (`52 tables in 11 schemas`). Each table row is `| [name](path) | Master / Transaction / Log | <column count> | <FK count> |`. Change the numbers only after the migration is final and re-run the audit; do not guess them.

## Adding a whole new table

New migration statement (and a `DROP TABLE` line in the down file, in reverse dependency order), new schema doc, README row and count, ER table (a new swimlane on its schema page and on "All Tables"), a test file. The down file must still run cleanly after the up file; `run_db_tests.sh` does up, down, up again.
