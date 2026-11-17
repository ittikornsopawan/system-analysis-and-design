---
name: Peter Task Plan
description: Active plans and task records of the System Analyst Peter, resolved from the workspace key peter in the agent registry.
---

# Peter Tasks

## e-commerce: security review of the published OpenAPI contract

Owner: peter
Status: In progress
Created at: 2026-11-17T13:00:00+07:00
Started at: 2026-11-17T13:00:00+07:00

- Assignment: Josh, authorized by ittikorn, read-only review; scope `docs/handoff`, `tasks/peter`. No change to the contract, generator or specs.

- [x] Compare the 74 operations with their specs (auth, webhook, examples, masking, 401/403/404, limits)
- [x] Write `docs/handoff/2026-11-17-openapi-security-review.md`
- [ ] Run the checks and preflight, open the PR, send the link to Josh

## e-commerce: follow-ups of the OpenAPI security review (owner answers 2026-11-17)

Owner: peter
Status: In progress
Created at: 2026-11-17T14:00:00+07:00
Started at: 2026-11-17T14:00:00+07:00

- Assignment: Josh (message of 2026-11-17). Both specs stay `status: approved` (owner-ordered change). Contract regenerated with `gen_contract.py`, never hand-edited.

- [x] PR 1 (F1): `shop/03-inquiry-shop-product-sku` member permission (spec, sequence, checker needles, contract, answers line in the review doc) — #213 merged 2026-11-17T13:14:50Z, CI `checks` passed
- [ ] PR 2 (F7, F9): webhook body at most 64 KB, 429 E90002 on the 9 public endpoints, `api-limits` checker, `api-conventions.md`, correction of the batch claim in the review (F8 was done by Tommy in #212)

Completed records are in `success-task.md`.
