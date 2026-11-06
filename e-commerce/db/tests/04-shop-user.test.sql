-- Tests for shop.t_shop_user (members of a shop): one membership per shop and user among rows that are not DELETED.
-- Run after 04-shop.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the constraints of the table, not its parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: a user can be a member of a shop once among the rows that are not DELETED
DO $$
DECLARE
    a UUID := '55555555-5555-4555-8555-555555555555';
    b UUID := '66666666-6666-4666-8666-666666666666';
    u UUID := '77777777-7777-4777-8777-777777777777';
    v UUID := '88888888-8888-4888-8888-888888888888';
    s TEXT;
BEGIN
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, u, 'ADMIN');
    BEGIN
        INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, u, 'STAFF');
        RAISE EXCEPTION 'FAIL: the same user was added twice to a shop';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- the same user in another shop and another user in the same shop are different memberships
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', b, u, 'STAFF');
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, v, 'STAFF');
    -- INACTIVE, LOCKED and ARCHIVED memberships still hold the place
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        UPDATE shop.t_shop_user SET row_status = s WHERE shop_id = a AND user_id = v AND row_status <> 'DELETED';
        BEGIN
            INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, v, 'STAFF');
            RAISE EXCEPTION 'FAIL: a user with an % membership was added again', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 1: one membership per shop and user among non deleted rows';
END $$;

-- test 2: after a soft delete the user can be added again, also more than once
DO $$
DECLARE
    a UUID := '55555555-5555-4555-8555-555555555555';
    u UUID := '99999999-9999-4999-8999-999999999999';
    live INT;
BEGIN
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, u, 'STAFF');
    UPDATE shop.t_shop_user SET row_status = 'DELETED' WHERE shop_id = a AND user_id = u;
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, u, 'ADMIN');
    UPDATE shop.t_shop_user SET row_status = 'DELETED' WHERE shop_id = a AND user_id = u AND row_status = 'ACTIVE';
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, u, 'STAFF');
    SELECT COUNT(*) INTO live FROM shop.t_shop_user WHERE shop_id = a AND user_id = u AND row_status <> 'DELETED';
    IF live <> 1 THEN
        RAISE EXCEPTION 'FAIL: expected one live membership, found %', live;
    END IF;
    RAISE NOTICE 'PASS test 2: a deleted member can be added again';
END $$;

-- test 3: role is ADMIN or STAFF and defaults to STAFF
DO $$
DECLARE
    a UUID := '55555555-5555-4555-8555-555555555555';
BEGIN
    INSERT INTO shop.t_shop_user (created_by, shop_id, user_id) VALUES ('test', a, 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
    IF (SELECT role FROM shop.t_shop_user WHERE user_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa') <> 'STAFF' THEN
        RAISE EXCEPTION 'FAIL: role must default to STAFF';
    END IF;
    BEGIN
        INSERT INTO shop.t_shop_user (created_by, shop_id, user_id, role) VALUES ('test', a, 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb', 'OWNER');
        RAISE EXCEPTION 'FAIL: an unknown role was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: role is ADMIN or STAFF, default STAFF';
END $$;

ROLLBACK;
