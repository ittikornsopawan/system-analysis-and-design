---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, author domain and owner conventions

Owner: marry
Status: In progress
Created at: 2026-11-17T09:33:00+07:00
Started at: 2026-11-17T09:33:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-author`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 2 of the contract rollout. Owner answers of 2026-11-17 relayed by Josh: count fields (`pageIndex`, `pageSize`, `totalItems`, `totalPages`, `expiresIn`, `status.code`) are integer; commit the generator under `api-contract-design/scripts` with a regenerate note in its SKILL.md; a null in a spec example makes the field nullable. Lead decision: publish author 01-12 now, Peter's 13-17 after the owner approves them.

- [x] `gen_contract.py`: regenerates the contract from the approved specs of `API_CONTRACT_DOMAINS`, applies the owner conventions, checks every example against its schema and exits 1 on any mismatch; 4/4 deliberate faults rejected.
- [x] Regenerate `authen-and-author`: 9 count fields `number` -> `integer`, nothing else changes.
- [x] Publish the 12 approved operations of `author`.
- [x] `check_docs.py api-contract`: `author` in `API_CONTRACT_DOMAINS`, only `status: approved` specs count, so in-review specs (Peter's 13-17) do not break CI; deliberate fault (an approved spec turned in-review) rejected.
- [x] `SKILL.md`: how to regenerate the contract.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
