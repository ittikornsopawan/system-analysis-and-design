-- Tests for shop.t_shop_product_sku_lot (lots of a shop product SKU) and sales.t_order_item.lot_id.
-- Run after 04-shop.schema.up.sql and 06-sales.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the lot constraints, not the parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: only one ACTIVE lot can be on sale per shop product SKU
DO $$
DECLARE s UUID := '11111111-1111-4111-8111-111111111111';
BEGIN
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity, is_on_sale)
    VALUES ('test', s, 'L1', 10, 20, 5, TRUE), ('test', s, 'L2', 11, 21, 5, FALSE);
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity, is_on_sale)
        VALUES ('test', s, 'L3', 12, 22, 5, TRUE);
        RAISE EXCEPTION 'FAIL: a second lot on sale was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- a lot that is not ACTIVE may keep is_on_sale without blocking the open lot
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity, is_on_sale, row_status)
    VALUES ('test', s, 'L4', 12, 22, 5, TRUE, 'INACTIVE');
    -- switching: close L1 then open L2
    UPDATE shop.t_shop_product_sku_lot SET is_on_sale = FALSE WHERE shop_product_sku_id = s AND lot_no = 'L1';
    UPDATE shop.t_shop_product_sku_lot SET is_on_sale = TRUE WHERE shop_product_sku_id = s AND lot_no = 'L2';
    RAISE NOTICE 'PASS test 1: one lot on sale per shop product SKU';
END $$;

-- test 2: lot_no is unique per shop product SKU unless the old row is DELETED
DO $$
DECLARE s UUID := '22222222-2222-4222-8222-222222222222';
BEGIN
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price)
    VALUES ('test', s, 'A', 1, 2);
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price)
        VALUES ('test', s, 'A', 1, 2);
        RAISE EXCEPTION 'FAIL: duplicate lot_no was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE shop.t_shop_product_sku_lot SET row_status = 'DELETED' WHERE shop_product_sku_id = s AND lot_no = 'A';
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price)
    VALUES ('test', s, 'A', 1, 2);
    -- same lot_no on another shop product SKU is fine
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price)
    VALUES ('test', '33333333-3333-4333-8333-333333333333', 'A', 1, 2);
    RAISE NOTICE 'PASS test 2: lot_no unique among non deleted rows per shop product SKU';
END $$;

-- test 3: prices and quantity cannot be negative
DO $$
DECLARE s UUID := '44444444-4444-4444-8444-444444444444';
BEGIN
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price) VALUES ('test', s, 'N1', -1, 2);
        RAISE EXCEPTION 'FAIL: negative cost_price accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price) VALUES ('test', s, 'N2', 1, -2);
        RAISE EXCEPTION 'FAIL: negative selling_price accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity) VALUES ('test', s, 'N3', 1, 2, -1);
        RAISE EXCEPTION 'FAIL: negative quantity accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    -- defaults
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price) VALUES ('test', s, 'D1', 1, 2);
    IF NOT EXISTS (SELECT 1 FROM shop.t_shop_product_sku_lot WHERE shop_product_sku_id = s AND lot_no = 'D1' AND quantity = 0 AND is_on_sale = FALSE AND row_status = 'ACTIVE') THEN
        RAISE EXCEPTION 'FAIL: defaults are not quantity 0, is_on_sale FALSE, row_status ACTIVE';
    END IF;
    RAISE NOTICE 'PASS test 3: non negative checks and defaults';
END $$;

-- test 4: the price columns moved out of t_shop_product_sku
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'shop' AND table_name = 't_shop_product_sku'
               AND column_name IN ('cost_price', 'selling_price', 'gross_margin', 'share_margin', 'platform_margin', 'quantity')) THEN
        RAISE EXCEPTION 'FAIL: price or stock columns are still on shop.t_shop_product_sku';
    END IF;
    RAISE NOTICE 'PASS test 4: price and stock live on the lot only';
END $$;

-- test 5: sales.t_order_item.lot_id is a required FK to the lot that RESTRICTs deletion
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'sales' AND table_name = 't_order_item'
                   AND column_name = 'lot_id' AND is_nullable = 'NO') THEN
        RAISE EXCEPTION 'FAIL: sales.t_order_item.lot_id is missing or nullable';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conrelid = 'sales.t_order_item'::regclass AND c.contype = 'f'
                   AND c.confrelid = 'shop.t_shop_product_sku_lot'::regclass AND c.confdeltype = 'r') THEN
        RAISE EXCEPTION 'FAIL: lot_id does not reference the lot with ON DELETE RESTRICT';
    END IF;
    RAISE NOTICE 'PASS test 5: order item records the lot it was sold from';
END $$;

-- test 6: a lot cannot be sold below its cost (the profit of an order item must not be negative)
DO $$
DECLARE k UUID := '66666666-6666-4666-8666-666666666666';
BEGIN
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity)
    VALUES ('test', k, 'AT-COST', 100, 100, 1);
    INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity)
    VALUES ('test', k, 'ABOVE-COST', 100, 150, 1);
    BEGIN
        INSERT INTO shop.t_shop_product_sku_lot (created_by, shop_product_sku_id, lot_no, cost_price, selling_price, quantity)
        VALUES ('test', k, 'BELOW-COST', 100, 99.99, 1);
        RAISE EXCEPTION 'FAIL: a lot with a selling price below its cost price was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        UPDATE shop.t_shop_product_sku_lot SET selling_price = 50 WHERE lot_no = 'ABOVE-COST';
        RAISE EXCEPTION 'FAIL: an update to a selling price below the cost price was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 6: selling price is not below cost price';
END $$;

ROLLBACK;
