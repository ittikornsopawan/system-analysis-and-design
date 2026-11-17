---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, shared schemas refactor

Owner: marry
Status: In progress
Created at: 2026-11-17T13:20:00+07:00
Started at: 2026-11-17T13:20:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `refactor/marry-api-contract-shared-schemas`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 9 of the contract rollout (refactor, before shipping and campaign).

- [x] Refactor the contract to reuse `components/schemas` (owner request of 2026-11-17): `ResponseEnvelope`, `PageInfo` and one component per object table, regenerate the 8 published domains; the generator fails on two components with one shape or an inline object that repeats a component; 511 request and response schemas compared before and after: identical.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
