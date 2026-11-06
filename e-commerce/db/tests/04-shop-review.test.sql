-- Tests for shop.t_shop_product_review (reviews of a product sold by a shop): one review per user and shop product
-- among the rows that are not DELETED, rating from 1 to 5, comment is optional.
-- Run after 04-shop.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the constraints of the table, not its parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: a user can review a shop product once among the rows that are not DELETED
DO $$
DECLARE
    sp1 UUID := '71717171-7171-4717-8717-717171717171';
    sp2 UUID := '72727272-7272-4727-8727-727272727272';
    u1 UUID := '73737373-7373-4737-8737-737373737373';
    u2 UUID := '74747474-7474-4747-8747-747474747474';
    s TEXT;
BEGIN
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating, comment) VALUES ('test', sp1, u1, 5, 'Good');
    BEGIN
        INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating, comment) VALUES ('test', sp1, u1, 4, 'Again');
        RAISE EXCEPTION 'FAIL: the same user reviewed the same shop product twice';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- another user, and the same user on another shop product, are different reviews
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp1, u2, 3);
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp2, u1, 2);
    -- INACTIVE, LOCKED and ARCHIVED reviews still hold the place
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        UPDATE shop.t_shop_product_review SET row_status = s WHERE shop_product_id = sp2 AND user_id = u1 AND row_status <> 'DELETED';
        BEGIN
            INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp2, u1, 1);
            RAISE EXCEPTION 'FAIL: a user with an % review wrote another one', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 1: one review per user and shop product among non deleted rows';
END $$;

-- test 2: after a soft delete the user can write a new review, also more than once
DO $$
DECLARE
    sp UUID := '75757575-7575-4757-8757-757575757575';
    u UUID := '76767676-7676-4767-8767-767676767676';
    live INT;
BEGIN
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp, u, 5);
    UPDATE shop.t_shop_product_review SET row_status = 'DELETED' WHERE shop_product_id = sp AND user_id = u;
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp, u, 4);
    UPDATE shop.t_shop_product_review SET row_status = 'DELETED' WHERE shop_product_id = sp AND user_id = u AND row_status = 'ACTIVE';
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp, u, 3);
    SELECT COUNT(*) INTO live FROM shop.t_shop_product_review WHERE shop_product_id = sp AND user_id = u AND row_status <> 'DELETED';
    IF live <> 1 THEN
        RAISE EXCEPTION 'FAIL: expected one live review, found %', live;
    END IF;
    RAISE NOTICE 'PASS test 2: a deleted review can be written again';
END $$;

-- test 3: rating is 1 to 5, the comment is optional, a new review is ACTIVE
DO $$
DECLARE
    sp UUID := '77777777-7777-4777-8777-777777777771';
    r INT;
BEGIN
    FOREACH r IN ARRAY ARRAY[0, 6, -1] LOOP
        BEGIN
            INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp, gen_random_uuid(), r);
            RAISE EXCEPTION 'FAIL: rating % was accepted', r;
        EXCEPTION WHEN check_violation THEN NULL;
        END;
    END LOOP;
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating) VALUES ('test', sp, gen_random_uuid(), 1);
    INSERT INTO shop.t_shop_product_review (created_by, shop_product_id, user_id, rating, comment) VALUES ('test', sp, gen_random_uuid(), 5, NULL);
    IF EXISTS (SELECT 1 FROM shop.t_shop_product_review WHERE shop_product_id = sp AND row_status <> 'ACTIVE') THEN
        RAISE EXCEPTION 'FAIL: a new review must default to ACTIVE';
    END IF;
    RAISE NOTICE 'PASS test 3: rating 1 to 5, comment optional, default ACTIVE';
END $$;

ROLLBACK;
