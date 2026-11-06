---
name: data-modeling
description: Design or change a database table in the e-commerce project the way the lead SA does it — migration SQL (CREATE TABLE edited in place, never ALTER), schema doc, README counts, ER diagram, and SQL tests written red-then-green, with the checkers run and mutation-tested. Use whenever the user asks to add or change a table, column, constraint, index, foreign key or unique rule, to fix a schema doc or ER diagram, or says "สร้าง/แก้ schema", "เพิ่มตาราง/คอลัมน์", "migration", "ER diagram", "ตาราง", even if they do not say "data modeling". Also use before writing an API spec that needs a new column, so the schema is settled first.
---

# Data Modeling (schema, migration, ER, SQL tests)

This is the method for any change to the database design of a project (the e-commerce project's files are named below). The project is in the **design phase**: the migrations have not run on a real database, so a table is changed by editing its `CREATE TABLE`, and the documents (schema doc, README, ER diagram) must always say the same thing as the migration. Four checkers enforce that, which is why the steps end with running them.

Load first: `.agents/README.md`, `.agents/rules/global.md`, `.agents/knowledge/projects/e-commerce.md`. The project's own templates override the generic ones in `.agents/templates/`.

## Inputs you need before starting

- The tables and columns to add or change and the business reason. If a rule is a business decision you cannot read from the repo (who may delete, whether a value may repeat, what a status means), ask the owner, or choose the safest option and record it as a decision (step 3).
- The current state: read the real migration (`e-commerce/db/migrations/up/NN-<schema>.schema.up.sql`), the table's schema doc in `e-commerce/doc/schema/<schema>/`, and the specs in `e-commerce/doc/api/` that use the table. A column you think is unused may be read by a spec.

## Procedure

1. **Inspect.** Read the migration, the schema doc, the README row, the ER rows and every spec that mentions the table (`grep -rn "<table>" e-commerce/doc e-commerce/db`). Note default values, checks and unique rules. Existing user changes in the worktree stay untouched.
2. **Write the decision list.** One line per rule that is not obvious from the request (see `references/verification-and-reporting.md` for the format). Ask the owner about anything that changes data or behaviour. Changing something already delivered (a table another spec relies on) needs the owner's yes first, because it reaches many specs.
3. **Write the SQL test first (RED).** Copy `assets/sql-test.test.sql.tmpl` to `e-commerce/db/tests/NN-<name>.test.sql`, pin each new rule, run `bash e-commerce/db/tests/run_db_tests.sh` and watch your test fail for the right reason (`references/sql-tdd.md`). A test that never failed proves nothing.
4. **Change the migration (GREEN).** Edit the `CREATE TABLE` in place, starting from `assets/migration-table.sql.tmpl` for a new table. Rules and naming: `references/schema-conventions.md`. Run `run_db_tests.sh` again until it prints `ALL PASSED`.
5. **Bring the documents in line.** The schema doc (`assets/schema-doc.md.tmpl` is the shape; its SQL block must equal the migration statement), the README row and counts, and the ER diagram (`references/er-diagram.md`). Realign any markdown table you touched with `scripts/realign_tables.py`.
6. **Render the ER diagram and look at it.** Do not trust the XML. Overlapping tables, a legend that sits on a table and wrongly coloured rows only show in the picture.
7. **Run every checker** and `audit_all.py` until `0 findings` (commands in `references/verification-and-reporting.md`).
8. **Mutation-test what you added.** Break the migration or the doc on purpose and confirm a test or checker fails (`scripts/mutation_harness.py`). If one slips through, fix the checker, not the mutation.
9. **Report** with `assets/decision-report.md.tmpl`: files changed, pasted results, each decision with why and what it costs if wrong, open questions. Do not `git add` or commit; the owner commits.

## Templates

The files in `assets/` end in `.tmpl` on purpose: they are copied verbatim into project files (which have no frontmatter) and the extension keeps them outside the Markdown frontmatter rule. Copy one to its real name and fill the `<...>` placeholders. `assets/schema-doc.md.tmpl` is a snapshot of `e-commerce/doc/schema/template.md`, which stays the project's source of truth.

## Outputs

The edited migration (up, and down when a table is added or dropped), the schema doc, the README, the ER diagram, a `*.test.sql` file, and the report. Nothing is committed.

## Done when

- `run_db_tests.sh` prints `ALL PASSED` (migrations up, down, up again, and every test file) and the new test failed before the change.
- Every `check_docs.py` sub-command is OK and `audit_all.py` says `0 findings`.
- The ER diagram was rendered and looked at.
- The report lists every decision you made yourself.

## Pitfalls that already happened

A comma before `);` breaks a migration; `order` is a reserved word (the order schema is `sales`); a plain `UNIQUE` blocks reusing a name after a soft delete; two tables that point at each other cannot be created; a README count edited by hand drifts. The full list with the reasons is in `references/schema-conventions.md`.
