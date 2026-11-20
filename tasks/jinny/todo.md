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

## repository: CI runs the diagram generator checks

Owner: jinny
Status: In review
Created at: 2026-11-20T15:57:28+07:00
Started at: 2026-11-20T15:57:28+07:00

Authority: Josh (SA Lead) answer to the #275 CI question, `authorized_by: ittikorn`, delivery `open-pr`. Scope: `.github/workflows/checks.yml`, `tasks/jinny`.

- [x] Add a `checks.yml` step running `generate_domain_diagrams.py --check` and `generate_layered_diagrams.py --check` (stdlib only, no draw.io). Evidence: on `main` (`0b2f6ad`) the domain check exits 1 with "DB evidence drift"; on the #275 content both pass.
- [ ] Open the PR and send it to Josh; CI turns green once #275 merges and `main` is merged in; close after merge.
