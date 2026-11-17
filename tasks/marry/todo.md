---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, security text, 429 and array limits

Owner: marry
Status: In progress
Created at: 2026-11-17T20:33:44+07:00
Started at: 2026-11-17T20:33:44+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-security-text`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 12 of the contract rollout, the last one; all 10 domains are in the contract.

- [x] Add the contract-side findings of #209 (F3 scheme text, F4 who may call, F5 webhook text with `security: []`, F6 global security, F8 `created` integer) and the two additions of Josh: shared `Error429` with `Retry-After` on the 9 public operations, and `minItems 1` / `maxItems 100` on the batch arrays and `cartIds`; the generator and `api-contract` check each of them.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
