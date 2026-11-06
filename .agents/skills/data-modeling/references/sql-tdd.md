---
name: SQL Test-Driven Workflow
description: How to write the *.test.sql file for a schema change, watch it fail, make it pass, and prove the tests catch regressions. Read before changing a migration.
---

# SQL tests, red then green

`e-commerce/db/tests/run_db_tests.sh` starts a throw-away PostgreSQL cluster in a temp directory (port 54339), runs every migration up, down in reverse, up again, then runs every `*.test.sql`, and deletes the cluster. It needs `initdb`, `pg_ctl` and `psql` (`brew install postgresql`). It does not touch any other database. Two runs at the same time collide on the port; if one run says `SOME FAILED` for no reason, run it again.

## The cycle

1. Write the test file first (`assets/sql-test.test.sql.tmpl`). One `DO $$ ... $$` block per rule, ending in `RAISE NOTICE 'PASS test N: ...'`.
2. Run `bash e-commerce/db/tests/run_db_tests.sh` against the **old** migration. The new test must fail, with your own `FAIL:` message or the expected missing-column error. If it passes, the test does not test the change; fix the test.
3. Change the migration. Run again. The new tests print `PASS` and the last line is `ALL PASSED`.
4. A test that only guards against a regression (it passes before and after) is fine, say so in the report.

## What a good test does

- Tries the bad input and expects the exact error class: `unique_violation`, `check_violation`, `not_null_violation`, `foreign_key_violation`. Use `BEGIN ... EXCEPTION WHEN <class> THEN NULL; END;` and `RAISE EXCEPTION 'FAIL: ...'` right after the statement that must fail, so an accepted bad row fails the test.
- Tries both sides of a boundary (100 and 100.01, -0.01 and 0).
- For a partial unique index: a duplicate fails; the same value on an `INACTIVE`, `LOCKED` or `ARCHIVED` row still fails; after the row is `DELETED` it can be reused, and reused again after the second delete.
- Fixture rows use fixed UUIDs, and parents are not created because foreign keys are off (`SET LOCAL session_replication_role = replica`). Check a foreign key's `ON DELETE` through `pg_constraint`.
- Never leaves data behind: the file ends with `ROLLBACK;`.

## Prove the tests are sharp

After GREEN, break the migration on purpose (restore a plain `UNIQUE`, remove the `WHERE` of an index, remove a check, make a nullable column NOT NULL), run `run_db_tests.sh`, and confirm it fails. Restore the file afterwards (keep a copy, or use `scripts/mutation_harness.py` with `"check": ["bash", "e-commerce/db/tests/run_db_tests.sh"]`). Report "tests caught n of n broken migrations".
