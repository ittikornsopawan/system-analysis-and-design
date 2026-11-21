---
name: Jinny Archived Tasks
description: Cancelled or superseded task records of the Diagram Designer Jinny, with closure time and reason.
---

# Jinny Archived Tasks

## e-commerce: domain diagram `--check` passes again (`ix_m_parameter_parent_id`)

Owner: jinny
Status: Superseded
Created at: 2026-11-20T15:53:39+07:00
Closed at: 2026-11-20T21:46:05+07:00

Reason: #275 shows as merged on GitHub (2026-11-20T09:05:32Z, `d820b45`), but its commits (`d117eda`, `5c652d5`) are not on `main`. #283 (merged 2026-11-20T14:46:05Z) redid the inventory refresh; the verification record is re-added by the diagram-checks PR. Josh (SA Lead) decided not to restore #275.

## repository: CI runs the diagram generator checks (#276)

Owner: jinny
Status: Superseded
Created at: 2026-11-20T15:57:28+07:00
Closed at: 2026-11-20T21:48:08+07:00

Reason: #276 was closed unmerged on Josh's decision. The owner's merge `c9b1eb5` brought commits into its branch that are not on `main` (#275 `d117eda`/`5c652d5`, #277 `30ed031`, `82a16db`), so merging `main` would have put them back under a CI PR. The step is re-done from current `main` in `ci/jinny-diagram-checks`. The branch stays on origin.
