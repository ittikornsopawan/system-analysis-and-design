---
name: Agent Lessons
description: Repository-wide and project-specific lessons captured from user corrections for review before related work begins.
---

# Lessons

## Repository-wide

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
