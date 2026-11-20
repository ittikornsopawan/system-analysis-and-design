---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

Completed records are in `success-task.md`.

## e-commerce: domain diagram `--check` passes again (`ix_m_parameter_parent_id`)

Owner: jinny
Status: In review
Created at: 2026-11-20T15:53:39+07:00
Started at: 2026-11-20T15:53:39+07:00

Authority: Josh (SA Lead) after #272, `authorized_by: ittikorn`, delivery `open-pr`. Scope: `e-commerce/diagram/domain`, the domain generator and its content/notes modules, `tasks/jinny`.

- [x] Find the cause. Evidence: inventory diff shows one new index, `ix_m_parameter_parent_id` (`3c740fa`, via #252), and the hashes of `00-common.schema.up.sql` and `m_parameter.md`.
- [x] Review the model: no concept, field, association or cardinality changes; refresh the inventory and regenerate. Evidence: `--refresh-inventory` then `--check` PASS (54/54 tables, 76/76 FK); HTML/draw.io/PNG unchanged; companions keep their approval.
- [x] Record the refresh in `domain-model-verification.md`, with the CI gap.
- [ ] Open the PR and send it to Josh; close after review and merge.

## repository: CI runs the diagram generator checks

Owner: jinny
Status: In review
Created at: 2026-11-20T15:57:28+07:00
Started at: 2026-11-20T15:57:28+07:00

Authority: Josh (SA Lead) answer to the #275 CI question, `authorized_by: ittikorn`, delivery `open-pr`. Scope: `.github/workflows/checks.yml`, `tasks/jinny`.

- [x] Add a `checks.yml` step running `generate_domain_diagrams.py --check` and `generate_layered_diagrams.py --check` (stdlib only, no draw.io). Evidence: on `main` (`0b2f6ad`) the domain check exits 1 with "DB evidence drift"; on the #275 content both pass.
- [ ] Open the PR and send it to Josh; CI turns green once #275 merges and `main` is merged in; close after merge.
