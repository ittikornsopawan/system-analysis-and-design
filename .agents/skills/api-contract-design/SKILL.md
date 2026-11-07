---
name: api-contract-design
description: Write or change an API spec in the e-commerce project the way the lead SA does it — the three-endpoint set (upsert, upsert batch, inquiry) per table, HTTP codes, bizCodes, permission and public-API rules, SQL in every spec, checked by check_docs.py and audit_all.py and mutation-tested. Use whenever the user asks to create, review or fix an API spec, endpoint, request/response example, error code, "API spec", "สร้าง/แก้ API", "upsert", "batch", "inquiry", "spec.md", or to add a checker for a spec, even if they do not say "contract". If the API needs a new column or table, run the data-modeling skill first.
---

# API Contract Design (spec per endpoint)

The API specs are the contract that the C# backend will implement, so every behaviour a developer would otherwise have to guess must be written down: the exact HTTP code, the error code, the order of checks, the SQL that touches each table. The project is in the design phase and the output is documents, so correctness is proved by the checkers and by deliberately breaking them, not by running a server.

Load first: `.agents/README.md`, `.agents/rules/global.md`, `.agents/knowledge/projects/e-commerce.md`. `e-commerce/doc/api/template.md` is the project's template (copy in `assets/api-spec.md.tmpl`) and overrides `.agents/templates/api-spec.md`.

## Inputs you need before starting

- The table(s) the API works on and the rules the business wants. Read the real migration and schema doc; a spec SQL that names a column that does not exist fails `audit_all.py`.
- The neighbouring specs: the prototype you will copy (table in `references/api-conventions.md`), and any spec that already touches the same tables (shared rules, error codes, and queries must stay identical).

## Procedure

1. **Inspect and pick a prototype.** Read the schema, then choose the closest existing spec folder (simple master table, table with a parent, table with nested children, public page, permission-guarded write). **Copy the whole folder** and edit it; do not write from scratch. Sentences and SQL that were already reviewed are worth reusing.
2. **List the rules to decide** (who may call, what makes a 409, what happens on delete, what is public, what is hidden). Ask the owner about anything that changes behaviour or data; decide small things yourself and record them (`../data-modeling/references/verification-and-reporting.md`). Changing a delivered spec needs the owner's yes because it reaches several endpoints.
3. **Settle the schema first.** If a rule needs a column, a unique index or a foreign key action, use the `data-modeling` skill (test red, then migration green) before the spec text, so the SQL in the spec has real columns.
4. **Write the three specs** (upsert, upsert batch, inquiry) following `references/api-conventions.md` for behaviour and `references/spec-structure.md` for the layout. `scripts/spec_helpers.py` generates the shared parts (tables, status objects, request blocks, error examples) so that they are identical in every file. Realign hand-written tables with `../data-modeling/scripts/realign_tables.py`.
5. **Draw the sequence diagram.** `python3 .agents/skills/api-contract-design/scripts/sequence_skeleton.py <spec.md> --write` builds `sequence.wsd` next to each spec with the SQL copied exactly; replace every `' TODO(author)` comment with the real branches, locks and responses of the spec, then run `check_docs.py api-sequence-spec`. No marker may stay (`grep -rn "TODO(author)" e-commerce/doc/api` prints nothing). Details in `references/api-conventions.md` (Sequence diagram).
6. **Make the examples agree with the rules.** Totals add up, ids match between request and response, the batch example shows `items[i]` in its errors, a public API shows no private field, and an example never breaks the rule written above it.
7. **Add the checker** as a new sub-command in `e-commerce/db/tests/check_docs.py` (`references/checker-patterns.md`) and register the status codes of the new endpoints in the existing `status-codes` / `biz-codes` checks where they apply.
8. **Run everything** (commands in `../data-modeling/references/verification-and-reporting.md`): all `check_docs.py` sub-commands, `audit_all.py` with `0 findings`, `run_db_tests.sh` when a schema changed.
9. **Mutation-test the checker** with `../data-modeling/scripts/mutation_harness.py`. Aim for every case caught; a slip means the checker is too loose.
10. **Report** with the decision-report template. State which rules are decided by the lead SA and which the owner approved, and write the approval sentence into the spec ("approved by the product owner"). Do not `git add` or commit.

## Outputs

`e-commerce/doc/api/<group>/<NN>-<name>/spec.md` and a `sequence.wsd` per endpoint (built with `scripts/sequence_skeleton.py` and finished by hand, no `TODO(author)` left), the new checker, any schema change with its tests, and the report.

## Done when

- Every endpoint of the set has a spec with all sections, every success and every error example, and SQL for every table it touches.
- Every `sequence.wsd` repeats the SQL of its spec exactly (`api-sequence-spec` is OK) and has no `' TODO(author)` marker.
- All `check_docs.py` sub-commands are OK, `audit_all.py` says `0 findings`, `run_db_tests.sh` says `ALL PASSED` if a schema changed.
- The new checker was mutation-tested and caught every case.
- The report lists every decision made without the owner and every open question.

## Where the detail is

- `references/api-conventions.md` — endpoint names, HTTP codes, bizCodes, upsert / batch / inquiry semantics, permission and public API rules, prototypes.
- `references/spec-structure.md` — required sections, formatting and SQL conventions, example hygiene.
- `scripts/sequence_skeleton.py` — builds `sequence.wsd` from `spec.md`; `scripts/test_sequence_skeleton.py` tests it against every spec.
- `references/checker-patterns.md` — how the checker for a new spec group is built and tested.
- `assets/api-spec.md.tmpl` — a snapshot of `e-commerce/doc/api/template.md` (the source of truth). It ends in `.tmpl` so that it stays outside the Markdown frontmatter rule, because the spec files it becomes have no frontmatter; copy it to `spec.md` and fill the placeholders.
