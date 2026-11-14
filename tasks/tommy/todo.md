---
name: Tommy Task Plan
description: Active plans and task records of the agent Tommy (System Analyst); read it to see what Tommy is working on, its status and its verification evidence.
---

# Tommy Tasks

## e-commerce: spec frontmatter, cart, payment, sales, shipping and campaign

Owner: tommy
Status: In review (pull request open)
Created at: 2026-11-14T17:30:00+07:00
Started at: 2026-11-14T17:40:00+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-frontmatter`, scopes `e-commerce/doc/api/cart`, `e-commerce/doc/api/payment`, `e-commerce/doc/api/sales`, `e-commerce/doc/api/shipping`, `e-commerce/doc/api/campaign`, `e-commerce/db/tests/check_docs.py`, `.agents/skills/data-modeling/SKILL.md`, `tasks/tommy`.

- [x] Add the frontmatter (`name`, `description`, `status: in-review`, `approved_by: null`, `approved_at: null`) to the 18 specs of the five groups that had none, as the owner decided on 2026-11-14; `name` is the Name of the API table, `description` states the purpose and when to read the spec. Evidence: `git diff --numstat` shows only added lines in `e-commerce/doc/api`, and `md-frontmatter` passes with the 18 specs removed from `MD_FRONTMATTER_PENDING`.
- [x] Make `md-frontmatter` print a readable FAIL instead of a traceback outside a git checkout. Evidence: a copy of `check_docs.py` in a temporary folder without `.git` printed `FAIL: md-frontmatter needs a git checkout`.
- [x] Correct the line of `.agents/skills/data-modeling/SKILL.md` that said the files copied from `assets/` have no frontmatter.
- [x] Run every check. Evidence: `check_docs.py` 69/69 OK, `audit_all.py` 53 tables audited and 0 findings, `run_db_tests.sh` ALL PASSED.
- [ ] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend. Next: the five specs of `docs/superpowers/specs` that still have no frontmatter, when the owner decides their status.

## e-commerce: spec template and frontmatter, shop 11 to 16

Owner: tommy
Status: In review (pull request open)
Created at: 2026-11-14T18:19:38+07:00
Started at: 2026-11-14T18:19:38+07:00

Assignment: agent `tommy`, delivery `open-pr`, authorized by `josh`, workspace `.workspace/tommy`, branch `docs/tommy-spec-template-shop-3`, scopes `e-commerce/doc/api/shop/11-upsert-shop-user` to `16-inquiry-storefront-product-review`, `e-commerce/db/tests/check_docs.py`, `tasks/tommy`. This is the last of three shop PRs.

- [x] Remove `### Shop User Rules` (shop/11, shop/12), `### Shop User Inquiry Rules`, `### Shop Product List Rules`, `### Review Rules` and `### Review Inquiry Rules`; the rules and the approval sentence of each section are short bullets under `## Domain`, the lock rule and the order of the checks are notes of `sequence.wsd`; the links to other specs become plain words; no SQL and no behavior is changed. Evidence: `verify_seq.py` OK for the six folders, strict SQL parity and render; every removed line is found again in the spec or its note.
- [x] Add the frontmatter (`status: in-review`) to the six specs; remove them from `LEGACY_SPEC_TEMPLATE` and `MD_FRONTMATTER_PENDING`; the shop user and review checkers look for each rule in the file where it lives (the moved rules in the sequence only).
- [x] Run every check. Evidence: see the pull request.
- [ ] Open the pull request with `commit-and-pr`, tell the lead SA when CI is green, then suspend.
