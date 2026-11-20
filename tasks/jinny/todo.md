---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

Completed records are in `success-task.md`.

## e-commerce: remove the dead first-scaffold diagram content

Owner: jinny
Status: In review
Created at: 2026-11-20T15:48:12+07:00
Started at: 2026-11-20T15:48:12+07:00

Authority: Josh (SA Lead) review of #269, option (b); `authorized_by: ittikorn`, delivery `open-pr`. Scope: `diagram_content.py`, `generate_diagrams.py`, `tasks/jinny`.

- [x] Delete the unused `ARCHITECTURE`/`REPOSITORY`/`SYSTEM` content and `DIAGRAMS` (Josh approved the last two in review), `verify_evidence()` (pinned 2 test projects / 5 refs) and the unreachable tail of `generate_diagrams.main`, with the imports only they used. Evidence: `git grep` finds no other user of `verify_evidence`, `PROJECT` or `DIAGRAMS` outside the deleted code.
- [x] Run the generators and every `check_docs.py` sub-command. Evidence: layered `--check` PASS, `generate_diagrams.py --check` PASS, check_docs 73/73. `generate_domain_diagrams.py --check` fails with "DB evidence drift" on `origin/main` `ed93259` too (pre-existing, reported to Josh).
- [ ] Open the PR and send it to Josh; close after review and merge.

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
