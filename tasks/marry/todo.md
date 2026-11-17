---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, product domain

Owner: marry
Status: In progress
Created at: 2026-11-17T12:28:00+07:00
Started at: 2026-11-17T12:28:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-product`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `tasks/lessons.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 4 of the contract rollout; Josh approved the lesson entry for the null-summary bug on 2026-11-17.

- [x] Publish the 15 approved operations of `product`; author 13 and 14 (in-review, now on main) stay unpublished.
- [x] `tasks/lessons.md`: lesson for the null-summary and conditional-default bug fixed in #199.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
