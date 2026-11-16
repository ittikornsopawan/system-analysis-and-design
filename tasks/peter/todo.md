---
name: Peter Task Plan
description: Active plans and task records of the System Analyst Peter, resolved from the workspace key peter in the agent registry.
---

# Peter Tasks

## e-commerce: shop roles design (owner, admin, staff; draft for the owner's decision)

Owner: peter
Status: In progress
Created at: 2026-11-14T18:03:13+07:00
Started at: 2026-11-14T18:03:13+07:00

Authority: the owner's answers of 2026-11-14 (relayed by Josh, SA Lead): the shop owner is a separate identity and not the shop ADMIN, a shop can have several owners, and owner, admin and staff are separate roles with fixed permissions; the SA Lead asked for a design draft first. Assignment `authorized_by: josh`, delivery `open-pr`. Nothing is approved and no schema, specification, checker, test or matrix row is changed by this task.

- [x] Collect the evidence: the `shop.t_shop_user` role constraint and unique index, the ADMIN and creator rules of `shop/08`, `shop/09`, `shop/11`, `shop/12`, the seventeen specs whose SQL checks the member role, the matrix rows of the shop APIs, the tests and the seed.
- [x] Write `docs/superpowers/specs/2026-11-14-shop-roles-design.md` with status draft (revised for the several-owner answer): D1 storage (role OWNER in `t_shop_user`, alternative `is_owner`), D2 the fixed permission table per shop API, D3 minimum rules, D4 creator, D5 who changes owners and leaving, D6 JWT or API check, D7 impact and order of work; each with a recommendation, the cost if wrong and a question (Q1–Q7).
- [x] The SA Lead put the questions to the owner and returned the answers (2026-11-14): Q1 `OWNER` as a third role value, Q2 the permission table as written, Q3 at least one ACTIVE OWNER replaces the ADMIN rule, Q4 the creator is OWNER, Q5 owners are added by promoting members and an owner leaves only while another ACTIVE owner remains, Q6 the role is checked in the database and not in the JWT; Q7 follows the order of work of D7 (SA Lead). Recorded in the document, renamed to `shop-roles-design`, status `in-review`.
- [x] The owner changes the status of the document to approved; only then is a schema or specification change planned (work not started, held for the owner's approval). Evidence: owner answer of 2026-11-16 (AskUserQuestion to the SA Lead); recorded in the frontmatter by the approvals pull request.

Verification: `md-frontmatter` check OK for the new design file and this task file; no other file is changed.

## e-commerce: frontmatter for five design documents

Owner: peter
Status: In progress
Created at: 2026-11-14T19:00:00+07:00
Started at: 2026-11-14T19:00:00+07:00

Authority: the SA Lead's assignment of 2026-11-14 (authorized_by josh): add frontmatter with status in-review and null approval fields, because the SA Lead cannot approve for the owner; the approval evidence found in the documents goes to the pull request body for the owner to decide.

- [x] Add name, description, `status: in-review`, `approved_by: null`, `approved_at: null` to the product SKU multi-level, cart, order, payment and shop lot pricing design documents.
- [x] Reconcile `MD_FRONTMATTER_PENDING` with the five newly frontmatter-complete design documents and the six already-complete shop API specs incorrectly added to the list.
- [x] Run the frontmatter checker and all required documentation checks on the PR branch.
- [x] The owner decides whether any of the five documents becomes `approved` (the evidence is listed in the pull request body; no status is changed here). Evidence: owner answer of 2026-11-16 (AskUserQuestion to the SA Lead); recorded in the frontmatter by the approvals pull request.

Progress (2026-11-14T19:49:25+07:00): PR #137's `md-frontmatter` action fails on 11 paths. The original task statement that the five entries were removed is not supported by the PR diff; the branch also added six shop API specs that already have frontmatter. Reproduced the exact failure on PR head `09f73d458aa10625cffa0a1fbfad6f6300635f02`; the earlier successful run was from the primary checkout, not this managed branch.

Progress (2026-11-14T19:52:01+07:00): Set `MD_FRONTMATTER_PENDING` to the empty tuple because all tracked Markdown specifications currently have frontmatter. The first preflight found unrelated paths because local `main` was at `bf6d033`; fetched `origin/main` into local `main` at `3ed244d` and the same preflight then had no blockers.

Verification (before task-branch integration): `md-frontmatter` reports `OK: md-frontmatter (263 Markdown files; 0 specs without frontmatter yet)`; delivery preflight reports `check_docs.py: 69/69 OK`, `audit_all.py: 53 tables audited, 0 findings`, and `run_db_tests.sh: ALL PASSED`. Preflight reports no blockers. Re-run affected checks after integrating the latest base.

Progress (2026-11-14T19:58:27+07:00): Fetched `origin/main` at `3ed244d1043c1757febaf5f762abe90606f7e899`; `git merge --no-commit origin/main` reported `Already up to date`. Verified the base is an ancestor, the unmerged index is empty, and the final eight-path diff stays in the recorded assignment scope.

Verification (after base integration): all 69 `check_docs.py` sub-commands pass; `md-frontmatter` reports 263 Markdown files and 0 pending specs; `audit_all.py` reports 53 tables audited, 0 findings; `run_db_tests.sh` reports `ALL PASSED`. Direct post-integration checks were used because preflight after commit reported no uncommitted files and therefore did not run project checkers.
