---
name: Task Plan
description: Shared checklist for planning and tracking non-trivial tasks without overwriting work belonging to another project or task.
---

# Task Plan

Use one section per task, named `<scope>: <task-name>`. Preserve other task sections and mark an item complete only after its completion criterion is satisfied.

## repository-wide: Make agent instructions operational

Status: Complete

- [x] Audit `AGENTS.md`, `CLAUDE.md`, and referenced agent resources.
- [x] Resolve task artifact, loading order, active scope, approval evidence, new-spec planning, and placeholder-role decisions.
- [x] Create task tracking, lessons, and canonical terminology documents.
- [x] Align root instructions, rules, workflow, registry, and ready spec templates.
- [x] Verify frontmatter, resource references, parity, numbering, and instruction consistency.
- [x] Record the final verification result and mark this task complete.

Verification: All 32 governed Markdown files have valid required frontmatter; root instructions match apart from runtime-specific names; workflow numbering is 1–14; all required resources exist; scope and approval rules are consistent; `git diff --check` passes.

## repository-wide: Fill the data-modeling and api-contract-design skills

Status: Complete

- [x] Inspect the registry, the placeholder skills, the project templates, and the conventions used in the e-commerce schema and API work.
- [x] Write `data-modeling` (schema, migration, ER diagram, SQL tests) with references, templates, and scripts.
- [x] Write `api-contract-design` (upsert, batch, inquiry specs, checkers) with references, template, and a spec generator helper.
- [x] Register both skills as ready in `.agents/README.md`.
- [x] Test the scripts and validate the frontmatter of every new Markdown file.

Verification: both `SKILL.md` files and all seven references have valid frontmatter; `realign_tables.py`, `mutation_harness.py`, and `spec_helpers.py` were run against real inputs; `spec_helpers.py` output passes the checker's table and JSON checks. The skills have not been run against test prompts with a baseline.

## repository-wide: Write the commit-and-pr skill

Status: Complete

- [x] Ask the user which formats must be fixed, the language, the subject style, and how to treat files of other tasks.
- [x] Write `commit-and-pr` (Conventional Commits in English, fixed PR title and body, fixed chat summary, pre-send checklist) with references and `.tmpl` templates.
- [x] Write and test `scripts/preflight.py` (branch, files by area, secrets, large files, junk, `git diff --check`, optional project checkers).
- [x] Register the skill as ready in `.agents/README.md`.

Verification: `preflight.py` flagged every planted problem in a scratch repository (main branch, secret, private key, 1.2 MB file, build output, trailing whitespace) and passed a placeholder bearer token and a clean file; `--run-checks` ran 22 `check_docs.py` sub-commands, `audit_all.py` (0 findings) and `run_db_tests.sh` (ALL PASSED) on the real repository. The skill has not been run against test prompts with a baseline, and nothing was committed.

## repository-wide: Define independent Component Repository standard

Status: Complete

- [x] Inspect the current `e-commerce/repository/` ownership and references without moving files.
- [x] Decide the manifest-managed independent repository model, naming, revision, ignore, and migration boundaries.
- [x] Create the Component Repository rule, Repository Manifest template, bootstrap skill, ADR, and canonical glossary terms.
- [x] Register the new resources and update root structure, SDD implementation routing, and e-commerce migration status.
- [x] Validate the skill package, frontmatter, manifest contract, routing parity, references, and unchanged e-commerce backend layout.
- [x] Record verification and mark this task complete.

Verification: isolated forward tests covered a valid staged clone, a dirty existing checkout, a migration-pending Project, and a revision outside the declared default branch; declared targets and existing work were preserved and staging directories were cleaned. Ruby fallback validation passed for skill structure and YAML because the bundled Python validator could not import PyYAML. Root instruction parity, workflow numbering, registry entries, ADR, manifest fields, full-SHA and remote safety instructions, e-commerce migration state, and `git diff --check` all passed. No `e-commerce` backend file was moved and no nested Git metadata or `e-commerce/REPOS.md` was created.

## e-commerce: Master tables WP6 (product type, product brand, consent type)

Status: Complete, reviewed by the lead SA (gates 1 and 2), waiting for the product owner to merge the pull request

- [x] Write `docs/superpowers/specs/2026-11-06-master-tables-design.md` (decisions B1 to B14) and get the owner's answers on permission (Q1) and the foreign key change (Q4).
- [x] Write `db/tests/03-product-master.test.sql` and `db/tests/00-consent-type.test.sql` first and watch them fail on the old migrations.
- [x] Change migrations `00-common` and `03-product`: partial unique name indexes, `RESTRICT` on `m_product.type_id`, `m_product.brand_id` and `t_consent.consent_type_id`, with no `ALTER TABLE`.
- [x] Update the five schema docs and the ER diagram (the `UK name` rows of the three tables).
- [x] Write nine specs: `product/10` to `15` and `consent/06` to `08` (upsert, batch and inquiry; upsert and batch need `PLATFORM_ADMIN`).
- [x] Add the checkers `product-master-spec`, `product-master-schema`, `consent-type-spec`, `consent-type-schema` and mutation-test them.
- [x] Run every checker, the audit and the database tests after rebasing on `origin/main`.

Verification: `check_docs.py` 30 sub-commands OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED. The new checkers caught 105 of 105 deliberate faults after the first run missed 6 and was tightened; the migrations caught 9 of 9. Tests 4 of the product file and 5 of the consent file were not seen failing before the migration change (the script stops at the first error of a file); their sharpness was shown by restoring `CASCADE`. ER pages Overview and All Tables were not looked at as pictures by the author; the lead looked at the Product page. Nothing was run against a real database beyond the throw-away test cluster.
