---
name: Tommy Task Plan
description: Active plans and task records of the agent Tommy (System Analyst); read it to see what Tommy is working on, its status and its verification evidence.
---

# Tommy Tasks

Completed records are in `success-task.md`.

## e-commerce: shop roles rollout, PR 7 to PR 10 (OWNER in the shop member checks)

Owner: tommy
Status: In progress
Created at: 2026-11-16T14:46:28+07:00
Started at: 2026-11-16T14:46:28+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/tommy`, one branch and one pull request per folder, each from the latest `origin/main`. Governing design: `docs/superpowers/specs/2026-11-14-shop-roles-design.md` (approved 2026-11-16, D1 and the fixed table of D2). Plan: `tasks/peter/todo.md`, "shop roles rollout", PR 7 item. This record is kept in PR 7 only, so that the four branches do not edit the same file.

- [ ] PR 7, `sales/04`, `sales/05`: `role IN ('ADMIN', 'STAFF')` becomes `role IN ('OWNER', 'ADMIN', 'STAFF')` in the spec and `sequence.wsd`, the member text names OWNER, `order-spec` requires the new role set and rejects the old one.
- [ ] PR 8, `payment/04` (member check, same change) and `payment/05` (the refund row of D2 stays: OWNER or ADMIN only, a STAFF member gets 403 E10009, with a 403 example); `payment-spec` needles.
- [ ] PR 9, `shipping/01–04`: the member check, same change; shipping needles.
- [ ] PR 10, `campaign/02`: the member check, same change; campaign needles.
- [ ] Before each PR: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py` and `preflight.py`; after CI is green, the link to Josh, then `suspend`.
