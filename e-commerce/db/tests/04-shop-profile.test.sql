-- Tests for shop.m_shop (unique name, margin rates) and shop.m_shop_image (one LOGO and one WALLPAPER per shop).
-- Run after 04-shop.schema.up.sql. Everything is rolled back at the end.
-- Foreign keys are switched off for the fixture rows (session_replication_role = replica) because
-- these tests only check the constraints of the two tables, not their parent tables.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL session_replication_role = replica;

-- test 1: the name of a shop is unique among shops that are not DELETED
DO $$
DECLARE t UUID := '22222222-2222-4222-8222-222222222222'; s TEXT;
BEGIN
    INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Aof Fashion', 'Clothes');
    BEGIN
        INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Aof Fashion', 'Another');
        RAISE EXCEPTION 'FAIL: a duplicate shop name was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO shop.m_shop (created_by, type_id, name, description, row_status) VALUES ('test', t, 'Held ' || s, 'held', s);
        BEGIN
            INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Held ' || s, 'again');
            RAISE EXCEPTION 'FAIL: the name of an % shop was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    UPDATE shop.m_shop SET row_status = 'DELETED' WHERE name = 'Aof Fashion';
    INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Aof Fashion', 'Reopened under the same name');
    UPDATE shop.m_shop SET row_status = 'DELETED' WHERE name = 'Aof Fashion' AND row_status = 'ACTIVE';
    INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Aof Fashion', 'Third time');
    RAISE NOTICE 'PASS test 1: shop name unique among non deleted shops';
END $$;

-- test 2: margin rates: 0..100 each and platform + shop at most 100
DO $$
DECLARE t UUID := '22222222-2222-4222-8222-222222222222';
BEGIN
    INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Default margin', 'x');
    IF (SELECT platform_margin_rate + shop_margin_rate FROM shop.m_shop WHERE name = 'Default margin') <> 0 THEN
        RAISE EXCEPTION 'FAIL: margin rates must default to 0.00';
    END IF;
    INSERT INTO shop.m_shop (created_by, type_id, name, description, platform_margin_rate, shop_margin_rate) VALUES ('test', t, 'Split 60/40', 'x', 60, 40);
    INSERT INTO shop.m_shop (created_by, type_id, name, description, platform_margin_rate, shop_margin_rate) VALUES ('test', t, 'All platform', 'x', 100, 0);
    BEGIN
        INSERT INTO shop.m_shop (created_by, type_id, name, description, platform_margin_rate, shop_margin_rate) VALUES ('test', t, 'Over 100', 'x', 60, 50);
        RAISE EXCEPTION 'FAIL: platform 60 + shop 50 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        UPDATE shop.m_shop SET shop_margin_rate = 41 WHERE name = 'Split 60/40';
        RAISE EXCEPTION 'FAIL: an update to platform 60 + shop 41 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO shop.m_shop (created_by, type_id, name, description, platform_margin_rate) VALUES ('test', t, 'Above range', 'x', 100.01);
        RAISE EXCEPTION 'FAIL: a rate above 100 was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO shop.m_shop (created_by, type_id, name, description, shop_margin_rate) VALUES ('test', t, 'Below range', 'x', -0.01);
        RAISE EXCEPTION 'FAIL: a negative rate was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: margin rates are 0..100 each and at most 100 together';
END $$;

-- test 3: one LOGO and one WALLPAPER per shop among images that are not DELETED, any number of BANNER images
DO $$
DECLARE a UUID := '33333333-3333-4333-8333-333333333333'; b UUID := '44444444-4444-4444-8444-444444444444'; ty TEXT;
BEGIN
    FOREACH ty IN ARRAY ARRAY['LOGO', 'WALLPAPER'] LOOP
        INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', a, ty, 0, '/shops/a/' || ty || '-1.png');
        BEGIN
            INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', a, ty, 1, '/shops/a/' || ty || '-2.png');
            RAISE EXCEPTION 'FAIL: a second % was accepted', ty;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
        -- another shop has its own
        INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', b, ty, 0, '/shops/b/' || ty || '-1.png');
        -- an INACTIVE image still holds the place
        UPDATE shop.m_shop_image SET row_status = 'INACTIVE' WHERE shop_id = a AND type = ty;
        BEGIN
            INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', a, ty, 1, '/shops/a/' || ty || '-3.png');
            RAISE EXCEPTION 'FAIL: a % was added while an INACTIVE one exists', ty;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
        -- a DELETED image frees the place, also more than once
        UPDATE shop.m_shop_image SET row_status = 'DELETED' WHERE shop_id = a AND type = ty;
        INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', a, ty, 0, '/shops/a/' || ty || '-4.png');
        UPDATE shop.m_shop_image SET row_status = 'DELETED' WHERE shop_id = a AND type = ty AND row_status = 'ACTIVE';
        INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES ('test', a, ty, 0, '/shops/a/' || ty || '-5.png');
    END LOOP;
    -- banners and equal seq values are allowed
    INSERT INTO shop.m_shop_image (created_by, shop_id, type, seq, image_path) VALUES
        ('test', a, 'BANNER', 0, '/shops/a/b1.png'), ('test', a, 'BANNER', 0, '/shops/a/b2.png'), ('test', a, 'BANNER', 1, '/shops/a/b3.png');
    RAISE NOTICE 'PASS test 3: one LOGO and one WALLPAPER per shop, many BANNER images';
END $$;

ROLLBACK;

-- test 4: a shop type that a shop uses cannot be deleted for real (RESTRICT), a soft delete is still possible
BEGIN;
DO $$
DECLARE t UUID;
BEGIN
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Restrict type', 'used by a shop') RETURNING id INTO t;
    INSERT INTO shop.m_shop (created_by, type_id, name, description) VALUES ('test', t, 'Restrict shop', 'x');
    BEGIN
        DELETE FROM shop.m_shop_type WHERE id = t;
        RAISE EXCEPTION 'FAIL: a shop type used by a shop was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    IF NOT EXISTS (SELECT 1 FROM shop.m_shop WHERE name = 'Restrict shop') THEN
        RAISE EXCEPTION 'FAIL: the shop disappeared';
    END IF;
    UPDATE shop.m_shop_type SET row_status = 'DELETED' WHERE id = t;
    -- a shop type without shops can still be removed
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Unused type', 'no shop') RETURNING id INTO t;
    DELETE FROM shop.m_shop_type WHERE id = t;
    RAISE NOTICE 'PASS test 4: shop.m_shop.type_id restricts the delete of its shop type';
END $$;
ROLLBACK;
