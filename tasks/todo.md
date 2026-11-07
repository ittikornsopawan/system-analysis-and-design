---
name: Task Plan
description: Shared checklist for planning and tracking non-trivial tasks without overwriting work belonging to another project or task.
---

# Task Plan

Use one section per task, named `<scope>: <task-name>`. Preserve other task sections and mark an item complete only after its completion criterion is satisfied.

## e-commerce: Jinny architecture diagrams

Status: Registration prepared and verified locally; diagram creation waits for registration on origin/main. Ittikorn requested Jinny and three diagrams on 2026-11-07, then explicitly chose to register Jinny and use the diagram-design default light style. Ittikorn subsequently authorized commit, push, and a registration PR in this chat. That direct delivery authorization covers registration only; the future diagram assignment retains delivery: none.

- [x] Read the bootstrap, applicable rules, lessons, diagram-design skill, existing diagram payload, backend project structure, project references, and relevant payment/shipping specifications.
- [x] Register Jinny with a dedicated diagram designer role, reporting to Josh, repository-wide scope for diagram assignments and required task bookkeeping, and no delegation capabilities; validate the role, registry, and existing workspace tests.
- [x] Obtain direct user authorization for registration delivery; prepare the registration branch and PR package, preserving unrelated handoff files. Merge remains the owner's action.
- [ ] After registration reaches origin/main, prepare Jinny's managed workspace with an assignment limited to `e-commerce/diagram/` and required task bookkeeping; delivery remains none.
- [ ] Record the visual plan before drawing: architecture overview, backend request architecture, and system/domain context; `doc-wide` 1280 x 720, engineer audience, default light style, at most nine functional nodes per image.
- [ ] Create self-contained HTML sources and editable draw.io PNGs for `architecture-design`, `repository-architecture`, and `system-design`, based on inspected evidence without introducing architecture changes; mark specification-only capabilities explicitly.
- [ ] Run skill self-checks, inspect connector geometry and text bounds, reopen embedded draw.io models, render and visually review all three final PNGs, and document any merged or omitted source content.
- [ ] Deliver the three requested files with verification evidence and any unresolved limitations.

Evidence: `architecture-design.drawio.png` and `system-design.drawio.png` are zero-byte files; the extractor reports `not a draw.io file (no mxfile, mxGraphModel, or payload)` for each. `repository-architecture.drawio.png` contains eight functional components plus decorative cells and legend edges. The current backend implements Authen in five .NET 10 projects; broader payment and shipping capabilities are described in specifications and must not be presented as implemented code. Jinny is absent from the inspected origin/main registry. Registration must be effective on origin/main before managed-workspace mutation begins, per `.agents/rules/named-agent-workspaces.md`.

Registration verification: `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 13 tests, including Jinny's role, enabled registry lookup, reporting line, workspace key, and inability to delegate delivery. Role frontmatter and registry pointer checks passed; `git diff --check` passed. No diagrams have been modified, rendered, or claimed as verified. Existing unrelated untracked handoff files were preserved.

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

Status: Round 2 done and reported to the lead SA for gate 2 (gate 1 passed on 2026-11-07 with two fixes, both done); not committed. Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `feat/tommy-shipping-auto-complete`.

- [x] Prepare the managed workspace (registry scope of `tommy` widened by PR #18; baseline `audit_all.py` 0 findings and `run_db_tests.sh` ALL PASSED).
- [x] Appendix S23 to S32 in `docs/superpowers/specs/2026-11-06-shipping-design.md` (eligibility, stuck partial shipment, effect on the rows, lock order and clashes, where the rule is written, the scan index, the `deliveredAt` wording); C17 to C22 of the campaign design relabelled as decided by the lead SA.
- [x] Gate 1 fixes: the partial index `ix_t_shipping_shipped_at` (S31, SQL test 7 red then green, migration 08, schema doc) and `deliveredAt` as "the customer or the system confirmed" in `shipping/04`, `05`, `06` (S32).
- [x] Spec `shipping/06`: Automatic Completion Rules, the Automatic Completion Example (7 cases) and three queries; the seven days are inclusive (a shipping that is exactly 7 days old qualifies).
- [x] Checkers: `shipping-spec` (needles, `deliveredAt` wording, the example is judged again with the five conditions) and `shipping-schema` (the index, test 7); mutation-tested with deliberate mistakes.
- [x] Run every `check_docs.py` sub-command, `audit_all.py` and `run_db_tests.sh`.
- [x] Gate 2 fix (lead SA, 2026-11-07): the scan query of the job now applies conditions 1, 2, 4 and 5 (a dead-end order no longer fills the batch and starves the others); S26, the rules, the example text and the checker `check_shipping_scan_query` (12 mutations caught) are updated.
- [ ] Gate 2 result of the fix: the lead SA reads the short result; then merge the current `main` into the branch, commit and open the PR with `commit-and-pr` from `.workspace/tommy` (delivery is authorized), without merging.

Verification: see the gate 2 report; mutation tests on a copy of the tree: spec 30/30, schema doc and test file 3/3, migration through the checker 4/4 and through `run_db_tests.sh` 4/4. No backend was run against the specs.

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

## e-commerce: WP5 author permissions (5a, 5b, 5c)

Status: 5a complete and rebased on the current `main`, waiting for gate 2 of the lead SA; 5b is deferred and 5c is planned (the product owner told the lead SA to stop after 5a until he gives the next order)

Governing spec: `docs/superpowers/specs/2026-11-06-author-design.md` (approved by the product owner through the lead SA, 2026-11-06). Worktree `.claude/worktrees/author`, branch `feat/author-permissions`.

5a (now): role, permission, scope, user role, me, seed

- [x] Write `db/tests/02-author.test.sql` and `db/tests/02-author-seed.test.sql`, run them against the old migration and see them fail.
- [x] Change `02-author.schema.up.sql` (partial unique names and pairs, role scope points at the permission scope, `t_user_permission.permission_scope_id`, `RESTRICT` to the master tables) until `run_db_tests.sh` prints `ALL PASSED`.
- [x] Write `e-commerce/db/seed/author.seed.sql` (role `PLATFORM_ADMIN`, scopes, permission list; idempotent, creates no user) and `grant-platform-admin.sql` (first administrator by `userId`, only when no ACTIVE holder exists).
- [x] Update the 8 schema docs, the README (`t_user_permission` 9 columns and 3 foreign keys), the ER diagram (rendered and looked at), and record the `seed` folder in `e-commerce/doc/schema/README.md`.
- [x] Write specs `author/01`–`12` (role, permission, scope: upsert, batch, inquiry; user role: upsert, inquiry; me).
- [x] Add `author-spec` and `author-schema` to `check_docs.py` before `def main` and mutation-test them (every deliberate mistake caught).
- [x] Run every `check_docs.py` sub-command, `audit_all.py` (0 findings) and `run_db_tests.sh`; send the gate 2 report to the lead SA.

Verification: on `main` at 553c8f4 plus this change: all 34 `check_docs.py` sub-commands OK, `audit_all.py` 53 tables 0 findings, `run_db_tests.sh` ALL PASSED (including `02-author` 6 tests and `02-author-seed` 4 tests). Deliberate mistakes: 142 of 142 caught by the two new checkers (including the grant-only ACTIVE rule of the user role spec), 15 of 15 caught through the SQL tests (migration, seed and grant script). The first administrator command was tested one after another, not with two sessions at the same time.

## e-commerce: WP5b author permission assignment (deferred)

Status: Deferred until an API enforces permissions (product owner chose the small scope, 2026-11-06)

- [ ] Specs `13`–`17`: role permission (upsert, inquiry), user permission (upsert, inquiry), check. The schema of these tables is already changed in 5a.

Verification: not started

## e-commerce: WP5c admin-only writes for delivered master data APIs

Status: Implemented and committed locally by the author (commit 05c7d4a in her managed workspace); the push was refused by the permission system of her session, so there is no pull request yet. Gate 2 of the lead is open. The lead wrote this section from the author's report because her assignment scope was `e-commerce` only.

- [x] Read the nine specs on `main` (with the WP7 changes of `product/01`, `03`, `04`, `06`) and find the checkers that cover them.
- [x] Add the `PLATFORM_ADMIN` rule, the 403 example and the two permission queries to `shop/05`, `06`, `product/01`, `03`, `04`, `06`, `07`, `09` and `consent/02`, and the two queries to the `consent/02` sequence diagram.
- [x] Add the checker `admin-write-spec`, narrow the leftover-word rule of `shop-type-spec`, and mutation-test every change (the author reports 150 of 150 caught).
- [x] Run every checker, `audit_all.py` and `run_db_tests.sh` (the author reports 38 of 38, 0 findings, ALL PASSED).
- [ ] Gate 2 of the lead, then push and open the pull request.

Verification: the numbers above are the author's; the lead has not rerun them yet.

## e-commerce: Payment WP2 (Stripe)

Status: Complete, merged in pull request 8

- [x] Write `docs/superpowers/specs/2026-11-06-payment-design.md` (rules R51 to R72) after the owner chose Stripe.
- [x] Write `db/tests/07-payment.test.sql` and change migration `07-payment` (provider, shipping method and fee, failure and refund columns, one live payment per order, `RESTRICT` on `order_id`).
- [x] Update the schema doc, the README and the ER diagram (pages 6 and 8).
- [x] Write five specs `payment/01` to `05` (start, Stripe webhook, inquiry for the customer and the shop, refund) and change `sales/01`, `sales/02`, `sales/05`.
- [x] Add the checkers `payment-spec` and `payment-schema` and mutation-test them.

Verification: when the pull request was opened `check_docs.py` passed 24 of 24, `audit_all.py` had 0 findings and `run_db_tests.sh` printed ALL PASSED. Nothing was run against Stripe; the Stripe event name for refunds and the THB 10 minimum are not confirmed against the Stripe reference.

## e-commerce: Lead review of the SA work packages

Status: In progress. Merged after the lead's review: WP3 shipping (pull request 10), WP6 master tables (11), WP4 authen (12), WP7 campaign (15), WP5 step 5a (17) and step 5c (20). Open work: WP3b (Tommy; gate 1 passed on 2026-11-07, round 2 in progress).

- [x] Review gate 1 and gate 2 of WP3, WP6, WP4, WP7 and WP5 5a and 5c, run the checkers in each analyst's tree and read the changed specs.
- [x] Fix the first team protocol so that the analysts write `tasks/todo.md` and `tasks/lessons.md` as `CLAUDE.md` requires.
- [x] Move the analysts' assignments to managed workspaces and widen the registry scope of tommy and marry (pull request 18) after the named-agent rule was merged.
- [x] Decide the 409 of `01-register` (owner on 2026-11-07: "เลือกให้เลย", the choice is the lead's). Decision: keep the 409 with its single message that does not say whether the username or the email exists, no change to the spec. Why: there is no email verification, so a neutral answer would leave a real user without a way to know why registration failed; the login answer is already the same for every failure and the lock limits guessing. Cost if wrong: add email verification and answer every registration the same way, which is a new work package. The registration rate limit belongs to the gateway and is not specified.
- [x] First platform administrator (owner on 2026-11-07, answered the lead's recommendation that the system operator runs `grant-platform-admin.sql` after confirming the user id: "แค่เก็บ data ไว้ เดี๋ยว dba มา export ให้การเงิน"). The lead reads this as: the database administrator is the system operator who runs the command, and the data is only stored, with no API for finance because the DBA exports it directly. This reading is not confirmed by the owner. Nothing in the specs changes.
- [ ] Review gate 2 of WP3b.
- [ ] Backlog for the owner's order: merge the two `er_name_rows` helpers of `check_docs.py` (check first that the API review did not already do it), extend `audit_all.py` to a column without an alias in the `WHERE` of an `UPDATE`, retrofit the plain `UNIQUE` and `CASCADE` of the older master tables, rewrite the team protocol in `docs/handoff/` to match the named-agent rule. Decided elsewhere: JWT claims are the authorization source (owner with Peter, 2026-11-07).

Verification: each gate was checked by running every `check_docs.py` sub-command, `audit_all.py` and `run_db_tests.sh` in the analyst's tree and by reading the changed specs. The analysts' own mutation tests were not rerun by the lead.


## repository-wide: Register Peter for the e-commerce API review

Status: Complete. PR #21 merged into origin/main at eee8add on 2026-11-07 (Asia/Bangkok); Peter's full managed clone was created and the first login assignment prepared through agent-workspace.

- [x] Read the bootstrap, global rules, team registry, named-agent workspace design, lessons, and delivery skill.
- [x] Confirm the owner chose to register Peter and retain the existing lifecycle rather than allow concurrent API pull requests.
- [x] Register Peter as an enabled System Analyst with the same repository-wide registry scope as the existing team, reporting to Josh, without delegation capabilities; bound actual assignments to e-commerce and required task bookkeeping.
- [x] Validate registry parsing and role/scope consistency, run the existing workspace tests and delivery preflight, and review the exact diff.
- [x] Prepare the commit and registration PR package using commit-and-pr; keep API changes out of this prerequisite PR.
- [x] After the owner merges registration into origin/main, create Peter's managed workspace with agent-workspace and record the bounded first-API assignment before edits.

Verification: The canonical registry test failed before adding Peter (expected four entries, found three). After registration, `python3 -B -m unittest discover -s .agents/skills/agent-workspace/tests -v` passed all 12 tests, including Peter's direct-user delivery authorization and inability to delegate. `preflight.py --base main` reported three in-scope files and no blockers; `git diff --check` passed. API/database tests were not rerun for this registry-only change. Registration takes effect only after merge into origin/main. The initial one-open-PR rule was superseded for this review by the owner's Q15 instruction; completed API PRs may stay open while Peter starts the next branch from main. Each API delivery will contain its spec.md and complete sequence.wsd, with the verification changes required for that API.


## e-commerce: Peter API review — login (API 1)

Status: Login artifacts verified and ready for one-API PR delivery. Owner confirmed Q1–Q13 and the additional Q14 ambiguity rule in this chat on 2026-11-07. Governing decisions are recorded in `docs/superpowers/specs/2026-11-07-api-review-design.md`; detailed endpoint changes remain in-review until reviewed. Assignment: Peter, System Analyst, delivery open-pr, authorized directly by ittikorn; branch `fix/peter-login-contract` in `.workspace/peter`.

- [x] Read all 30 APIs (60 files), identify SQL/sequence/approval contradictions, and settle the JWT and consent behavior with the owner.
- [x] Verify PR #21 merged, create Peter's managed clone, and prepare the bounded login assignment with the declared baseline checks.
- [x] Persist the exact owner-approved decisions and scope; reconcile superseded A16/A18 and token-design statements without marking detailed endpoint work approved.
- [x] Correct login SQL and specify the role/permission-specific scope payload, password verification, lock order, counter and transaction behavior.
- [x] Rewrite sequence.wsd with success, validation, REFUSED, FAILED, rollback and timeout branches and exact table-bound SQL.
- [x] Extend SQL/sequence and login-behavior checks; prove the old defects fail and mutation-test the changed checker.
- [x] Run every documentation check, SQL audit and database test; verify source structure and review the exact diff.
- [x] Prepare the one-login-API commit-and-pr package; verify actual PR/lock state through GitHub and agent-workspace during delivery.
- [x] Verify login PR #23 merged, park the completed workspace and prepare refresh as a fresh assignment. Subsequent APIs follow the owner's newer continue-without-merge instruction below.

Baseline: all 37 documentation subcommands passed, audit reported 53 tables and 0 findings, and database tests reported ALL PASSED during agent-workspace prepare. The initial PATH-only Java probe failed; the paired-review follow-up below discovered the installed OpenJDK and PlantUML JAR and records completed rendering verification.

Queue after login: refresh, then the remaining original 30 APIs and the additional APIs affected by JWT authorization. Each API owns one PR; after opening it, owner decision Q15 permits the next editing assignment from current main without waiting for merge. The existing registration worktree was retained because Codex's archive tool refused to remove the chat's primary checkout; Peter's API edits use only his managed full clone.

Login verification evidence: the new login-flow check rejected the old files before correction. Final mutation run caught 56/56 deliberate faults (the first 53-case run caught 48/53; selectors and projection/threshold checks were tightened before rerunning). The SQL and sequence now contain 15 exact operations and seven outcome paths. The delivery preflight ran 38/38 documentation checks, audited 53 tables with 0 findings, ran database tests with ALL PASSED, and found no blockers. PostgreSQL verification executed the specification's exact queries against adversarial role/direct-scope fixtures, empty arrays and ambiguous identifiers, proved token/attempt rollback, and used two connections to verify serialized counting. No backend or published OpenAPI was changed; the detailed login and revised WP4/WP5 documents remain in-review, while the separate owner-decision record is approved. The initial delivery did not render PlantUML; the paired-review follow-up below now records real rendering and visible-SQL verification.


### Login PR #23 — paired sequence/spec review follow-up

Status: Paired-review artifacts verified and ready for the existing PR update, resumed through agent-workspace with the original login assignment after the owner's 2026-11-07 correction. GitHub reported the PR OPEN when verified; no next API assignment has started.

- [x] Verify the PR changes both spec.md and sequence.wsd and rerun SQL parity and seven-path flow checks.
- [x] Find installed OpenJDK and the VS Code PlantUML JAR rather than treating the system Java launcher as proof that no runtime exists.
- [x] Render the source and reproduce that PlantUML omits SQL value lines beginning with a single quote, despite passing source parity.
- [x] Preserve all quoted SQL values in the rendered diagram and make decoded SQL parity and application/infrastructure exchanges explicit.
- [x] Add a scenario correspondence table and strengthen mutation checks for rendered SQL and request/result handoff gaps.
- [x] Render SVG/PNG, inspect the complete diagram and critical SQL/branch regions, and run paired source/flow/rendered-text checks.
- [x] Prepare the existing PR update with the observed before/after evidence; verify final delivery through GitHub and release the session lock.


Paired-review evidence: PlantUML -syntax reports SEQUENCE (19 participants); SVG and PNG were generated and visually inspected. The original SVG is rejected for missing 15/113 SQL lines; the corrected SVG has 113/113 visible SQL lines. Exact decoded SQL parity passes for the 18 existing source pairs, and login-flow verifies the seven outcomes plus all query requests/results, parameter mappings and four success fields. Mutation testing caught 67/67 faults. The complete preflight reran all 38 documentation commands, audited 53 tables with 0 findings and passed database tests; its first attempt also flagged an extra blank line at the end of this task file, which was removed before final delivery.


PR #23 integration: origin/main advanced to 01a5e41 with the already merged Jinny registration (#22) and administrator-write spec retrofit (#20). Reconcile this base into Peter's existing branch without force-pushing; preserve both login-flow and admin-write-spec in the checker. Verify the PR diff against the current main contains only Peter's recorded assignment paths, rerun all current checks and rendered SQL verification, then push the reconciliation commit and release the session lock. Imported main changes are base history, not additional APIs authored in this PR.

Integration verification: both checker registrations are present, all 39 documentation commands pass, the audit reports 53 tables / 0 findings, database tests report ALL PASSED, login mutations remain 67/67, and the rendered SVG still contains 113/113 SQL lines. The working-tree PR diff against the updated main was checked before the reconciliation commit: all eight changed paths match Peter's original assignment.


## e-commerce: Peter API review — refresh token (API 2)

Status: In progress. Login PR #23 merged at 9ae6b6d; branch `fix/peter-refresh-token-contract` was prepared in Peter's managed clone with all 39 baseline documentation commands, audit and database tests. Direct delivery authorization remains ittikorn.

Owner delivery override (2026-11-07): “เสร็จแล้วเปิด pr ทิ้งไว้เดียวฉันมาอ่าน ไม่ต้องรอ merge switch ไปที่ main แล้วเกิด brach ใหม่ได้เลย”. This supersedes the earlier one-open-PR/wait-for-merge choice and skill defaults for this API review. Finish each API, open its own PR, preserve the branch/assignment for review, return to updated main and begin the next API immediately. Keep explicit scope, one active editing session, clean transitions and no force pushes or PR merging. Do not ask again whether to continue after opening a PR.

- [x] Verify/park merged login, read refresh spec and sequence together, and prepare the scoped refresh assignment with passing baselines.
- [x] Persist the superseding delivery decision and capture the workflow lesson without changing unrelated team capabilities.
- [x] Correct refresh ownership lookup, user-first lock, post-lock token reread/time capture, single-use update, fresh claims and distinct old/new token hashes.
- [x] Rewrite sequence with every request/result, SQL, rotation, recent duplicate, older replay, invalid/expired/inactive, rollback and timeout outcome.
- [x] Add paired flow/SQL/render checks and mutation-test them; validate concurrent refresh/replay SQL in temporary PostgreSQL.
- [x] Render and inspect SVG/PNG; pass all documentation commands, audit, database tests and preflight.
- [x] Prepare the refresh-only commit-and-pr package with paired verification evidence and owner decision Q15. After opening, preserve its branch/assignment record and continue immediately on main; actual delivery state is verified through GitHub and the local history record.

Refresh verification so far: the old spec/sequence pair is rejected by refresh-flow. The corrected pair has 16 exact SQL operations, 10 outcome paths and 128/128 SQL lines visible in the rendered SVG. Mutations caught 44/44 (43/44 initially; the consume ownership check was tightened to require the WHERE user_id predicate rather than merely seeing userId in updated_by). Temporary PostgreSQL checks passed concurrent post-lock reread/recent duplicate, newly assigned role reads, single-use consume, older replay revoking both tables while preserving other sessions/users, atomic rollback, inactive user and expiry while waiting for the user lock.

Refresh delivery verification: preflight ran 40/40 documentation checks, audit 53 tables / 0 findings and database tests ALL PASSED. Its first run flagged a bytecode file generated by the temporary builder; only that generated file was removed, and all six intended task paths then passed. PlantUML syntax reports 17 participants; SVG/PNG were rendered and inspected, and refresh-flow confirms 128/128 visible SQL lines and ten outcome paths. No backend implementation or schema changes are included.

## e-commerce: Sequence phase 0 — api-sequence-spec checker for all 83 specs

Status: Implemented in the managed workspace of Marry on branch `feat/marry-sequence-checker`; the pull request is opened after the preflight and merged by the lead, not by the author. Scope: `e-commerce/db/tests/check_docs.py` and `tasks/`. No spec and no `sequence.wsd` is changed.

- [x] Remove the fixed list of 18 specs and the fixed list of directories; check every spec folder under `e-commerce/doc/api` and require a `sequence.wsd` in each of them.
- [x] For every non-empty `sequence.wsd`: the SQL is identical to the spec, the lifecycle (activate, note, return, deactivate) is complete and the database participants are in the order of the spec.
- [x] Add `REQUIRED_GROUPS` (`authen-and-author`, `consent`) that must have no empty file; other groups may be empty (pending) and the output prints filled/total per group.
- [x] Add the structure check modelled on `02-login`: `@startuml`, title, `skinparam` Sarabun, `hide footbox`, actor `User`, boxes Frontend / Web API / Database, participant chain API -> Application -> Domain -> Infrastructure, the handler line and no `TODO(author)` marker.
- [x] Add the login standard for every spec with INSERT, UPDATE or DELETE (BEGIN, COMMIT, ROLLBACK, HTTP 400 `E10001`, HTTP 408 `E90001`, HTTP 500) with the explicit named list `LEGACY_SEQUENCES` for the 10 diagrams that do not follow it yet.
- [x] Mutation-test the checker: 35 cases of `mutation_harness.py` and 10 special cases (empty file, only blanks, missing file, pending group, moved BEGIN, moved COMMIT, TODO marker).
- [x] Run every `check_docs.py` sub-command (40), `audit_all.py` and `run_db_tests.sh`.
- [ ] Preflight, commit, push, open the pull request, tell the lead; hold the lock until the merge, then release and park.

Verification: `api-sequence-spec` prints `OK: api-sequence-spec (83 specs; ... 10 legacy without the login standard)`; harness 35 of 35 caught; special cases 10 of 10 as expected after the BEGIN case was rebuilt (see the lesson of 2026-11-07); 40 of 40 sub-commands OK; audit 53 tables, 0 findings; database tests ALL PASSED.
