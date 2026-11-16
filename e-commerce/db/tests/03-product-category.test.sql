-- Tests for product.m_product_category and product.m_product_category_attribute (owner approval of 2026-11-16):
--   * name is unique among rows that are not DELETED (partial unique index, a DELETED name can be reused)
--   * every foreign key into the two tables is ON DELETE RESTRICT
-- Run after 03-product.schema.up.sql and 09-campaign.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a name used by a row that is not DELETED cannot be used again, INACTIVE, LOCKED and ARCHIVED rows keep their name
DO $$
DECLARE cat UUID; s TEXT;
BEGIN
    INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Same category', 'first', 'same-category') RETURNING id INTO cat;
    BEGIN
        INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Same category', 'second', 'same-category-2');
        RAISE EXCEPTION 'FAIL: m_product_category accepted a duplicate name';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO product.m_product_category_attribute (created_by, category_id, name, description) VALUES ('test', cat, 'Same attribute', 'first');
    BEGIN
        INSERT INTO product.m_product_category_attribute (created_by, category_id, name, description) VALUES ('test', cat, 'Same attribute', 'second');
        RAISE EXCEPTION 'FAIL: m_product_category_attribute accepted a duplicate name';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO product.m_product_category (created_by, name, description, slug, row_status) VALUES ('test', 'Held ' || s, 'held', 'held-' || lower(s), s);
        BEGIN
            INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Held ' || s, 'again', 'held-again');
            RAISE EXCEPTION 'FAIL: the name of an % category was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 1: name unique among category and attribute rows that are not DELETED';
END $$;

-- test 2: the name of a DELETED row can be used again, but only one live row keeps it
DO $$
DECLARE cat UUID;
BEGIN
    INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Reusable category', 'v1', 'reusable-1') RETURNING id INTO cat;
    UPDATE product.m_product_category SET row_status = 'DELETED' WHERE id = cat;
    INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Reusable category', 'v2', 'reusable-2') RETURNING id INTO cat;
    INSERT INTO product.m_product_category_attribute (created_by, category_id, name, description, row_status) VALUES ('test', cat, 'Reusable attribute', 'v1', 'DELETED');
    INSERT INTO product.m_product_category_attribute (created_by, category_id, name, description) VALUES ('test', cat, 'Reusable attribute', 'v2');
    BEGIN
        INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Reusable category', 'v3', 'reusable-3');
        RAISE EXCEPTION 'FAIL: a second live Reusable category was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO product.m_product_category_attribute (created_by, category_id, name, description) VALUES ('test', cat, 'Reusable attribute', 'v3');
        RAISE EXCEPTION 'FAIL: a second live Reusable attribute was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: the name of a DELETED category or attribute can be reused';
END $$;

-- test 3: every foreign key into the two tables is ON DELETE RESTRICT, and a used category cannot be hard deleted
DO $$
DECLARE bad TEXT; parent UUID; child UUID;
BEGIN
    SELECT string_agg(c.conrelid::regclass || '.' || a.attname, ', ') INTO bad
    FROM pg_constraint c
    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
    WHERE c.contype = 'f' AND c.confdeltype <> 'r'
      AND c.confrelid IN ('product.m_product_category'::regclass, 'product.m_product_category_attribute'::regclass);
    IF bad IS NOT NULL THEN
        RAISE EXCEPTION 'FAIL: these foreign keys must be ON DELETE RESTRICT: %', bad;
    END IF;
    IF (SELECT COUNT(*) FROM pg_constraint c WHERE c.contype = 'f'
        AND c.confrelid IN ('product.m_product_category'::regclass, 'product.m_product_category_attribute'::regclass)) <> 5 THEN
        RAISE EXCEPTION 'FAIL: expected 5 foreign keys into the category and attribute tables';
    END IF;
    INSERT INTO product.m_product_category (created_by, name, description, slug) VALUES ('test', 'Restrict parent', 'p', 'restrict-parent') RETURNING id INTO parent;
    INSERT INTO product.m_product_category (created_by, parent_id, name, description, slug) VALUES ('test', parent, 'Restrict child', 'c', 'restrict-child') RETURNING id INTO child;
    BEGIN
        DELETE FROM product.m_product_category WHERE id = parent;
        RAISE EXCEPTION 'FAIL: a category with a child category was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    UPDATE product.m_product_category SET row_status = 'DELETED' WHERE id = parent;
    RAISE NOTICE 'PASS test 3: the 5 foreign keys into category and attribute are ON DELETE RESTRICT';
END $$;

ROLLBACK;
