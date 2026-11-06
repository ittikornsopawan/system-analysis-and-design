-- Tests for cart.t_cart: one ACTIVE line per user and SKU, a SKU is always set, quantity is positive.
-- Run after 05-cart.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the cart constraints, not the parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: one non deleted line per (user, shop, product, SKU), a deleted line can be added again
DO $$
DECLARE
    u UUID := '11111111-1111-4111-8111-111111111111'; s UUID := '22222222-2222-4222-8222-222222222222';
    p UUID := '33333333-3333-4333-8333-333333333333'; k UUID := '44444444-4444-4444-8444-444444444444';
BEGIN
    INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id, quantity) VALUES ('test', u, s, p, k, 2);
    BEGIN
        INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id, quantity) VALUES ('test', u, s, p, k, 1);
        RAISE EXCEPTION 'FAIL: a second ACTIVE line of the same SKU was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- another SKU of the same product is another line
    INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id) VALUES ('test', u, s, p, '55555555-5555-4555-8555-555555555555');
    -- another user may have the same SKU
    INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id) VALUES ('test', '66666666-6666-4666-8666-666666666666', s, p, k);
    -- a deleted line does not block adding the SKU again
    UPDATE cart.t_cart SET row_status = 'DELETED' WHERE user_id = u AND sku_id = k;
    INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id, quantity) VALUES ('test', u, s, p, k, 3);
    RAISE NOTICE 'PASS test 1: one non deleted line per user and SKU';
END $$;

-- test 2: every line has a SKU
DO $$
BEGIN
    BEGIN
        INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id)
        VALUES ('test', '77777777-7777-4777-8777-777777777777', '22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333', NULL);
        RAISE EXCEPTION 'FAIL: a cart line without a SKU was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: sku_id is required';
END $$;

-- test 3: quantity must be positive and defaults to 1
DO $$
DECLARE u UUID := '88888888-8888-4888-8888-888888888888';
BEGIN
    BEGIN
        INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id, quantity)
        VALUES ('test', u, '22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333', '99999999-9999-4999-8999-999999999999', 0);
        RAISE EXCEPTION 'FAIL: quantity 0 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO cart.t_cart (created_by, user_id, shop_id, product_id, sku_id)
    VALUES ('test', u, '22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333', '99999999-9999-4999-8999-999999999999');
    IF NOT EXISTS (SELECT 1 FROM cart.t_cart WHERE user_id = u AND quantity = 1 AND row_status = 'ACTIVE') THEN
        RAISE EXCEPTION 'FAIL: defaults are not quantity 1 and row_status ACTIVE';
    END IF;
    RAISE NOTICE 'PASS test 3: quantity check and defaults';
END $$;

ROLLBACK;
