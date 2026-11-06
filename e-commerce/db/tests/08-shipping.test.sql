-- Tests for shipping.t_shipping, t_shipping_item and t_shipping_stop (rules decided in
-- docs/superpowers/specs/2026-11-06-shipping-design.md, S6 to S12: tracking number per carrier, status checks,
-- one row per order item in a shipping, hub stops, history is protected). Run after 08-shipping.schema.up.sql.
-- Everything is rolled back at the end. Foreign keys are switched off for the fixture rows
-- (session_replication_role = replica) because these tests only check the constraints of the shipping tables;
-- the ON DELETE rules are checked through pg_constraint.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: a tracking number is unique per carrier among rows that are not DELETED, and several PENDING shippings may have none
DO $$
DECLARE
    o UUID := '11111111-1111-4111-8111-111111111111';
BEGIN
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
    VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0001', NOW());
    BEGIN
        INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
        VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0001', NOW());
        RAISE EXCEPTION 'FAIL: the same tracking number of the same carrier was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- the same number at another carrier is a different parcel
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
    VALUES ('test', o, 'STANDARD', 'SHIPPED', 'FLASH', 'TH0001', NOW());
    -- INACTIVE still holds the number
    UPDATE shipping.t_shipping SET row_status = 'INACTIVE' WHERE carrier_name = 'KERRY' AND tracking_number = 'TH0001';
    BEGIN
        INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
        VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0001', NOW());
        RAISE EXCEPTION 'FAIL: the number of an INACTIVE shipping was reused';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- a DELETED row frees the number, also more than once
    UPDATE shipping.t_shipping SET row_status = 'DELETED' WHERE carrier_name = 'KERRY' AND tracking_number = 'TH0001';
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
    VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0001', NOW());
    UPDATE shipping.t_shipping SET row_status = 'DELETED' WHERE carrier_name = 'KERRY' AND tracking_number = 'TH0001';
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
    VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0001', NOW());
    -- PENDING shippings carry no number yet, any count is fine
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method) VALUES ('test', o, 'EXPRESS');
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method) VALUES ('test', o, 'EXPRESS');
    RAISE NOTICE 'PASS test 1: tracking number unique per carrier among non deleted rows';
END $$;

-- test 2: SHIPPED, DELIVERED and RETURNED need the carrier, the tracking number and shipped_at; PENDING and CANCELLED do not
DO $$
DECLARE
    o UUID := '22222222-2222-4222-8222-222222222222';
    s TEXT;
BEGIN
    FOREACH s IN ARRAY ARRAY['SHIPPED', 'RETURNED'] LOOP
        BEGIN
            INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, tracking_number, shipped_at)
            VALUES ('test', o, 'STANDARD', s, 'TH0100', NOW());
            RAISE EXCEPTION 'FAIL: % without a carrier was accepted', s;
        EXCEPTION WHEN check_violation THEN NULL;
        END;
        BEGIN
            INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, shipped_at)
            VALUES ('test', o, 'STANDARD', s, 'KERRY', NOW());
            RAISE EXCEPTION 'FAIL: % without a tracking number was accepted', s;
        EXCEPTION WHEN check_violation THEN NULL;
        END;
        BEGIN
            INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number)
            VALUES ('test', o, 'STANDARD', s, 'KERRY', 'TH0101');
            RAISE EXCEPTION 'FAIL: % without shipped_at was accepted', s;
        EXCEPTION WHEN check_violation THEN NULL;
        END;
    END LOOP;
    BEGIN
        INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, shipped_at, delivered_at)
        VALUES ('test', o, 'STANDARD', 'DELIVERED', NOW(), NOW());
        RAISE EXCEPTION 'FAIL: DELIVERED without a carrier and a tracking number was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status) VALUES ('test', o, 'STANDARD', 'PENDING');
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status) VALUES ('test', o, 'STANDARD', 'CANCELLED');
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
    VALUES ('test', o, 'STANDARD', 'RETURNED', 'KERRY', 'TH0102', NOW());
    RAISE NOTICE 'PASS test 2: carrier, tracking number and shipped_at are required once the parcel is shipped';
END $$;

-- test 3: delivered_at is set exactly when the status is DELIVERED
DO $$
DECLARE
    o UUID := '33333333-3333-4333-8333-333333333333';
BEGIN
    BEGIN
        INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at)
        VALUES ('test', o, 'STANDARD', 'DELIVERED', 'KERRY', 'TH0200', NOW());
        RAISE EXCEPTION 'FAIL: DELIVERED without delivered_at was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at, delivered_at)
        VALUES ('test', o, 'STANDARD', 'SHIPPED', 'KERRY', 'TH0201', NOW(), NOW());
        RAISE EXCEPTION 'FAIL: delivered_at on a SHIPPED shipping was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    INSERT INTO shipping.t_shipping (created_by, order_id, shipping_method, status, carrier_name, tracking_number, shipped_at, delivered_at)
    VALUES ('test', o, 'STANDARD', 'DELIVERED', 'KERRY', 'TH0202', NOW(), NOW());
    RAISE NOTICE 'PASS test 3: delivered_at only on DELIVERED';
END $$;

-- test 4: one row per order item in a shipping among rows that are not DELETED
DO $$
DECLARE
    sh UUID := '44444444-4444-4444-8444-444444444444'; oi UUID := '55555555-5555-4555-8555-555555555555';
BEGIN
    INSERT INTO shipping.t_shipping_item (created_by, shipping_id, order_item_id, quantity) VALUES ('test', sh, oi, 1);
    BEGIN
        INSERT INTO shipping.t_shipping_item (created_by, shipping_id, order_item_id, quantity) VALUES ('test', sh, oi, 1);
        RAISE EXCEPTION 'FAIL: the same order item twice in one shipping was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- the same order item in another shipping is a split shipment
    INSERT INTO shipping.t_shipping_item (created_by, shipping_id, order_item_id, quantity)
    VALUES ('test', '66666666-6666-4666-8666-666666666666', oi, 1);
    UPDATE shipping.t_shipping_item SET row_status = 'DELETED' WHERE shipping_id = sh AND order_item_id = oi;
    INSERT INTO shipping.t_shipping_item (created_by, shipping_id, order_item_id, quantity) VALUES ('test', sh, oi, 1);
    RAISE NOTICE 'PASS test 4: one row per order item in a shipping among non deleted rows';
END $$;

-- test 5: a stop number is unique in a shipping among non deleted rows, TRANSIT is a stop type, arrived_at is optional
DO $$
DECLARE
    sh UUID := '77777777-7777-4777-8777-777777777777';
BEGIN
    INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name)
    VALUES ('test', sh, 1, 'PICKUP', 'Shop warehouse');
    BEGIN
        INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name)
        VALUES ('test', sh, 1, 'TRANSIT', 'Bangkok hub');
        RAISE EXCEPTION 'FAIL: a duplicate stop number was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name, estimated_arrival, arrived_at)
    VALUES ('test', sh, 2, 'TRANSIT', 'Bangkok hub', NOW(), NOW());
    INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name)
    VALUES ('test', sh, 3, 'DROPOFF', 'Customer address');
    BEGIN
        INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name)
        VALUES ('test', sh, 4, 'LAYOVER', 'Somewhere');
        RAISE EXCEPTION 'FAIL: an unknown stop type was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    UPDATE shipping.t_shipping_stop SET row_status = 'DELETED' WHERE shipping_id = sh AND stop_number = 2;
    INSERT INTO shipping.t_shipping_stop (created_by, shipping_id, stop_number, stop_type, location_name)
    VALUES ('test', sh, 2, 'TRANSIT', 'Chiang Mai hub');
    RAISE NOTICE 'PASS test 5: stop number unique among non deleted rows, TRANSIT and arrived_at';
END $$;

-- test 6: history is protected: the order and the order item of a shipping cannot be deleted (RESTRICT), the children of a shipping follow it (CASCADE)
DO $$
DECLARE d "char";
BEGIN
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'shipping.t_shipping'::regclass AND contype = 'f' AND confrelid = 'sales.t_order'::regclass;
    IF d IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: t_shipping.order_id must be ON DELETE RESTRICT, found %', d;
    END IF;
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'shipping.t_shipping_item'::regclass AND contype = 'f' AND confrelid = 'sales.t_order_item'::regclass;
    IF d IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: t_shipping_item.order_item_id must be ON DELETE RESTRICT, found %', d;
    END IF;
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'shipping.t_shipping_item'::regclass AND contype = 'f' AND confrelid = 'shipping.t_shipping'::regclass;
    IF d IS DISTINCT FROM 'c' THEN
        RAISE EXCEPTION 'FAIL: t_shipping_item.shipping_id must be ON DELETE CASCADE, found %', d;
    END IF;
    SELECT confdeltype INTO d FROM pg_constraint
    WHERE conrelid = 'shipping.t_shipping_stop'::regclass AND contype = 'f' AND confrelid = 'shipping.t_shipping'::regclass;
    IF d IS DISTINCT FROM 'c' THEN
        RAISE EXCEPTION 'FAIL: t_shipping_stop.shipping_id must be ON DELETE CASCADE, found %', d;
    END IF;
    RAISE NOTICE 'PASS test 6: order and order item are ON DELETE RESTRICT, shipping children are CASCADE';
END $$;

ROLLBACK;
