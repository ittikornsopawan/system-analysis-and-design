-- Tests for shop.t_shop_product (the products a shop sells): no quantity column (stock lives on the lots) and
-- one row per shop and product among the rows that are not DELETED.
-- Run after 04-shop.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the constraints of the table, not its parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: the stock is only on the lots, the shop product has no quantity
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'shop' AND table_name = 't_shop_product' AND column_name = 'quantity') THEN
        RAISE EXCEPTION 'FAIL: shop.t_shop_product still has a quantity column';
    END IF;
    IF (SELECT COUNT(*) FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE n.nspname = 'shop' AND t.relname = 't_shop_product' AND c.contype = 'c' AND pg_get_constraintdef(c.oid) ILIKE '%quantity%') <> 0 THEN
        RAISE EXCEPTION 'FAIL: a check on the quantity of the shop product is left';
    END IF;
    RAISE NOTICE 'PASS test 1: shop.t_shop_product has no quantity';
END $$;

-- test 2: a product is listed once by a shop among the rows that are not DELETED
DO $$
DECLARE
    a UUID := 'a1a1a1a1-a1a1-4a1a-8a1a-a1a1a1a1a1a1';
    b UUID := 'b2b2b2b2-b2b2-4b2b-8b2b-b2b2b2b2b2b2';
    p UUID := 'c3c3c3c3-c3c3-4c3c-8c3c-c3c3c3c3c3c3';
    q UUID := 'd4d4d4d4-d4d4-4d4d-8d4d-d4d4d4d4d4d4';
    s TEXT;
BEGIN
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, p);
    BEGIN
        INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, p);
        RAISE EXCEPTION 'FAIL: the same product was listed twice by a shop';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- the same product in another shop and another product in the same shop are different rows
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', b, p);
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, q);
    -- INACTIVE, LOCKED and ARCHIVED rows still hold the place
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        UPDATE shop.t_shop_product SET row_status = s WHERE shop_id = a AND product_id = q AND row_status <> 'DELETED';
        BEGIN
            INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, q);
            RAISE EXCEPTION 'FAIL: a product with an % shop product was listed again', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 2: one shop product per shop and product among non deleted rows';
END $$;

-- test 3: after a soft delete the shop can list the same product again, also more than once
DO $$
DECLARE
    a UUID := 'a1a1a1a1-a1a1-4a1a-8a1a-a1a1a1a1a1a1';
    p UUID := 'e5e5e5e5-e5e5-4e5e-8e5e-e5e5e5e5e5e5';
    live INT;
BEGIN
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, p);
    UPDATE shop.t_shop_product SET row_status = 'DELETED' WHERE shop_id = a AND product_id = p;
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, p);
    UPDATE shop.t_shop_product SET row_status = 'DELETED' WHERE shop_id = a AND product_id = p AND row_status = 'ACTIVE';
    INSERT INTO shop.t_shop_product (created_by, shop_id, product_id) VALUES ('test', a, p);
    SELECT COUNT(*) INTO live FROM shop.t_shop_product WHERE shop_id = a AND product_id = p AND row_status <> 'DELETED';
    IF live <> 1 THEN
        RAISE EXCEPTION 'FAIL: expected one live shop product, found %', live;
    END IF;
    IF (SELECT row_status FROM shop.t_shop_product WHERE shop_id = a AND product_id = p AND row_status <> 'DELETED') <> 'ACTIVE' THEN
        RAISE EXCEPTION 'FAIL: a new shop product must default to ACTIVE';
    END IF;
    RAISE NOTICE 'PASS test 3: a deleted shop product can be listed again';
END $$;

ROLLBACK;
