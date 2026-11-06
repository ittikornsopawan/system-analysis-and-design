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

## repository-wide: Select the minimum SDD agent set

Status: Complete

- [x] Map the roles and phase responsibilities required by `.agents/workflows/spec-driven-development.md`.
- [x] Inventory relevant candidates in `awesome-claude-code-subagents/categories`.
- [x] Compare the minimum candidate agents with the repository's existing agent files and terminology.
- [x] Present the recommended initial agent set, gaps, and decisions for user confirmation.
- [x] After confirmation, identify the exact content to adapt from each selected source file.
- [x] Adapt the six canonical SDD agent roles with `model: inherit` and explicit boundaries and handoffs.
- [x] Build the System Analyst as the specification, traceability, and SQL-analysis lead.
- [x] Add Security Auditor as an optional specialist for security-sensitive work.
- [x] Register the seven roles and document the optional security-review trigger in the SDD workflow.
- [x] Verify frontmatter, registry consistency, role boundaries, source-specific boilerplate removal, and clean Markdown diffs.

Verification: all seven selected agent files have valid YAML frontmatter, matching path/name, explicit tools, and `model: inherit`; every selected role is registered `ready`; imported context-manager protocols, fixed models, arbitrary thresholds, fake delivery metrics, and unselected agent dependencies are absent; the System Analyst includes project-backed PostgreSQL, transaction, constraint, index, and query-specification expertise while excluding DBA operations; `git diff --check` passes. The pre-existing unregistered agent copies were left untouched, and no build or runtime test was required for this documentation-only change.

## repository-wide: Add the pre-implementation OpenAPI role

Status: Complete

- [x] Remove unregistered agent copies that are outside the approved SDD team.
- [x] Adapt API Documenter to publish OpenAPI 3.1 from Approved API Specs into the project API contract.
- [x] Insert API Documenter between architecture approval and backend implementation.
- [x] Register API Documenter as ready and align System Analyst, Backend Developer, and Code Reviewer handoffs.
- [x] Verify frontmatter, registry and workflow consistency, JSON validity, preserved unrelated work, and clean Markdown diffs.

Verification: the eight selected Agent Roles have valid frontmatter, matching names and paths, `model: inherit`, and `ready` registry rows; the SDD workflow has nine sequential phases with API Documenter publishing the contract before implementation; System Analyst, Solution Architect, Backend Developer, and Code Reviewer handoffs reference OpenAPI consistently; `e-commerce/api/api-contract.json` parses as JSON; `git diff --check` passes. No semantic OpenAPI validator is configured in the repository, so the role reports semantic validation as unverified until a validator is available.
## e-commerce: Authentication WP4 (tokens, refresh, logout, reset password, profile, address)

Status: Complete, reviewed by the lead SA (gate 1, gate 2 and one re-check), waiting for the product owner to merge the pull request

- [x] Write `docs/superpowers/specs/2026-11-06-authen-design.md` (decisions U1 to U29) and get the owner's answers on token lifetime, login lock, logout scope, scope of work, field encryption and the unique indexes on delivered tables.
- [x] Write `db/tests/01-authen.test.sql` first and watch it fail on the old migration.
- [x] Change migration `01-authen` (up and down): `session_id` on both token tables, four partial unique indexes, the new log table `authen.l_user_login_attempt` (53 tables), with no `ALTER TABLE`.
- [x] Update seven schema docs, the README counts and the ER diagram (Common and Authen page and All Tables page).
- [x] Write eight specs `03` to `10` and change `01-register` and `02-login` (plain text over TLS, session and token rows, login lock, token lifetime, default address).
- [x] Add the checkers `authen-spec` and `authen-schema`, extend `audit_all.py` to plain indexes, and mutation-test them.
- [x] Run every checker, the audit and the database tests after rebasing on `origin/main`.

Verification: see the pull request. The authen checkers caught 120 of 120 deliberate faults and the migration 10 of 10 according to the author; the lead did not rerun them. Tests 2 to 6 of the SQL file were not seen failing before the migration change (the script stops at the first error of a file); their sharpness was shown by deliberate migration faults. Nothing was run against a backend or a real database; the existing backend differs from the specs in endpoint paths and token lifetime, as written in the design document.

## e-commerce: Shipping domain (WP3)

Status: Complete (PR #10 merged into `main` at `85e64de` on 2026-11-06); S3 was answered by the product owner (7 days, reported by the lead SA) and is written up in WP3b below

- [x] Read the shop-domain hand-off, roadmap WP3, order design R38–R50, migrations 06 and 08, schema docs, sales specs, and the data-modeling and api-contract-design skills.
- [x] Ask the product owner the business questions and agree the payment contract with the lead SA.
- [x] Write `docs/superpowers/specs/2026-11-06-shipping-design.md` (round 1) and get the product owner's approval.
- [x] Round 2: `08-shipping.test.sql` red then green, migration 08, schema docs, README, ER diagram pages 6 and 8 rendered and viewed.
- [x] Round 2: six specs in `e-commerce/doc/api/shipping/` and the `shipping-schema` and `shipping-spec` checkers, mutation-tested.
- [x] Rebase onto `main` after the payment work, pass the lead SA's gate 2, commit and open the PR with the `commit-and-pr` skill.
- [x] S17 to S22 (decisions added during round 2) decided by the lead SA on 2026-11-06 (technical details, not an owner approval).
- [x] Product owner answers S3: an order completes by itself 7 days after `shipped_at` when the customer does not confirm (config, reported by the lead SA on 2026-11-06).

Verification: `check_docs.py` 26/26 OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED. Checkers were mutation-tested on a copy of the merged tree: spec 58/58, schema doc, README and ER 8/8, migration 10/10 through the checker and 10/10 through `run_db_tests.sh`, audit 8/8 (the audit run was before the last rebase). No backend was run against the specs.

## e-commerce: Campaign and discount (WP7)

Status: Round 2 done, reported to the lead SA for gate 2 (round 1 approved by the product owner on 2026-11-06 at 13:00:05Z); not committed

- [x] Round 1: `docs/superpowers/specs/2026-11-06-campaign-design.md` with decisions C1 to C16 and proposals E1 to E8.
- [x] `09-campaign.test.sql` extended to tests 1 to 11 and red before the migration change (`column "remaining" ... does not exist`), green after.
- [x] Migration 09 edited in place (period check, unique name, `remaining`, ledger `entry_type` and `order_id`, product target check, partial unique indexes, discount checks); schema docs, README counts, ER pages 7 and 8 rendered and viewed.
- [x] Three specs in `e-commerce/doc/api/campaign/`: upsert campaign, inquiry campaign, inquiry campaign ledger.
- [x] `campaign-schema` and `campaign-spec` checkers added before `def main` in `check_docs.py`.
- [x] E1 to E7 in the delivered specs: `sales/01`, `sales/02` (discount rules, budget reservation, lot order by `id`, campaign examples), `sales/05`, `payment/05`, `payment/02` (budget release), `shop/08–09`, `product/01`, `03`, `04`, `06` (delete blocked while in a running campaign); `order-spec` changed on purpose for the discount examples.
- [x] Mutation-test the new and the changed checkers with deliberate mistakes (campaign-schema, campaign-spec, order-spec): spec 48/48 (includes the delivered-spec effects and 5 order-spec cases), doc, README, ER and test file 8/8, migration through the checker 11/11 and through `run_db_tests.sh` 11/11 (10/11 first, SQL test 6 was tightened for an INACTIVE budget), audit 10/11 (the miss is an audit limitation, covered by a needle).
- [x] Full run after the mutation work: every `check_docs.py` sub-command OK, `audit_all.py` 0 findings, `run_db_tests.sh` ALL PASSED (preflight with `--run-checks`); the ER file did not change after it was rendered and viewed.
- [x] Report gate 2 to the lead SA (new WP7 files separate from the delivered files that were edited).
- [x] Gate 2 result: passed with one fix (an example where the cap cuts a `FIXED_AMOUNT` discount): `sales/02` now has the Discount Example table and `Success - With Capped Discount`, `campaign-spec` checks the cap and the profits, 8/8 deliberate mistakes caught.
- [ ] Wait for the lead SA to say that PR #12 is merged, then fetch and rebase once (no rebase before that), and wait for the owner's order to commit.

Verification: `preflight.py --base main --run-checks`: `check_docs.py` 28/28 OK, `audit_all.py` 52 tables 0 findings, `run_db_tests.sh` ALL PASSED (tests 1 to 11 of `09-campaign.test.sql`), no blockers. No backend was run against the specs.

## e-commerce: Shipping automatic completion (WP3b)

Status: Not started (starts after WP7 round 2, no hurry; the lead SA asked for it on 2026-11-06 after the owner answered S3)

- [ ] Write an appendix to `docs/superpowers/specs/2026-11-06-shipping-design.md` with decisions S23 and up: which orders qualify (PROCESSING, every item allocated in shippings that are SHIPPED or DELIVERED, no PENDING shipping left, latest `shipped_at` older than 7 days) and the stuck case of a partial shipment.
- [ ] Decide the effect on the shipping rows (the system sets SHIPPED to DELIVERED as `system`, or a separate state) with the cost if wrong.
- [ ] Decide the lock order (order row first), the clash with refund and with S9, and where the rule is written (spec 06 or a new job section, not an endpoint) as a proposal to the lead SA because spec 06 is already merged.
- [ ] Send the document to the lead SA for gate 1 before any change to a spec, schema or checker.

## repository-wide: Add named-agent workspace lifecycle

Status: Complete

- [x] Persist the user-approved named-agent workspace design and its approval evidence.
- [x] Add the named-agent rule, canonical team registry, workspace ignore, and matching Codex/Claude routing.
- [x] Implement the `agent-workspace` skill and deterministic lifecycle script.
- [x] Add isolated tests for registry authority, path safety, locking, clone preparation, and merged-PR parking.
- [x] Align `commit-and-pr` and supersede the conflicting dated team protocol without changing merge authority.
- [x] Validate skill structure, Markdown frontmatter, routing parity, registry references, script behavior, and diffs.
- [x] Record verification evidence and mark this task complete.

Verification: `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 12 tests, covering registry authority from `origin/main`, scope-bound delivery preflight, cleared-marker bypass prevention, symlink and linked-worktree rejection, execution locking, baseline contamination, open PRs on any base, cross-repository PR rejection, clone preparation, and squash-merge parking while preserving the remote branch. Independent forward review found no remaining P1/P2 issues. Team registry YAML, 11 modified Markdown frontmatters, and `AGENTS.md`/`CLAUDE.md` parity passed. `git diff --check` passed. The bundled `quick_validate.py` could not start because PyYAML is not installed; an equivalent Ruby YAML fallback passed its frontmatter, allowed-key, naming, description, and unfinished-placeholder checks.
