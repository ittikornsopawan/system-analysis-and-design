---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

Completed records are in `success-task.md`.

## e-commerce: redraw the architecture-design and repository-architecture diagrams from backend `4a8e680`

Owner: jinny
Status: In review
Created at: 2026-11-20T14:40:00+07:00
Started at: 2026-11-20T14:40:00+07:00

Authority: assignment from Josh (SA Lead) session, `authorized_by: ittikorn`, delivery `open-pr`. Scope: `layered_core_content.py`, the two diagram bundles, `e-commerce/diagram/README.md`, `e-commerce/doc/code-structure.md`, `tasks/jinny`.

- [x] Read the backend at `4a8e680` (`git ls-tree`, `.csproj` references, `Program.cs`, controllers, DI) and the tables of `code-structure.md`.
- [x] Redraw both views in `layered_core_content.py`: current controllers, filters, `ITransactionRunner`/`EfTransactionRunner`, `EcommerceDbContext` + `ForUpdate()`/`AdvisoryLock`, per-use-case repositories, `FieldTransport`, `ValidationMessages`, Business Domain as CODE; four test projects and 9 + 7 references. No `GetCurrentUser`, Dapper, `DbSession`, `UnitOfWork`, `IAuthenRepositories` or scaffold entities.
- [x] Regenerate HTML/draw.io, export with draw.io Desktop, finalize the PNGs, view both renders and fix the clipped rows. Evidence: `generate_layered_diagrams.py --check` PASS; `verify_diagram.py --require-nested` PASS for both PNGs (2378 x 1682).
- [x] Update both companions, the diagram README and remove the "first scaffold" notes from `code-structure.md`.
- [x] Run every `check_docs.py` sub-command. Evidence: 73/73 pass.
- [ ] Open the PR and send it to Josh; close after review and merge.
