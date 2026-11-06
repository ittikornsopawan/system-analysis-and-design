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
