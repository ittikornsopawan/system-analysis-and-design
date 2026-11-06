---
name: Agent Lessons
description: Repository-wide and project-specific lessons captured from user corrections for review before related work begins.
---

# Lessons

## Repository-wide

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
