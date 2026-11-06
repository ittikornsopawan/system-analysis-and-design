-- Tests for product.m_product_type and product.m_product_brand (WP6 B1, B2):
--   * name is unique among rows that are not DELETED (partial unique index, a DELETED name can be reused)
--   * m_product.type_id and m_product.brand_id are ON DELETE RESTRICT
-- Run after 03-product.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a name used by a non deleted type or brand cannot be used again
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['m_product_type', 'm_product_brand'] LOOP
        EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Same name'', ''first'')', t);
        BEGIN
            EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Same name'', ''second'')', t);
            RAISE EXCEPTION 'FAIL: % accepted a duplicate name', t;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 1: name unique among non deleted product types and brands';
END $$;

-- test 2: INACTIVE, LOCKED and ARCHIVED rows still hold their name
DO $$
DECLARE t TEXT; s TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['m_product_type', 'm_product_brand'] LOOP
        FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
            EXECUTE format('INSERT INTO product.%I (created_by, name, description, row_status) VALUES (''test'', %L, ''held'', %L)', t, 'Held ' || s, s);
            BEGIN
                EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', %L, ''again'')', t, 'Held ' || s);
                RAISE EXCEPTION 'FAIL: the name of an % row of % was reused', s, t;
            EXCEPTION WHEN unique_violation THEN NULL;
            END;
        END LOOP;
    END LOOP;
    RAISE NOTICE 'PASS test 2: INACTIVE, LOCKED and ARCHIVED rows keep their name';
END $$;

-- test 3: the name of a DELETED row can be used again, also more than once
DO $$
DECLARE t TEXT; live INT;
BEGIN
    FOREACH t IN ARRAY ARRAY['m_product_type', 'm_product_brand'] LOOP
        EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Reusable'', ''v1'')', t);
        EXECUTE format('UPDATE product.%I SET row_status = ''DELETED'' WHERE name = ''Reusable''', t);
        EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Reusable'', ''v2'')', t);
        EXECUTE format('UPDATE product.%I SET row_status = ''DELETED'' WHERE name = ''Reusable'' AND row_status = ''ACTIVE''', t);
        EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Reusable'', ''v3'')', t);
        EXECUTE format('SELECT COUNT(*) FROM product.%I WHERE name = ''Reusable'' AND row_status <> ''DELETED''', t) INTO live;
        IF live <> 1 THEN
            RAISE EXCEPTION 'FAIL: expected one live Reusable row in %, found %', t, live;
        END IF;
        BEGIN
            EXECUTE format('INSERT INTO product.%I (created_by, name, description) VALUES (''test'', ''Reusable'', ''v4'')', t);
            RAISE EXCEPTION 'FAIL: a second live Reusable row was accepted in %', t;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 3: the name of a DELETED product type or brand can be reused';
END $$;

-- test 4: a type or brand used by a product cannot be deleted for real (RESTRICT), a soft delete is still possible
DO $$
DECLARE ty UUID; br UUID; cat UUID;
BEGIN
    IF (SELECT COUNT(*) FROM pg_constraint c
        WHERE c.conrelid = 'product.m_product'::regclass AND c.contype = 'f' AND c.confdeltype = 'r'
          AND c.confrelid IN ('product.m_product_type'::regclass, 'product.m_product_brand'::regclass)) <> 2 THEN
        RAISE EXCEPTION 'FAIL: m_product.type_id and m_product.brand_id must both be ON DELETE RESTRICT';
    END IF;
    INSERT INTO product.m_product_type (created_by, name, description) VALUES ('test', 'Restrict type', 'used') RETURNING id INTO ty;
    INSERT INTO product.m_product_brand (created_by, name, description) VALUES ('test', 'Restrict brand', 'used') RETURNING id INTO br;
    INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Restrict category', 'c', 'restrict-category') RETURNING id INTO cat;
    INSERT INTO product.m_product (created_by, type_id, category_id, brand_id, name, description, body, slug)
    VALUES ('test', ty, cat, br, 'Restrict product', 'p', 'body', 'restrict-product');
    BEGIN
        DELETE FROM product.m_product_type WHERE id = ty;
        RAISE EXCEPTION 'FAIL: a product type used by a product was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    BEGIN
        DELETE FROM product.m_product_brand WHERE id = br;
        RAISE EXCEPTION 'FAIL: a product brand used by a product was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    IF NOT EXISTS (SELECT 1 FROM product.m_product WHERE name = 'Restrict product') THEN
        RAISE EXCEPTION 'FAIL: the product disappeared';
    END IF;
    UPDATE product.m_product_type SET row_status = 'DELETED' WHERE id = ty;
    UPDATE product.m_product_brand SET row_status = 'DELETED' WHERE id = br;
    RAISE NOTICE 'PASS test 4: m_product.type_id and brand_id restrict the delete of their type and brand';
END $$;

ROLLBACK;
