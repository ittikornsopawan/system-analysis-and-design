-- Tests for WP5 (author): names unique among rows that are not DELETED, pairs unique among rows that are not DELETED,
-- the role scope points at the permission scope, user permission scope, foreign key actions, and the two PLATFORM_ADMIN
-- queries of the delivered specs still use an index.
-- Run after 02-author.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

CREATE TEMP TABLE fx (k TEXT PRIMARY KEY, id UUID) ON COMMIT DROP;
WITH u AS (INSERT INTO authen.m_user (created_by, username, email_address) VALUES ('test', '\x0301'::bytea, '\x0401'::bytea) RETURNING id),
     r AS (INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'PLATFORM_ADMIN', 'admin') RETURNING id),
     p AS (INSERT INTO author.m_permission (created_by, name, description) VALUES ('test', 'catalog.manage', 'catalog') RETURNING id),
     p2 AS (INSERT INTO author.m_permission (created_by, name, description) VALUES ('test', 'order.read', 'orders') RETURNING id),
     s AS (INSERT INTO author.m_scope (created_by, scope, name, description) VALUES ('test', 'ALL', 'All', 'all') RETURNING id),
     s2 AS (INSERT INTO author.m_scope (created_by, scope, name, description) VALUES ('test', 'SHOP', 'Shop', 'shop') RETURNING id)
INSERT INTO fx SELECT 'user', id FROM u UNION ALL SELECT 'role', id FROM r UNION ALL SELECT 'perm', id FROM p UNION ALL SELECT 'perm2', id FROM p2
    UNION ALL SELECT 'scope', id FROM s UNION ALL SELECT 'scope2', id FROM s2;
INSERT INTO author.t_permission_scope (created_by, permission_id, scope_id)
SELECT 'test', (SELECT id FROM fx WHERE k = 'perm'), (SELECT id FROM fx WHERE k = 'scope');
INSERT INTO fx SELECT 'ps', id FROM author.t_permission_scope;

-- test 1: a name used by a non deleted row cannot be used again, INACTIVE, LOCKED and ARCHIVED rows keep it, a DELETED name can be reused
DO $$
DECLARE s TEXT; live INT;
BEGIN
    -- m_role and m_permission have no scope column, so each table is written out
    BEGIN
        INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'PLATFORM_ADMIN', 'again');
        RAISE EXCEPTION 'FAIL: m_role accepted a duplicate name';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO author.m_permission (created_by, name, description) VALUES ('test', 'catalog.manage', 'again');
        RAISE EXCEPTION 'FAIL: m_permission accepted a duplicate name';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO author.m_scope (created_by, scope, name, description) VALUES ('test', 'ALL', 'again', 'again');
        RAISE EXCEPTION 'FAIL: m_scope accepted a duplicate scope';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO author.m_role (created_by, name, description, row_status) VALUES ('test', 'HELD_' || s, 'held', s);
        BEGIN
            INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'HELD_' || s, 'again');
            RAISE EXCEPTION 'FAIL: the name of an % role was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'REUSE_ME', 'v1');
    UPDATE author.m_role SET row_status = 'DELETED' WHERE name = 'REUSE_ME';
    INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'REUSE_ME', 'v2');
    UPDATE author.m_role SET row_status = 'DELETED' WHERE name = 'REUSE_ME' AND row_status = 'ACTIVE';
    INSERT INTO author.m_role (created_by, name, description) VALUES ('test', 'REUSE_ME', 'v3');
    SELECT COUNT(*) INTO live FROM author.m_role WHERE name = 'REUSE_ME' AND row_status <> 'DELETED';
    IF live <> 1 THEN RAISE EXCEPTION 'FAIL: expected one live REUSE_ME role, found %', live; END IF;
    INSERT INTO author.m_permission (created_by, name, description) VALUES ('test', 'reuse.me', 'v1');
    UPDATE author.m_permission SET row_status = 'DELETED' WHERE name = 'reuse.me';
    INSERT INTO author.m_permission (created_by, name, description) VALUES ('test', 'reuse.me', 'v2');
    INSERT INTO author.m_scope (created_by, scope, name, description) VALUES ('test', 'REUSE', 'v1', 'd');
    UPDATE author.m_scope SET row_status = 'DELETED' WHERE scope = 'REUSE';
    INSERT INTO author.m_scope (created_by, scope, name, description) VALUES ('test', 'REUSE', 'v2', 'd');
    RAISE NOTICE 'PASS test 1: names are unique among rows that are not DELETED';
END $$;

-- test 2: a pair is unique among rows that are not DELETED, a revoked pair can be granted again
DO $$
DECLARE u UUID := (SELECT id FROM fx WHERE k = 'user'); r UUID := (SELECT id FROM fx WHERE k = 'role');
        p UUID := (SELECT id FROM fx WHERE k = 'perm'); sc UUID := (SELECT id FROM fx WHERE k = 'scope'); ps UUID := (SELECT id FROM fx WHERE k = 'ps');
        rp UUID;
BEGIN
    BEGIN
        INSERT INTO author.t_permission_scope (created_by, permission_id, scope_id) VALUES ('test', p, sc);
        RAISE EXCEPTION 'FAIL: t_permission_scope accepted the same pair twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE author.t_permission_scope SET row_status = 'DELETED' WHERE id = ps;
    INSERT INTO author.t_permission_scope (created_by, permission_id, scope_id) VALUES ('test', p, sc) RETURNING id INTO ps;
    UPDATE fx SET id = ps WHERE k = 'ps';

    INSERT INTO author.t_role_permission (created_by, role_id, permission_id) VALUES ('test', r, p) RETURNING id INTO rp;
    BEGIN
        INSERT INTO author.t_role_permission (created_by, role_id, permission_id) VALUES ('test', r, p);
        RAISE EXCEPTION 'FAIL: t_role_permission accepted the same pair twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE author.t_role_permission SET row_status = 'DELETED' WHERE id = rp;
    INSERT INTO author.t_role_permission (created_by, role_id, permission_id) VALUES ('test', r, p) RETURNING id INTO rp;
    INSERT INTO fx VALUES ('rp', rp);

    INSERT INTO author.t_role_permission_scope (created_by, role_permission_id, permission_scope_id) VALUES ('test', rp, ps);
    BEGIN
        INSERT INTO author.t_role_permission_scope (created_by, role_permission_id, permission_scope_id) VALUES ('test', rp, ps);
        RAISE EXCEPTION 'FAIL: t_role_permission_scope accepted the same pair twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE author.t_role_permission_scope SET row_status = 'DELETED' WHERE role_permission_id = rp;
    INSERT INTO author.t_role_permission_scope (created_by, role_permission_id, permission_scope_id) VALUES ('test', rp, ps);

    INSERT INTO author.t_user_role (created_by, user_id, role_id) VALUES ('test', u, r);
    BEGIN
        INSERT INTO author.t_user_role (created_by, user_id, role_id) VALUES ('test', u, r);
        RAISE EXCEPTION 'FAIL: t_user_role accepted the same pair twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE author.t_user_role SET row_status = 'DELETED' WHERE user_id = u;
    INSERT INTO author.t_user_role (created_by, user_id, role_id) VALUES ('test', u, r);
    RAISE NOTICE 'PASS test 2: pairs are unique among rows that are not DELETED';
END $$;

-- test 3: a user permission without a scope is unique per user and permission, with a scope per user, permission and scope
DO $$
DECLARE u UUID := (SELECT id FROM fx WHERE k = 'user'); p2 UUID := (SELECT id FROM fx WHERE k = 'perm2');
        p UUID := (SELECT id FROM fx WHERE k = 'perm'); ps UUID := (SELECT id FROM fx WHERE k = 'ps'); x UUID;
BEGIN
    INSERT INTO author.t_user_permission (created_by, user_id, permission_id) VALUES ('test', u, p2) RETURNING id INTO x;
    BEGIN
        INSERT INTO author.t_user_permission (created_by, user_id, permission_id) VALUES ('test', u, p2);
        RAISE EXCEPTION 'FAIL: a second scope-less grant of one permission was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO author.t_user_permission (created_by, user_id, permission_id, permission_scope_id) VALUES ('test', u, p, ps);
    BEGIN
        INSERT INTO author.t_user_permission (created_by, user_id, permission_id, permission_scope_id) VALUES ('test', u, p, ps);
        RAISE EXCEPTION 'FAIL: a second grant of one permission and scope was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE author.t_user_permission SET row_status = 'DELETED' WHERE id = x;
    INSERT INTO author.t_user_permission (created_by, user_id, permission_id) VALUES ('test', u, p2);
    RAISE NOTICE 'PASS test 3: user permission grants are unique per scope';
END $$;

-- test 4: a role scope must be a scope of the permission (it points at t_permission_scope, not at m_scope)
DO $$
DECLARE rp UUID := (SELECT id FROM fx WHERE k = 'rp'); s UUID := (SELECT id FROM fx WHERE k = 'scope2');
BEGIN
    BEGIN
        INSERT INTO author.t_role_permission_scope (created_by, role_permission_id, permission_scope_id) VALUES ('test', rp, s);
        RAISE EXCEPTION 'FAIL: a role permission scope pointing at a plain scope was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conrelid = 'author.t_role_permission_scope'::regclass AND c.contype = 'f'
                   AND c.confrelid = 'author.t_permission_scope'::regclass) THEN
        RAISE EXCEPTION 'FAIL: t_role_permission_scope must reference t_permission_scope';
    END IF;
    RAISE NOTICE 'PASS test 4: role scopes point at the permission scope';
END $$;

-- test 5: foreign key actions: masters are RESTRICT, the user and the role permission of a scope are CASCADE
DO $$
DECLARE bad TEXT; r UUID := (SELECT id FROM fx WHERE k = 'role');
BEGIN
    SELECT string_agg(c.conrelid::regclass || '.' || c.conname, ', ') INTO bad
    FROM pg_constraint c
    WHERE c.contype = 'f' AND c.connamespace = 'author'::regnamespace
      AND c.confrelid IN ('author.m_role'::regclass, 'author.m_permission'::regclass, 'author.m_scope'::regclass, 'author.t_permission_scope'::regclass)
      AND c.confdeltype <> 'r';
    IF bad IS NOT NULL THEN RAISE EXCEPTION 'FAIL: these foreign keys must be ON DELETE RESTRICT: %', bad; END IF;
    SELECT string_agg(c.conrelid::regclass || '.' || c.conname, ', ') INTO bad
    FROM pg_constraint c
    WHERE c.contype = 'f' AND c.connamespace = 'author'::regnamespace
      AND (c.confrelid = 'authen.m_user'::regclass OR c.confrelid = 'author.t_role_permission'::regclass) AND c.confdeltype <> 'c';
    IF bad IS NOT NULL THEN RAISE EXCEPTION 'FAIL: these foreign keys must be ON DELETE CASCADE: %', bad; END IF;
    BEGIN
        DELETE FROM author.m_role WHERE id = r;
        RAISE EXCEPTION 'FAIL: a role that is assigned to a user was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 5: foreign key actions';
END $$;

-- test 6: the two PLATFORM_ADMIN queries of the delivered specs return the role and the assignment and can use the new indexes
DO $$
DECLARE u UUID := (SELECT id FROM fx WHERE k = 'user'); rid UUID; found UUID; plan TEXT := ''; line TEXT;
BEGIN
    SELECT r.id INTO rid FROM author.m_role r WHERE r.name = 'PLATFORM_ADMIN' AND r.row_status = 'ACTIVE';
    IF rid IS NULL THEN RAISE EXCEPTION 'FAIL: the query "Get the platform administrator role" found no role'; END IF;
    SELECT ur.id INTO found FROM author.t_user_role ur WHERE ur.user_id = u AND ur.role_id = rid AND ur.row_status = 'ACTIVE';
    IF found IS NULL THEN RAISE EXCEPTION 'FAIL: the query "Check platform administrator" found no assignment'; END IF;
    -- with sequential scans off, the planner must be able to answer both queries from the partial unique indexes
    SET LOCAL enable_seqscan = off;
    FOR line IN EXECUTE 'EXPLAIN SELECT r.id FROM author.m_role r WHERE r.name = ''PLATFORM_ADMIN'' AND r.row_status = ''ACTIVE''' LOOP
        plan := plan || line || ' ';
    END LOOP;
    IF plan NOT LIKE '%uq_m_role_name%' THEN RAISE EXCEPTION 'FAIL: the role query does not use uq_m_role_name: %', plan; END IF;
    plan := '';
    FOR line IN EXECUTE format('EXPLAIN SELECT ur.id FROM author.t_user_role ur WHERE ur.user_id = %L AND ur.role_id = %L AND ur.row_status = ''ACTIVE''', u, rid) LOOP
        plan := plan || line || ' ';
    END LOOP;
    IF plan NOT LIKE '%uq_t_user_role_user_id_role_id%' THEN RAISE EXCEPTION 'FAIL: the assignment query does not use uq_t_user_role_user_id_role_id: %', plan; END IF;
    RAISE NOTICE 'PASS test 6: the PLATFORM_ADMIN queries return the role and the assignment and use the new indexes';
END $$;

ROLLBACK;
