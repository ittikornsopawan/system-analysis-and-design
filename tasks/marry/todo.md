---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, payment domain

Owner: marry
Status: In progress
Created at: 2026-11-17T13:10:00+07:00
Started at: 2026-11-17T13:10:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-payment`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 8 of the contract rollout.

- [x] Publish the 5 approved operations of `payment`; the Stripe webhook body nests its dotted names (a parent is required when a child is MANDATORY) and marks the external payload `additionalProperties: true` (lead decision of Josh, 2026-11-17); 3/3 deliberate faults rejected.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
