---
name: Jinny Task Plan
description: Active plans and task records of the Diagram Designer Jinny, resolved from the workspace key jinny in the agent registry.
---

# Jinny Tasks

Completed records are in `success-task.md`.

## e-commerce: domain diagrams cover the 54-table database (`public.m_parameter`)

Owner: jinny
Status: In progress
Created at: 2026-11-18T07:34:31+07:00
Started at: 2026-11-18T07:34:31+07:00

Authority: assignment from Josh (SA Lead), `authorized_by: ittikorn`, delivery `open-pr`. Scope: `e-commerce/diagram`, `e-commerce/scripts/diagrams`, `tasks/jinny`.

- [x] Map `public.m_parameter` to a concept and place it in the identity view's `public` group with `public.t_key`; update the overview family and every 53/75 count to 54/76.
- [x] Refresh the inventory and regenerate HTML, draw.io and companions; companions whose body changes go back to `in-review`.
- [x] Export and finalize the PNGs of every changed view and look at them.
- [x] Update `domain-model-verification.md`, `README.md` and `design/handoff-verification.md` to 54 tables.
- [x] Run every check of the team protocol and the preflight. Evidence: `generate_domain_diagrams.py --check` PASS (54/54 tables, 76/76 FK); check_docs 72/72; audit_all 54 tables 0 findings; test_sequence_skeleton OK; test_agent_workspace 27 OK; diagram-creator tests OK; the 4 PNGs viewed.
- [ ] Open the PR, send it to Josh when CI is green.
