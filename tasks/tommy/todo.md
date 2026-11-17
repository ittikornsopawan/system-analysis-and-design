---
name: Tommy Task Plan
description: Active plans and task records of the agent Tommy (System Analyst); read it to see what Tommy is working on, its status and its verification evidence.
---

# Tommy Tasks

## F8: Stripe webhook amount and currency check

- Owner: Tommy
- Created at: 2026-11-17
- Started at: 2026-11-17
- Status: In progress

- [x] Spec: domain rule, body parameters, `p.currency` in the query
- [x] Sequence: mismatch branch, amount-check note
- [x] Checker needles for 02-stripe-webhook
- [x] Regenerate `api-contract.json` with `gen_contract.py`
- [ ] Run all checks and preflight, open PR, send link to Josh

## OpenAPI 3.1 validator in CI

- Owner: Tommy
- Created at: 2026-11-17
- Started at: 2026-11-17
- Status: In progress

- [x] Validate current main contract: `openapi-spec-validator` 0.9.0 reports OK (no errors to route to Josh)
- [x] Add pinned install, validate and deliberate-fault steps to `.github/workflows/checks.yml`
- [x] Add optional validator pass to `check_docs.py api-contract`
- [ ] Run all checks and preflight, open PR, send link to Josh

Completed records are in `success-task.md`.
