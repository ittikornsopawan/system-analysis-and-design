-- Tests for the author seed (db/seed/author.seed.sql) and the first administrator command (db/seed/grant-platform-admin.sql).
-- Run after the migrations. The seed is only run here, run_db_tests.sh does not run it by itself. Everything is rolled back.
\set ON_ERROR_STOP on
BEGIN;

-- the seed can run twice and creates no user and no grant
\ir ../seed/author.seed.sql
\ir ../seed/author.seed.sql

-- test 1: the seed creates the system role, the scopes and the permission list once, and nothing else
DO $$
DECLARE n INT;
BEGIN
    SELECT COUNT(*) INTO n FROM author.m_role WHERE name = 'PLATFORM_ADMIN' AND row_status = 'ACTIVE' AND created_by = 'system';
    IF n <> 1 THEN RAISE EXCEPTION 'FAIL: expected one ACTIVE PLATFORM_ADMIN role, found %', n; END IF;
    SELECT COUNT(*) INTO n FROM author.m_role;
    IF n <> 1 THEN RAISE EXCEPTION 'FAIL: the seed must create only the PLATFORM_ADMIN role, found % roles', n; END IF;
    SELECT COUNT(*) INTO n FROM author.m_scope WHERE scope IN ('ALL', 'SHOP', 'OWN') AND row_status = 'ACTIVE';
    IF n <> 3 THEN RAISE EXCEPTION 'FAIL: expected the scopes ALL, SHOP and OWN, found %', n; END IF;
    SELECT COUNT(*) INTO n FROM author.m_permission WHERE row_status = 'ACTIVE'
        AND name IN ('catalog.manage', 'consent.manage', 'shop.manage', 'order.read', 'payment.refund', 'shipping.manage', 'author.manage');
    IF n <> 7 THEN RAISE EXCEPTION 'FAIL: expected 7 permissions, found %', n; END IF;
    SELECT COUNT(*) INTO n FROM author.t_permission_scope WHERE row_status = 'ACTIVE';
    IF n <> 12 THEN RAISE EXCEPTION 'FAIL: expected 12 permission scopes, found %', n; END IF;
    IF (SELECT COUNT(*) FROM authen.m_user) <> 0 THEN RAISE EXCEPTION 'FAIL: the seed must not create a user'; END IF;
    IF (SELECT COUNT(*) FROM author.t_user_role) <> 0 OR (SELECT COUNT(*) FROM author.t_role_permission) <> 0 OR (SELECT COUNT(*) FROM author.t_user_permission) <> 0 THEN
        RAISE EXCEPTION 'FAIL: the seed must not grant anything';
    END IF;
    RAISE NOTICE 'PASS test 1: the seed creates the role, scopes and permissions once and grants nothing';
END $$;

CREATE TEMP TABLE fx_user (n INT PRIMARY KEY, id UUID) ON COMMIT DROP;
WITH a AS (INSERT INTO authen.m_user (created_by, username, email_address) VALUES ('test', '\x0501'::bytea, '\x0601'::bytea) RETURNING id),
     b AS (INSERT INTO authen.m_user (created_by, username, email_address) VALUES ('test', '\x0502'::bytea, '\x0602'::bytea) RETURNING id),
     c AS (INSERT INTO authen.m_user (created_by, username, email_address, row_status) VALUES ('test', '\x0503'::bytea, '\x0603'::bytea, 'INACTIVE') RETURNING id)
INSERT INTO fx_user SELECT 1, id FROM a UNION ALL SELECT 2, id FROM b UNION ALL SELECT 3, id FROM c;
SELECT id AS ua FROM fx_user WHERE n = 1 \gset
SELECT id AS ub FROM fx_user WHERE n = 2 \gset
SELECT id AS uc FROM fx_user WHERE n = 3 \gset

-- test 2: a user that is not ACTIVE is not made an administrator
\set user_id :uc
\ir ../seed/grant-platform-admin.sql
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM author.t_user_role) <> 0 THEN RAISE EXCEPTION 'FAIL: a user that is not ACTIVE became an administrator'; END IF;
    RAISE NOTICE 'PASS test 2: a user that is not ACTIVE is refused';
END $$;

-- test 3: with no administrator the command grants the role, with one it refuses another user
\set user_id :ua
\ir ../seed/grant-platform-admin.sql
\set user_id :ub
\ir ../seed/grant-platform-admin.sql
DO $$
DECLARE ua UUID := (SELECT id FROM fx_user WHERE n = 1);
BEGIN
    IF (SELECT COUNT(*) FROM author.t_user_role WHERE row_status = 'ACTIVE') <> 1 THEN RAISE EXCEPTION 'FAIL: the command must leave exactly one administrator'; END IF;
    IF NOT EXISTS (SELECT 1 FROM author.t_user_role WHERE user_id = ua AND row_status = 'ACTIVE' AND created_by = 'system') THEN
        RAISE EXCEPTION 'FAIL: the first user was not made an administrator by the system';
    END IF;
    RAISE NOTICE 'PASS test 3: the first administrator is granted and a second one is refused';
END $$;

-- test 4: an administrator whose assignment is not ACTIVE, or whose user is not ACTIVE, does not count, and a closed assignment is opened again
UPDATE author.t_user_role SET row_status = 'INACTIVE' WHERE user_id = :'ua';
\set user_id :ub
\ir ../seed/grant-platform-admin.sql
UPDATE authen.m_user SET row_status = 'INACTIVE' WHERE id = :'ub';
\set user_id :ua
\ir ../seed/grant-platform-admin.sql
DO $$
DECLARE ua UUID := (SELECT id FROM fx_user WHERE n = 1);
BEGIN
    IF NOT EXISTS (SELECT 1 FROM author.t_user_role WHERE user_id = ua AND row_status = 'ACTIVE') THEN
        RAISE EXCEPTION 'FAIL: the closed assignment of the first user was not opened again when the only holder was not ACTIVE';
    END IF;
    IF (SELECT COUNT(*) FROM author.t_user_role WHERE user_id = ua) <> 1 THEN RAISE EXCEPTION 'FAIL: the command must reuse the closed row, not add a second one'; END IF;
    RAISE NOTICE 'PASS test 4: holders that are not ACTIVE do not count and a closed row is opened again';
END $$;

ROLLBACK;
