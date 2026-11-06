-- Tests for sales.t_order_item: every item is sold from a SKU and from one lot (the price and the cost live on the lot).
-- Run after 06-sales.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the columns of the order item, not the parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: an order item without a SKU is rejected, with a SKU it is accepted
DO $$
DECLARE
    o UUID := '11111111-1111-4111-8111-111111111111'; s UUID := '22222222-2222-4222-8222-222222222222';
    p UUID := '33333333-3333-4333-8333-333333333333';
BEGIN
    BEGIN
        INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
        VALUES ('test', o, s, p, NULL, '88888888-8888-4888-8888-888888888888', 2, 100, 0, 200, 40);
        RAISE EXCEPTION 'FAIL: an order item without a SKU was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
    VALUES ('test', o, s, p, '44444444-4444-4444-8444-444444444444', '88888888-8888-4888-8888-888888888888', 2, 100, 0, 200, 40);
    RAISE NOTICE 'PASS test 1: sku_id is required on an order item';
END $$;

-- test 2: one item per SKU in an order, total_price must equal price x quantity
DO $$
DECLARE
    o UUID := '55555555-5555-4555-8555-555555555555'; s UUID := '22222222-2222-4222-8222-222222222222';
    p UUID := '33333333-3333-4333-8333-333333333333'; k UUID := '66666666-6666-4666-8666-666666666666';
BEGIN
    INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
    VALUES ('test', o, s, p, k, '88888888-8888-4888-8888-888888888888', 1, 50, 0, 50, 10);
    BEGIN
        INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
        VALUES ('test', o, s, p, k, '88888888-8888-4888-8888-888888888888', 1, 50, 0, 50, 10);
        RAISE EXCEPTION 'FAIL: the same SKU twice in one order was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
        VALUES ('test', o, s, p, '77777777-7777-4777-8777-777777777777', '88888888-8888-4888-8888-888888888888', 2, 50, 0, 99, 10);
        RAISE EXCEPTION 'FAIL: total_price different from price x quantity was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: one item per SKU and total_price = price x quantity';
END $$;

-- test 3: an order item without the lot it was sold from is rejected (the cost of the lot gives the profit)
DO $$
BEGIN
    BEGIN
        INSERT INTO sales.t_order_item (created_by, order_id, shop_id, product_id, sku_id, lot_id, quantity, price, discount, total_price, gross_profit)
        VALUES ('test', '99999999-9999-4999-8999-999999999999', '22222222-2222-4222-8222-222222222222', '33333333-3333-4333-8333-333333333333',
                'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', NULL, 1, 50, 0, 50, 10);
        RAISE EXCEPTION 'FAIL: an order item without a lot was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: lot_id is required on an order item';
END $$;

-- test 4: total_amount = total_price - total_discount + total_tax + total_shipping
DO $$
DECLARE
    u UUID := '11111111-1111-4111-8111-111111111111'; s UUID := '22222222-2222-4222-8222-222222222222';
    a UUID := 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
BEGIN
    INSERT INTO sales.t_order (created_by, user_id, shop_id, address_id, code, total_price, total_discount, total_tax, total_shipping, total_amount,
        expires_at, ship_title, ship_address, ship_city, ship_state, ship_postal_code, ship_country)
    VALUES ('test', u, s, a, 'ORD-1', 100, 10, 7, 20, 117, NOW() + INTERVAL '30 minutes', 'Home', '\x01', '\x01', '\x01', '\x01', '\x01');
    BEGIN
        INSERT INTO sales.t_order (created_by, user_id, shop_id, address_id, code, total_price, total_discount, total_tax, total_shipping, total_amount,
            expires_at, ship_title, ship_address, ship_city, ship_state, ship_postal_code, ship_country)
        VALUES ('test', u, s, a, 'ORD-2', 100, 10, 7, 20, 999, NOW() + INTERVAL '30 minutes', 'Home', '\x01', '\x01', '\x01', '\x01', '\x01');
        RAISE EXCEPTION 'FAIL: a total_amount that is not price - discount + tax + shipping was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 4: total_amount follows the totals';
END $$;

-- test 5: the order keeps its own copy of the shipping address and the time until which it holds the stock
DO $$
DECLARE
    u UUID := '11111111-1111-4111-8111-111111111111'; s UUID := '22222222-2222-4222-8222-222222222222';
    a UUID := 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
BEGIN
    BEGIN
        INSERT INTO sales.t_order (created_by, user_id, shop_id, address_id, code, total_price, total_discount, total_tax, total_shipping, total_amount,
            ship_title, ship_address, ship_city, ship_state, ship_postal_code, ship_country)
        VALUES ('test', u, s, a, 'ORD-3', 100, 0, 0, 0, 100, 'Home', '\x01', '\x01', '\x01', '\x01', '\x01');
        RAISE EXCEPTION 'FAIL: an order without expires_at was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO sales.t_order (created_by, user_id, shop_id, address_id, code, total_price, total_discount, total_tax, total_shipping, total_amount,
            expires_at, ship_title, ship_address, ship_city, ship_state, ship_postal_code, ship_country)
        VALUES ('test', u, s, a, 'ORD-4', 100, 0, 0, 0, 100, NOW(), 'Home', NULL, '\x01', '\x01', '\x01', '\x01');
        RAISE EXCEPTION 'FAIL: an order without a shipping address copy was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 5: expires_at and the shipping address copy are required';
END $$;

-- test 6: a user address that an order points to cannot be hard deleted (the order must survive)
DO $$
DECLARE d "char";
BEGIN
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'sales.t_order'::regclass AND contype = 'f' AND confrelid = 'authen.t_user_address'::regclass;
    IF d IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: t_order.address_id must be ON DELETE RESTRICT, found %', d;
    END IF;
    RAISE NOTICE 'PASS test 6: order address is ON DELETE RESTRICT';
END $$;

ROLLBACK;
