---
name: Agent Lessons
description: Repository-wide and project-specific lessons captured from user corrections for review before related work begins.
---

# Lessons

### 2026-11-09 — Cover all requested layers and their sub-layers

- **Correction**: The owner asked why the meaning/scope section explained mainly Service = Domain, then required every layer and sub-layer to be explained.
- **Root cause**: The latest terminology discussion displaced the guide's system-wide scope; a five-row overview and file inventory were treated as sufficient coverage of other layers.
- **Corrected behavior**: Introduce the whole architecture first and give each requested layer/sub-layer its purpose, owned work, input/output, boundaries, collaborators, source example and evidence status. Keep Service = Domain in its proper Domain context and inspect the full document after a scope correction.
- **Preventive resource**: `.agents/skills/commit-and-pr/references/checklist.md` now requires explicit substantive scope coverage before publication; names, diagram boxes and successful link checks alone are insufficient. Verify the current guide against the complete five-layer/sub-layer inventory and confirm the earlier Domain-focused introduction would fail that coverage gate.
- **Delivery check exercised**: Preflight caught an extra blank line at EOF introduced by the scripted section append; per-line trailing-whitespace checks had not detected that whole-file condition. The guide was normalized to one final newline, the existing whitespace checklist now requires that normalization after scripted edits, and the document validator checks the same condition. A captured failing file confirms the guard rejects the original defect before the corrected checks are rerun; no publication occurred with the blocker.
- **Integration check exercised**: Current main and this task inserted independent sections at the same position in `tasks/todo.md`, causing a real merge conflict. The resolution retains both complete sections and proves that removing this task's section reproduces incoming main byte-for-byte. The integration gate in `.agents/skills/commit-and-pr/references/checklist.md` now explicitly requires complete-section preservation and a non-task-content comparison for this conflict shape.

### 2026-11-08 — Show real decomposition and choose semantics before layout

- **Correction**: The owner rejected the detail and layer grouping across the whole diagram set. Application must expose Command/Query, Validator and Handler as smaller boxes inside its layer; different diagram meanings must be researched before rendering.
- **Root cause**: The shared flat-card renderer and short node budget shaped the models before their analytical viewpoints and ownership hierarchy were settled. Long bullet lists substituted for actual subcomponents; several operational checkpoints were also presented using the same state/card grammar.
- **Corrected behavior**: Define the question, notation, ownership/decomposition levels and edge semantics for every diagram first. Use true native parent/child containment for structural views, time/activation/fragments for sequence, state/guard/effect for lifecycle, physical host/artifact placement for deployment, entity/field/cardinality for document models, and lanes/actions/gates for recovery. Do not force application layers into unrelated business or data views. Visually compare the complete set and verify the requested sublayers are actual editable child boxes rather than descriptive rows.

### 2026-11-08 — Preserve the owner's `Domain` business-logic convention

- **Correction**: The Domain layer also needs a child named `Domain` for reusable business logic, with the owner-specified example path `src/Ecommerce.Domain/Authen/Domain/`. The owner further clarified “service = domain เลยความหมายเดียวกัน” when discussing code structure.
- **Root cause**: Decomposition stopped at entities, value objects and repository contracts, omitting reusable domain operations and the project's chosen naming. Generic terminology distinctions also obscured the owner's intended business-code area.
- **Corrected behavior**: Use Service = Domain for reusable business operations in this project's code-structure discussion and preserve the owner-selected `Domain/` name instead of replacing it with Services/Policies. Show `Domain` explicitly under the Domain layer and the feature's physical path in the repository view. Explain reusable rules separately from handler orchestration and entity invariants; infrastructure services and database-domain associations still have their own roles. Treat tax calculation as a generic example owned by the relevant business feature, not an implemented Authen capability; distinguish owner-directed design from the pinned source baseline.

## Repository-wide

### 2026-11-09 — Improve delivery guidance after every error

- **Correction**: The owner requires errors in `commit-and-pr` to improve the skill as well as the immediate delivery result.
- **Root cause**: The delivery skill required resolving failures before publication but had no mandatory step that feeds each failure back into its reusable instructions.
- **Corrected behavior**: Apply the error improvement loop in `.agents/skills/commit-and-pr/SKILL.md` for self-discovered, check/integration/publication and review failures. Verify the preventive change, record its path and evidence, and preserve all delivery authorization and protected-branch boundaries.
- **Applied evidence**: The Python skill validator could not start because PyYAML was missing. The new loop was strengthened to distinguish startup failures from validation findings and require explicit coverage/gaps for equivalent checks; Ruby YAML parsing and direct metadata/reference checks verify this prose-only change without claiming the original validator ran.
- **Scope evidence**: A publication check incorrectly required the entire shared checkout to be clean while another task edited `e-commerce/doc/code-structure.md`. Verification now checks this task's paths and final branch diff separately; the skill's merged-result step explicitly requires inventorying/preserving unrelated working-tree edits rather than rejecting them as task failures.

### 2026-11-08 — Feed every API authoring error back into the skill

- **Correction**: The owner requires every error to produce a skill improvement as well as a correction to the work.
- **Root cause**: The API skill's completion criteria covered artifact verification but did not require every discovered failure to improve the reusable authoring method.
- **Corrected behavior**: Apply the error improvement loop in `.agents/skills/api-contract-design/SKILL.md` for self-discovered, tooling/check/render and review failures; complete and verify the preventive skill change before closing the task.
- **Applied evidence**: Delivery rebase stopped because two independent task sections were inserted at the same position in `tasks/todo.md`. Both sections were retained and all upstream task content was verified byte-for-byte. The loop's correction step now explicitly requires preserving valid overlapping edits and verifying unrelated content.
### 2026-11-08 — Integrate current main before PR publication

- **Correction**: The owner requires merging current main into the task branch and resolving conflicts before opening a PR.
- **Root cause**: The delivery skill went directly from task commit to push/PR, while its blanket merge prohibition also obscured the permitted direction of integration.
- **Corrected behavior**: The `commit-and-pr` skill now distinguishes main-to-task integration from merging a PR. Fetch the base, merge into the task branch, preserve valid work on both sides, verify the merged result and publish only after the integration gate passes; keep main and published history protected.

### 2026-11-08 — Keep required skill examples inside the skill

- **Correction**: The sequence guidance required reading a particular endpoint's diagram to learn its format and storytelling, so moving or deleting that file would remove the example.
- **Root cause**: A live project artifact was treated as the durable definition of reusable authoring conventions.
- **Corrected behavior**: Put the full presentation rules and a complete illustrative example in the skill or its bundled reference. Use the target spec for actual behavior and SQL; required instructional examples must remain available independently of the project file that inspired them.

### 2026-11-08 — Reconcile renderer consumers during a rename/modify conflict

- **Correction**: The owner reported PR #64's conflict at the original `e-commerce/diagram/generate_diagrams.py` path after main added the Domain diagram package.
- **Root cause**: The PR relocated shared helpers to `scripts/` while main added `output_dir` support and a Domain generator importing helpers from their former location. Choosing either side of the conflict alone would lose behavior or break imports.
- **Corrected behavior**: Combine explicit output directories with routed defaults, update incoming consumers and navigation, and run both generator families. Preserve existing models/PNGs and verify their hashes against each parent; resolving conflict markers alone is insufficient.


### 2026-11-08 — Check a replacement agent's workspace before offering it

- **Correction**: After Logan was found unregistered, the owner chose Jinny, but Jinny's managed workspace was already locked by another active task. The owner then directed this task to use a separate workspace.
- **Root cause**: Identity validation and workspace availability were checked in separate rounds, so the first proposed replacement could not actually start the work.
- **Corrected behavior**: Check registration, active assignment and lock together before proposing a named replacement. Preserve another chat's work and lock. In this task, the owner's explicit separate-workspace direction authorizes a separate Codex worktree; this task-specific choice does not change the registry or the default managed-clone rule.


### 2026-11-06 — Keep agent reviews within the requested adaptation scope

- **Correction**: A review of an existing agent expanded into redesigning the role, creating a separate skill, and changing the resource registry when the user only wanted the current agent adapted to the desired .NET backend role.
- **Root cause**: The review optimized for the repository's ideal resource architecture instead of separating necessary changes from optional future improvements.
- **Corrected behavior**: Preserve the existing resource and structure when it can meet the request; recommend only changes required by the stated goal, and label broader redesigns or new roles as optional rather than necessary.

### 2026-11-06 — Preserve explicit workflow artifacts

- **Correction**: The adapted Workflow Orchestration omitted the explicit `tasks/todo.md` and `tasks/lessons.md` references shown in the approved source.
- **Root cause**: The adaptation optimized for document structure before confirming which concrete artifacts were mandatory.
- **Corrected behavior**: Preserve explicitly requested artifacts and paths when adapting a reference; propose alternatives separately and wait for approval before substituting them.

### 2026-11-06 — Model delegated delivery as a user-appointed capability

- **Correction**: Delegated delivery authority must not be hardcoded to Josh or any specific lead name; any named agent may delegate delivery only when the user explicitly grants that capability.
- **Root cause**: The design inferred authority from the current team example instead of separating stable agent identity from user-appointed capabilities.
- **Corrected behavior**: Store delegation as an explicit registry capability, require the authorized user to grant or revoke it, and never let an agent self-assign or transitively grant that capability.

## Project-specific

### 2026-11-06 — A plain `UNIQUE` on a name blocks reuse after a soft delete

- **Correction**: The lead SA found `UNIQUE` on `name` in `m_product_type`, `m_product_brand` and `m_consent_type` while reviewing WP6; the same pattern still exists in `m_product_category`, `m_product_category_attribute` and `m_user` (username, email).
- **Root cause**: Tables were written with an inline `UNIQUE` before the convention of a partial unique index `WHERE row_status <> 'DELETED'` existed, and no checker compared new tables with the convention.
- **Corrected behavior**: Use a partial unique index for every name that a soft delete must free; list the plain `UNIQUE` columns of delivered tables as backlog instead of changing them inside an unrelated task.

### 2026-11-06 — Master data foreign keys must protect history

- **Correction**: `m_product.type_id`, `brand_id` and `t_consent.consent_type_id` were `ON DELETE CASCADE`, so deleting a master row would silently delete products, order items and consent evidence.
- **Root cause**: `CASCADE` was the default choice for every foreign key.
- **Corrected behavior**: A foreign key that points at a master or history row is `RESTRICT`; `CASCADE` only for children that have no meaning without the parent. `m_product.category_id` is still `CASCADE` and is backlog.

### 2026-11-06 — Every write API must say who may call it

- **Correction**: Review found that the shop type, product category, category attribute, product and consent upsert specs said nothing about permission, so every access token could write master data.
- **Root cause**: Early specs copied a template that had no permission section, and the checkers did not require one.
- **Corrected behavior**: A spec of a write API states its caller (`PLATFORM_ADMIN`, shop member, or owner of the data) and has a 403 example when the answer can be 403; the fix for the delivered specs is planned in WP5 step 5c.

### 2026-11-06 — A lock that counts its own refusals never ends

- **Correction**: The first login lock counted refused attempts as failures, so anyone sending one request every 15 minutes kept a victim locked out for ever. The lead SA missed it at gate 1 and found it at gate 2.
- **Root cause**: The attempt log had a boolean success flag, which cannot tell a wrong password from a refused attempt.
- **Corrected behavior**: Log every attempt with a result of `SUCCESS`, `FAILED` or `REFUSED` and count only `FAILED`; test the count with refused rows present.

### 2026-11-06 — State what is committed when an API answers an error

- **Correction**: The refresh token reuse rule closed the whole session but did not say that the closing is committed although the answer is 401.
- **Root cause**: The spec described the steps of one transaction and the answer, not which writes survive a failed answer.
- **Corrected behavior**: When an error answer must keep a write (closing a session, recording a refused attempt), say so in the rules and in the order of steps, and keep that write outside the transaction that is rolled back.

### 2026-11-06 — A key shipped in the client gives no secrecy

- **Correction**: `01-register` and `02-login` asked the frontend to encrypt fields with AES and a key and IV, while the backend already took plain text; the owner chose plain text over TLS with encryption on the server.
- **Root cause**: The first specs described client-side encryption without asking where the key lives.
- **Corrected behavior**: Protect sensitive fields with TLS in transit and server-side encryption at rest; do not specify client-side encryption with a key that ships in the app.

### 2026-11-06 — Compare an amount with the same inputs as the rule that owns it

- **Correction**: In the campaign design (C14) the minimum payment amount was compared with `total_price - total_discount` without the shipping fee, but the payment rule (R65) checks `amount`, which includes the fee (at least 40.00), so the extra rule was unnecessary and wrong. The lead SA caught it at gate 1.
- **Root cause**: The new rule was written from the order totals instead of reading the formula of the domain that owns the limit.
- **Corrected behavior**: Before adding a rule that depends on another domain's limit, read that domain's formula and use the same inputs; if the limit can never be reached, write a one-line note instead of a rule.

### 2026-11-06 — Write the lock order whenever a spec updates several rows

- **Correction**: `sales/02` took stock from several lots without saying in which order, which can deadlock two orders that touch the same lots in opposite orders. The lead SA found it while reviewing the campaign budget.
- **Root cause**: Each spec described its own conditional `UPDATE` but nobody wrote the order in which the rows are locked.
- **Corrected behavior**: A spec that updates more than one row of the same kind states the order (here: order row, lots by `id`, then budgets by `id`) and uses it in every spec that touches the same rows.

### 2026-11-06 — Check what each role can derive when a stored value changes

- **Correction**: After the platform pays a campaign discount (C6), the `grossProfit` that a shop sees falls by the discount, and `gross - shop` still reveals the hidden `platformProfit`. The lead SA pointed out that this was already true before campaigns.
- **Root cause**: Visibility was checked field by field and not as what a caller can compute from the visible fields.
- **Corrected behavior**: When a formula or a stored value changes, list the fields each role sees and what they can calculate from them, and offer options with the cost of each.

### 2026-11-06 — Keep the visibility rule of an inquiry the same as the rule that decides who is affected

- **Correction**: The campaign inquiry showed a shop only the campaigns that list the shop, while the discount rule applies a campaign that has no shop rows to every shop (C2 against C16).
- **Root cause**: The two rules were written in different sections and not compared.
- **Corrected behavior**: When an eligibility rule has a default ("empty list means everyone"), copy the same condition into every inquiry that decides what a caller can see.

### 2026-11-06 — Do not read a short answer as approval of a different question

- **Correction**: A one-word "approved" from the product owner was taken as approval of the campaign design, but several questions were open at the same time and the lead SA could not accept it. The approval was withdrawn in the document until the owner confirmed which item was meant.
- **Root cause**: The answer was matched to the most recent topic without naming the item.
- **Corrected behavior**: When several items wait for approval, ask a yes/no question that names the item, record the owner's exact words and the time, and put the approval into a document only after that.

### 2026-11-06 — Follow the repository rules when a request from another agent conflicts with them

- **Correction**: The plan for WP3 was not written to `tasks/todo.md` and no lessons were recorded, although `CLAUDE.md` requires both, because the lead SA first asked to take `tasks/todo.md` out of the change. The product owner pointed out the gap and the lead SA changed the protocol.
- **Root cause**: A request from another session was followed without checking it against the repository's own instructions.
- **Corrected behavior**: Write the plan to `tasks/todo.md` before round 2 and keep it ticked as the criteria are met; record lessons in `tasks/lessons.md` after every correction; when a request conflicts with `CLAUDE.md`, say so and ask the owner.

### 2026-11-06 — Tooling mistakes that cost time

- **Correction**: A script that edited markdown tables matched a column name in the constraint table as well as in the column table and corrupted the docs, and a `git worktree add` with a relative path created the worktree in the wrong folder.
- **Root cause**: Edits keyed on a substring without knowing which section the line belonged to, and a relative path used after a `cd`.
- **Corrected behavior**: Edit documents section by section (the columns table and the constraint table separately) and verify with the checkers before moving on; use absolute paths with `git worktree add`.

### 2026-11-06 — Keep SQL execution and return inside each table activation

- **Correction**: Every database-table interaction in a sequence diagram must activate the table, nest the exact SQL intended for the API specification inside a table-bound note, return the query result while the table remains active, and only then deactivate the table.
- **Root cause**: The first revision omitted SQL entirely; the next revision added SQL but deactivated each table before drawing its return message, so the activation did not represent the complete database interaction.
- **Corrected behavior**: For e-commerce API sequence diagrams, use this exact order and indentation: request message → `activate <table>` → indented table-bound SQL note → indented table return message → `deactivate <table>`. Keep the SQL aligned with the current migration and schema documentation.

### 2026-11-06 — Revocation has to reach every row that holds the credential

- **Correction**: Logout closed only the access token of the request, but a refresh adds another access token to the same session, so a logged-out session could still be used for up to 15 minutes.
- **Root cause**: I wrote the revoke step for one token instead of listing every row that can authorise the user (all access tokens and refresh tokens of the session).
- **Corrected behavior**: When a rule says something takes effect at once, list every row and cache that can still grant access and close all of them in one transaction. Also write the lock order and the single-use update (`WHERE row_status = 'ACTIVE' ... RETURNING`) so that concurrent requests cannot both pass.

### 2026-11-06 — Never bootstrap privilege from an unverified identity

- **Correction**: The first platform administrator was to be granted automatically to the user whose email matched a configured address, but registration does not verify email addresses and answers 409 for a taken name, so anyone who registers first would get the highest privilege.
- **Root cause**: I treated the email address as proof of identity.
- **Corrected behavior**: Grant the first administrator by an operator command that names the `userId` after the operator has checked the account out of band, and make it work only when no ACTIVE administrator exists. Ask first which identifiers the system really verifies.

### 2026-11-06 — Do not build the API surface that nothing uses

- **Correction**: The design proposed 17 specs for roles, permissions and scopes although no API enforces a permission, and the new `seed` folder changed the project structure without being asked.
- **Root cause**: I followed the roadmap list and the table design instead of asking what is needed to hand over the first administrator.
- **Corrected behavior**: Split the work into what is needed now and what waits for a consumer, change the schema of the deferred tables once so that later work is free, and ask before adding a folder or a tool to the project structure.

### 2026-11-07 — Process rules must not override the repository rules

- **Correction**: The owner asked why neither the lead nor the analysts wrote `tasks/todo.md` and `tasks/lessons.md`. The first team protocol told the analysts not to touch those files, against `CLAUDE.md`.
- **Root cause**: The protocol was written to avoid merge conflicts without checking it against the repository instructions.
- **Corrected behavior**: Check a new process against `CLAUDE.md` before issuing it, write a plan before a package starts and lessons after a correction, and settle merge conflicts when packaging.

### 2026-11-07 — Read the schema of a request before saying what it allows

- **Correction**: The lead reported that `01-register` accepts several addresses with their own default flag; the spec has one address object, and the analyst corrected it.
- **Root cause**: The lead inferred an array from a placeholder name in an `INSERT` instead of reading the request table.
- **Corrected behavior**: Read the body parameters and the example before a claim about a request, and say in the finding when something was not checked.

### 2026-11-07 — A review that approves a limit must test its worst case

- **Correction**: The lead passed the login lock at gate 1 although refused attempts were counted, which let a stranger keep an account locked for ever; it was found at gate 2.
- **Root cause**: The review checked the numbers (5 failures, 15 minutes) and not what a hostile caller does at the edge.
- **Corrected behavior**: For every limit or lock ask what an attacker does to extend or abuse it, and write the answer into the finding.

### 2026-11-07 — Give the next assignment when a gate closes

- **Correction**: An analyst sat idle after her gate passed because the lead had said what not to touch but not what to do next.
- **Root cause**: The lead answered each report and did not look at who was waiting.
- **Corrected behavior**: When a gate passes, say in the same message what the analyst does next or that the analyst should stop.

### 2026-11-07 — Read a rule the owner just merged before issuing assignments

- **Correction**: The lead gave the analysts assignments in linked worktrees and with paths outside their registry scope, against `.agents/rules/named-agent-workspaces.md` that had been merged the evening before. One analyst found it and stopped; the lead had also opened a pull request from a linked worktree.
- **Root cause**: The lead read the merged pull request list but not the rule it contained, and kept using the protocol written before it.
- **Corrected behavior**: After the owner merges a rule, read it before the next assignment, state the contract (`agent`, `role`, `task`, `scope`, `delivery`, `authorized_by`) inside the registry scope, and when a helper blocks an assignment stop and ask instead of narrowing it alone.

### 2026-11-07 — Treat a blocked helper as a limit of authority, not as a technical obstacle

- **Correction**: `agent_workspace.py prepare` refused an assignment whose paths were outside the registry scope; the analyst cut the scope and ran it again before a new message from the assigner arrived.
- **Root cause**: The refusal was read as something to get around, and no check was made for newer instructions before repeating the command.
- **Corrected behavior**: When a helper blocks for a reason of authority or scope, stop and ask the assigner; do not change the contract, and look for a newer message before a retry.

### 2026-11-07 — A checker written before a rule may reject the rule's own text

- **Correction**: `shop-type-spec` flagged the word "product" in the standard approval sentence "product owner" of the new specs.
- **Root cause**: The leftover-word rule was written before specs had to carry that approval sentence.
- **Corrected behavior**: When a new spec rule collides with an old checker, narrow the checker as little as needed, show that it still catches the other words, and say so in the report.

### 2026-11-07 — Look for the files that other checkers read from the same spec

- **Correction**: `api-sequence-spec` forces `sequence.wsd` to match the SQL of its spec; adding the permission queries to the nine specs almost missed the sequence diagram of `consent/02`.
- **Root cause**: The search for affected files stopped at the specs.
- **Corrected behavior**: After adding SQL to a spec, search for every file read from the same spec (sequence diagram, schema doc) and run all the checkers before saying the work is complete.

### 2026-11-07 — Prove specification and sequence correctness together

- **Correction**: The owner challenged whether sequence.wsd had been checked alongside spec.md. Both files were changed in PR #23, but the handoff did not make the paired evidence easy to inspect. The subsequent render exposed a real gap: PlantUML treated SQL value lines beginning with a single quote as comments, so VALUES were missing in the image even though source SQL parity passed.
- **Root cause**: Source equality, table activation and branch checks were treated as sufficient diagram evidence without verifying the renderer's interpretation of the same SQL text.
- **Corrected behavior**: Review each scenario against both files, including validation, input/result mapping, permissions, SQL order, transaction effects and HTTP outcomes; preserve visible SQL values with renderer-safe escaping and compare the decoded SQL; render and inspect the diagram before claiming the diagram is verified, and show paired paths plus a scenario correspondence table in the handoff. Any SQL edit must update its existing sequence in the same PR; run every current checker before each push, and announce the current and next API group to coordinate concurrent work.

### 2026-11-07 — Discover installed runtimes beyond PATH

- **Correction**: The handoff said Java was unavailable after /usr/bin/java failed. OpenJDK was already installed under Homebrew, and a PlantUML JAR existed in the VS Code extension.
- **Root cause**: A failing system launcher was mistaken for the absence of an installed runtime; common installation locations were not checked.
- **Corrected behavior**: Inspect the selected tool path and known installation locations before reporting a missing capability. Use the existing runtime by absolute path and report precisely what was tried when rendering truly cannot run.

### 2026-11-07 — Apply the owner's latest delivery override

- **Correction**: The owner replaced the earlier one-open-PR workflow with an explicit instruction to leave each completed API PR open, switch back to main and start a fresh branch immediately, without waiting for merge.
- **Root cause**: A previously selected workflow or a tool default can remain in effect after the user has superseded it unless the current assignment records the new authority explicitly.
- **Corrected behavior**: For this API review, persist the exact override, preserve branch-scoped PR/assignment records and edit one branch at a time in Peter's managed clone, then continue to the next API after opening its PR. Do not use the old merge gate to stop, and do not infer merge, force-push or delegation authority from this override.

### 2026-11-07 — A design that scans a table must name the index, or say why none is needed

- **Correction**: The first WP3b appendix (S26) scanned the `SHIPPED` shipping rows by `shipped_at` for the automatic completion job but also said that the schema does not change (S30). The lead SA pointed out the contradiction at gate 1.
- **Root cause**: The scan was designed from the rules and the data model was not read for the access path of a query that runs all the time.
- **Corrected behavior**: When a job or an inquiry filters a growing table by a column, write the index (a partial index when the filtered state is small), its test and its documents in the same design, or write the reason it is not needed.

### 2026-11-07 — A status that gets a new meaning must change every field that shows it

- **Correction**: Letting the system set `DELIVERED` (S25) changed what `deliveredAt` means in `shipping/04`, `05` and `06`, but the first appendix did not touch their field descriptions. The lead SA found it at gate 1.
- **Root cause**: The change was designed at the rules level and the specs that display the value were not listed.
- **Corrected behavior**: List every spec and field that shows a status or a timestamp whose meaning changes, change their descriptions in the same round and make the checker catch the new wording.

### 2026-11-07 — Write the boundary of a time limit once and use it everywhere

- **Correction**: The rule said "older than 7 days" while the SQL used `shipped_at <= now - 7 days` and the example said "day 3 or earlier"; a mutation test showed that the checker agreed with the wrong reading.
- **Root cause**: The words, the SQL and the checker were written separately.
- **Corrected behavior**: Decide whether the limit includes the boundary, write it in the rule ("at least 7 days old, exactly 7 days qualifies"), the SQL comment, the example and the checker, and add a mutation at the boundary.

### 2026-11-07 — A scan with a limit must filter by everything that decides the result

- **Correction**: The scan query of the automatic completion job selected the orders by the age of a `SHIPPED` parcel only, sorted by `order_id` and limited to one batch. The lead SA found at gate 2 that an order that can never qualify (a partial shipment that cannot be finished, a `PENDING` parcel left) stays a candidate in every run and, with more such orders than the batch size, the orders with a larger id that qualify are never selected.
- **Root cause**: The scan was treated as a loose pre-filter because the conditions are checked again under the lock, and the effect of `ORDER BY ... LIMIT` over rows that are always skipped was not considered.
- **Corrected behavior**: When a job takes a limited, ordered batch, put every condition that can be tested without a lock into the scan (the check under the lock stays as the guard), write the reason in the rule, and add a checker needle with a mutation for each condition.

### 2026-11-07 — Test a standard against every file it will govern, not only the model file

- **Correction**: The first login standard of the sequence checker required BEGIN before the first database interaction. Running it on all 83 specs showed that `05-refresh-token` reads the refresh token row before BEGIN on purpose (the row decides which user to lock).
- **Root cause**: The rule was copied from `02-login`, which has no read before BEGIN, and was not run on the other finished diagrams before it was called a standard.
- **Corrected behavior**: Run a new structural rule on every finished file first; when a design decision explains the exception, write the rule at the exact point that matters (here: BEGIN before the first INSERT, UPDATE or DELETE), say so in the report to the lead, and never solve it by adding the file to the legacy list.

### 2026-11-07 — A mutation case must break the property, not only touch the line

- **Correction**: The first run of the manual case "BEGIN after the first write" passed the checker and looked like a miss. The case itself was wrong: it removed BEGIN and put it back immediately before the first write, which is still before it.
- **Root cause**: The mutation was written from the name of the case and its result was not compared with the property (order of two lines) before the checker was blamed.
- **Corrected behavior**: When a mutation is not caught, first print the mutated lines and check that they really break the property; fix the case if it does not, and fix the checker only if it does.

### 2026-11-07 — A rule about "the line before" must follow the block, not the text

- **Correction**: The lead found in review of PR #27 that a lock taken before BEGIN and an error answer without ROLLBACK were not caught. My first fix for the second one looked for the nearest earlier `app -> infra:` line, and the ROLLBACK of a sibling branch still satisfied it.
- **Root cause**: The checker read the diagram as a flat list of lines, while an `alt` / `else` diagram has branches; the transaction standard was only compared with the lines the login diagram happens to have (408 and 500) and not with every way a transaction can fail (400 to 409, a lock before BEGIN).
- **Corrected behavior**: When a checker reasons about order inside a diagram with branches, follow the nesting (indentation) so closed branches do not count, and write the mutation for each ROLLBACK or COMMIT one by one, not for one example. For a transaction rule, list every statement that must be inside it (writes and locks) and every exit that must end it.

### 2026-11-07 — Read how a repeated option is parsed before passing several values

- **Correction**: `agent_workspace.py prepare` was called with `--scope "a,b,c"`. The option is `action="append"`, so the assignment record kept one string with commas and no changed file could be inside it; a second `prepare` was refused because the task branch was already active, and the record had to be reset by hand with the approval of the lead.
- **Root cause**: The values were joined in the way the previous assignment message listed them and the usage line (`--scope SCOPE`) was not checked for how several scopes are given; the `scope` of the output was not read before the lock was used.
- **Corrected behavior**: Pass one `--scope` per path, and read the `scope` list of the `prepare` output before starting; it must show every path as its own entry. If it does not, release the lock and stop to ask the assigner before touching the record.


### 2026-11-07 — A displayed consent is read independently of its answer

- **Correction**: The owner rejected inferring reading only from an explicit boolean result. Displaying triggers the submission endpoint without result; answering adds result later.
- **Root cause**: Read state was inferred from answering rather than the owner's display event.
- **Corrected behavior**: Record a supplied displayed version as read independently of result; preserve any answer on read-only calls and preserve the original read timestamp once read. Already-read read-only calls need no UPDATE. Review register, submit and pending together; each remains its own PR.

### 2026-11-07 — Give each requested diagram a distinct analytical purpose

- **Correction**: The owner found the three delivered architecture diagrams too shallow and too similar, and requested research before revising all three with diagram-design.
- **Root cause**: A single compact Architecture grammar and similar component cards were reused for code structure, runtime flow, and commerce capabilities; the nine-node budget became a reason to omit useful detail instead of selecting the right view and canvas.
- **Corrected behavior**: Research the purpose of each view first, define a distinct question and visual grammar per deliverable, and include concrete project paths, responsibilities, interfaces, interactions, guards, and transaction effects as appropriate. Use evidence-based detail and a larger readable frame where needed. Review the three renders together for both semantic separation and detail before claiming completion.

### 2026-11-07 — Refresh diagram evidence before delivery

- **Finding**: The diagram branch retained the earlier shipping rule without automatic completion while WP3b had already merged into main.
- **Root cause**: Local specifications were used without comparing changes on the refreshed PR base before delivery.
- **Corrected behavior**: Before a diagram PR, compare governing sources against current origin/main, reconcile affected diagrams and explanations, and rerun rendered/source checks; do not ship a known superseded lifecycle rule.

### 2026-11-07 — Reconcile the local PR base and stop delivery on a failed preflight

- **Finding**: After merging origin/main into a task branch, local main was still behind. Delivery preflight compared against that stale base and rejected upstream files outside the assignment; a following shell push nevertheless ran.
- **Root cause**: The remote-tracking base was mistaken for the local base selected by the helper, and dependent delivery commands did not stop on failure.
- **Corrected behavior**: Fast-forward the local base safely, verify the task diff against the current base, and make dependent commit/push commands fail immediately if preflight fails. Preserve both histories and never expand scope to hide upstream files.

### 2026-11-08 — Tell the lead when a pull request is opened, before anyone can merge it

- **Correction**: The checker pull request #54 was opened and not reported to the lead; the owner merged it before the lead had reviewed it. The lead asked to be told before the owner merges, every time.
- **Root cause**: The report to the lead was left for the end of the task, as a part of the final handoff, so the gap between opening and merging was not covered.
- **Corrected behavior**: Send the lead the link right after `gh pr create` and the first PR status call, before any other step, with the checks and the open questions; never leave it for the final report.

### 2026-11-08 — Prove that every SQL line is drawn, not only that the SQL equals the spec

- **Correction**: The INSERT written by hand in PR #58 had value lines that start with a quote after the indentation; PlantUML draws such a line as a comment, so six lines were missing from the picture. `api-sequence-spec` passed because it reads the raw text, and my first rendered check passed too because it asked only whether each line appears somewhere in the picture.
- **Root cause**: The edit script encoded a line only when the quote was in the first column, and the rendered check used a substring test that a repeated line (`'<sequence.userId>',` appears twice) satisfies by luck.
- **Corrected behavior**: Encode a leading quote after the indentation (`&#39;`), and check the render by counting: every SQL line must appear in the picture at least as many times as it appears in the spec.

### 2026-11-08 — Preserve retired exemptions when updating a PR base

- **Finding**: GitHub merge commit 87162eb restored the completed inquiry-profile token/timeout exemption that its first parent b1c5c90 had removed. Endpoint artifacts still passed their flow check, but the combined main failed api-sequence-spec.
- **Root cause**: A shared checker contains both function logic and changing exemption lists; retaining functions alone does not prove that a merge preserved retired entries.
- **Corrected behavior**: Compare function registrations and retired exemptions against both parents, run every registered check on the combined tree before delivery, and record/repair an existing failure within the authorized scope rather than masking it or weakening the check.

### 2026-11-08 — Use the returned PR identity, never the next presumed number

- **Finding**: After opening role-batch PR69, the rotation command mistakenly used 68, which another branch had already taken. The identity/head guard stopped rotation before changing active assignment history.
- **Root cause**: A sequential PR number was assumed instead of consuming the URL returned by the create command; concurrent authors can take intervening numbers.
- **Corrected behavior**: Capture the actual returned PR URL, verify repository/base/head branch/head commit before any lifecycle action, and pass that same verified URL throughout release/archive/rotation. Keep the identity guard; correct the input rather than relaxing it.

### 2026-11-08 — A replacement PR does not authorize closing the original

- **Finding**: Automatic approval review rejected closing PR67 after replacement PR73 opened because the owner had explicitly instructed leaving PRs open. No closure was performed.
- **Root cause**: Replacement delivery was incorrectly treated as an exception to the earlier leave-open instruction.
- **Corrected behavior**: Keep original PRs and branches intact unless the owner explicitly authorizes closing that specific PR; creating a replacement and resuming other work do not supply that authorization.

### 2026-11-09 — Bind a narrative guard check to its actual phase

- **Finding**: A permission mutation removing the before-count rule passed because the short phrase “every non-DELETED definition” also occurred in the unrelated duplicate rule.
- **Root cause**: A global substring check could be satisfied by another paragraph and did not prove the Q22 count definition.
- **Corrected behavior**: Require the complete beforeDefinitionCount clause, keep exact SQL and phase checks independent, and test synchronized SQL faults in both spec and sequence. Recheck: 66/66 isolated mutations and 10/10 synchronized faults are rejected; positive permission/SQL/render checks pass.

### 2026-11-09 — Establish fixture lifecycle before asserting error precedence

- **Finding**: A batch SQL fixture expected the missing second target index, but its first target had already been deleted in the preceding all-delete scenario. The actual contract correctly returned the first missing target.
- **Root cause**: A scenario reused a lifecycle-mutated id without checking its precondition.
- **Corrected behavior**: Use an existing ACTIVE fixture target for the first item, then assert the missing later index. Preserve the contract and checker. The full real PostgreSQL batch driver now passes, including all-target existence, 100-item results, whole-batch rollback and concurrency. Carry this fixture-precondition guidance into the separate bounded verification-guidance follow-up; keep API19 scope intact.

### 2026-11-09 — Compare a checker helper only across its supported API family

- **Finding**: An integration comparison called author_needles for author API10, which belongs to another checker; the comparison stopped with KeyError before producing evidence.
- **Root cause**: The broad AUTHOR_SPECS registry was mistaken for the helper's supported master API01..09 domain.
- **Corrected behavior**: Re-run the comparison over the supported master family, retain the full registration/function preservation check, and report that the failed validator did not establish coverage. Corrected comparison passes for every unaffected master API and COMMANDS exactly 57 -> 58. Carry this generic validator-domain requirement into the verification-guidance follow-up without widening the API19 diff.
