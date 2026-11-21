---
name: Verification and Reporting
description: The checkers to run, how to mutation-test a checker, and the report format (files, pasted results, decisions with why and cost, open questions) used for every schema or API task. Shared by data-modeling and api-contract-design.
---

# Verification and reporting

## Run from the repository root

```bash
for c in $(python3 e-commerce/db/tests/check_docs.py 2>&1 | sed -n 2p | sed 's/subcommands: //; s/,//g'); do printf "%s: " $c; python3 e-commerce/db/tests/check_docs.py $c | tail -1; done
python3 e-commerce/db/tests/audit_all.py
bash e-commerce/db/tests/run_db_tests.sh
```

- `check_docs.py <sub-command>`: one check per area (`schema`, `shop-schema`, `er`, `er-lot`, `spec01`–`spec03`, `cart-spec`, `order-spec`, `shop-*-spec`, `shop-*-schema`, `status-codes`, `biz-codes`). The first line without arguments lists them. Every line must start with `OK`.
- `audit_all.py`: all tables against schema doc, README, ER and every SQL block in every spec (tables and columns). The result must be `... 0 findings`.
- `run_db_tests.sh`: migrations up, down, up and every `*.test.sql`; the last line must be `ALL PASSED`.
- Several people (or sessions) edit `check_docs.py`. Read the file again right before you save an edit to it, and add your sub-command next to its neighbours instead of reformatting.

## Mutation-test every checker you add or rely on

A checker that has never failed is not evidence. Break the thing it should protect, in place, run it, expect a failure, and restore. `scripts/mutation_harness.py` does that safely from a JSON list of cases. Cover: a wrong number in an example, a removed rule sentence, a removed SQL guard, a misspelled column in a spec SQL, a changed HTTP code, a leaked field in a public API. When a mutation slips through, tighten the checker (a too-broad text match is the usual cause) and rerun all cases. Report `caught / total`.

## Report format

Use `assets/decision-report.md.tmpl`. The four parts the owner reads: (1) files added or changed, (2) real pasted results, (3) every decision you made yourself, (4) open questions.

A decision has three parts: **what** you decided, **why**, and **what it costs if it is wrong** (which files and how much rework). Mark it "decided by the lead SA, pending product owner confirmation" until the owner answers, then "approved by the product owner" (and write that sentence into the spec).

Rules for the report:

- Do not stay silent about assumptions. A business rule you had to guess is a decision.
- A problem you find in someone else's delivered work is reported separately; fix it only after the owner agrees, and then list it as a decision.
- Do not `git add` or commit. The owner commits by hand.
- Do not claim "done" without the pasted results. If something could not run, say what and why.
