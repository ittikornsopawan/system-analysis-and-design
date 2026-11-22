---
name: Marry Task Plan
description: Active plans and task records of the System Analyst Marry, resolved from the workspace key marry in the agent registry.
---

# Marry Tasks

Completed records are in `success-task.md`.

## e-commerce: author 12 and 17 login anchor links

Owner: marry
Status: In progress
Created at: 2026-11-22T08:44:07+07:00
Started at: 2026-11-22T08:44:07+07:00

Assignment: agent `marry`, delivery `open-pr`, authorized by `ittikorn`, workspace `.workspace/marry`, branch `docs/marry-author-login-anchor`, scopes `e-commerce/doc/api/author/12-me`, `e-commerce/doc/api/author/17-check-permission`, `tasks/marry`. Found by Drake while checking links for #299.

- [x] Change the login link in `12-me/sequence.wsd` and `17-check-permission/sequence.wsd` from `#claim-resolution-and-payload` (no such heading) to `#example-jwt-payload` (`#### Example JWT Payload` in `authen-and-author/02-login/spec.md`); no other `claim-resolution-and-payload` link in the repository. Link fix only, no behaviour change.
- [x] Verification: every step of `.github/workflows/checks.yml` run locally: OpenAPI validator 0.9.0 OK, `audit_all.py` 0 findings, the 7 `check_docs.py` checks OK (`api-sequence-spec` 91 specs, `md-frontmatter` 389 files), both diagram generators `--check` PASS, both tooling test suites OK, skill copies equal.
- [ ] Open the PR and ask Josh to confirm the edit of the two approved specs; never merge.
