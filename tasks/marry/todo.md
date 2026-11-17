---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, shop domain

Owner: marry
Status: In progress
Created at: 2026-11-17T12:31:00+07:00
Started at: 2026-11-17T12:31:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-shop`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 5 of the contract rollout.

- [x] Publish the 16 approved operations of `shop`; the 3 storefront inquiries are public (no security requirement), as their specs say.
- [x] Write the contract as one-line JSON (lead decision of Josh, 2026-11-17): the indented file was 1221 KB, over the 1 MB preflight limit, about 1.66 MB projected for all domains; `SKILL.md` says how to read it.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
