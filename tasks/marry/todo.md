---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, consent domain and drift check

Owner: marry
Status: In progress
Created at: 2026-11-17T09:40:00+07:00
Started at: 2026-11-17T09:40:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-consent`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`, `.agents/skills/api-contract-design/scripts/gen_contract.py`, `.agents/skills/api-contract-design/SKILL.md`. Step 3 of the contract rollout; Josh asked on 2026-11-17 for a `--check` drift mode called from `api-contract`.

- [x] `gen_contract.py --check`: exits 1 when the committed contract differs from a fresh generation; `check_docs.py api-contract` runs it; hand edit and unregenerated spec change rejected.
- [x] Fix: every operation had `summary: null` and a description starting `None` (#197, #198) because the Name/Description table above the first `##` was never read; the generator now reads it and reports a spec without it; deliberate fault rejected.
- [x] Fix: a conditional default ("FALSE on insert") is no longer published as a string `default` of a boolean.
- [x] Publish the 8 approved operations of `consent`.
- [x] `SKILL.md`: the regenerate note names the drift check.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
