---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: OpenAPI contract, shared components and authen-and-author

Owner: marry
Status: In progress
Created at: 2026-11-17T09:20:00+07:00
Started at: 2026-11-17T09:20:00+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-api-contract-authen`, scopes `e-commerce/api/api-contract.json`, `e-commerce/db/tests/check_docs.py`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`. Owner order of 2026-11-17: the SA team publishes `e-commerce/api/api-contract.json` from the 83 approved specs before dev starts, one PR per domain (authen-and-author, author, consent, product, shop, cart, sales, payment, shipping, campaign). Role: API Documenter (`.agents/agents/api-documenter.md`).

- [x] Shared `components`: status object, error responses (400 E10001, 401 E10002, 403 E10009, 404 E10004/E10005, 408 E90001, 409 E10003/E10006/E10007/E10008, and 500 without bizCode because every spec has a 500 example), bearer JWT scheme, `timestamp` and `requestId` header parameters, tags; servers from the spec Domain table.
- [x] The 10 operations of `authen-and-author`, each with `x-spec`, fields, required state, constraints and examples copied from its spec.
- [x] `check_docs.py api-contract`: missing operation, operation without a spec, status codes different from the spec examples, wrong `x-spec`, `openapi` not 3.1.0; 5/5 deliberate faults rejected.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge before the next domain.
