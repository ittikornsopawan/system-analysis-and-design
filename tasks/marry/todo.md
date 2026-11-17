---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: specs, Domain rules out of the frontmatter

Owner: marry
Status: In progress
Created at: 2026-11-17T20:42:29+07:00
Started at: 2026-11-17T20:42:29+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-move-domain-rules-out-of-frontmatter`, scopes `e-commerce/doc/api/payment/04-inquiry-shop-payment`, `e-commerce/doc/api/payment/05-refund-payment`, `e-commerce/doc/api/sales/04-inquiry-shop-order`, `e-commerce/doc/api/sales/05-cancel-order`, `e-commerce/api/api-contract.json`, `tasks/marry/todo.md`, `tasks/marry/success-task.md`. The last task of the contract rollout, ordered by Josh on 2026-11-17: the rule lines of these four approved specs stand in the frontmatter, so `gen_contract.py` printed a WARNING for each; they move word for word into `## Domain`, like every other spec. The approval fields are not touched.

- [x] Move the `## Domain` rule lines of payment/04, payment/05, sales/04 and sales/05 out of the frontmatter into `## Domain`, word for word (Josh, 2026-11-17); the contract does not change, the generator warnings disappear.
- [ ] Verification: every `check_docs.py` sub-command, `audit_all.py`, `test_sequence_skeleton.py`, `test_agent_workspace.py`, `preflight.py`.
- [ ] Open the PR, tell Josh when `checks` is green, suspend, wait for the merge.
