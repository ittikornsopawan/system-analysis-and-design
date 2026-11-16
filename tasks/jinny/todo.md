---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

## e-commerce: domain diagram generator `--check` passes on main again

Owner: jinny
Status: In progress
Created at: 2026-11-16T14:47:05+07:00
Started at: 2026-11-16T14:47:05+07:00

Authority: assignment from Josh (SA Lead), `authorized_by: ittikorn`, delivery `open-pr`. Scope: `e-commerce/diagram/domain`, `e-commerce/scripts/diagrams/generate_domain_diagrams.py`, `tasks/jinny`.

- [x] Reproduce: `generate_domain_diagrams.py --check` fails on `1e5d2a2` with "DB evidence drift"; diff the inventory against fresh evidence (category RESTRICT, 2 partial unique indexes, `t_shop_user` OWNER, schema-doc frontmatter hashes).
- [x] Generator keeps a companion's approval frontmatter when only the baseline-commit line differs; a changed body returns to `in-review`.
- [x] Refresh the inventory and regenerate; HTML, draw.io and PNG unchanged; merchandising and commerce companions back to `in-review` for the owner's re-approval.
- [x] Record the refresh in `domain-model-verification.md`.
- [ ] Run every check of the team protocol and render the 4 views.
- [ ] Open the PR, send it to Josh when CI is green.
