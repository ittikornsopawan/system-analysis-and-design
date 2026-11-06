-- Test for multi-level product SKU tables (03-product.schema.up.sql)
-- Run after the up migration. Everything is rolled back at the end.
-- Usage: psql -v ON_ERROR_STOP=1 -f 03-product-sku-levels.test.sql
BEGIN;

-- Fixture: one product with fixed ids so every DO block can reference it
INSERT INTO
    product.m_product_type (id, created_by, name, description)
VALUES
    (
        '00000000-0000-0000-0000-0000000000a1',
        'test',
        'test-type',
        'test type'
    );

INSERT INTO
    product.m_product_category (id, created_by, name, description, slug)
VALUES
    (
        '00000000-0000-0000-0000-0000000000a2',
        'test',
        'test-category',
        'test category',
        'test-category'
    );

INSERT INTO
    product.m_product_brand (id, created_by, name, description)
VALUES
    (
        '00000000-0000-0000-0000-0000000000a3',
        'test',
        'test-brand',
        'test brand'
    );

INSERT INTO
    product.m_product (
        id,
        created_by,
        type_id,
        category_id,
        brand_id,
        name,
        description,
        body,
        slug
    )
VALUES
    (
        '00000000-0000-0000-0000-0000000000a4',
        'test',
        '00000000-0000-0000-0000-0000000000a1',
        '00000000-0000-0000-0000-0000000000a2',
        '00000000-0000-0000-0000-0000000000a3',
        'test-product',
        'test product',
        'body',
        'test-product'
    );

-- 1. m_product_option: unique (product_id, level_no) among non-deleted rows
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Pattern', 1)
    RETURNING id INTO v_option;

    BEGIN
        INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
        VALUES ('test', v_product, 'Other', 1);
        RAISE EXCEPTION 'FAIL: duplicate (product_id, level_no) was accepted';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    UPDATE product.m_product_option SET row_status = 'DELETED' WHERE id = v_option;

    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Other', 1);

    RAISE NOTICE 'PASS: m_product_option unique (product_id, level_no)';
END
$$;

-- 2. m_product_option: unique (product_id, name) among non-deleted rows
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Size', 2)
    RETURNING id INTO v_option;

    BEGIN
        INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
        VALUES ('test', v_product, 'Size', 3);
        RAISE EXCEPTION 'FAIL: duplicate (product_id, name) was accepted';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    UPDATE product.m_product_option SET row_status = 'DELETED' WHERE id = v_option;

    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Size', 3);

    RAISE NOTICE 'PASS: m_product_option unique (product_id, name)';
END
$$;

-- 3. m_product_option_value: unique (option_id, value) among non-deleted rows
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
    v_value UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Color', 4)
    RETURNING id INTO v_option;

    INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
    VALUES ('test', v_option, 'Red', 1)
    RETURNING id INTO v_value;

    BEGIN
        INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
        VALUES ('test', v_option, 'Red', 2);
        RAISE EXCEPTION 'FAIL: duplicate (option_id, value) was accepted';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    UPDATE product.m_product_option_value SET row_status = 'DELETED' WHERE id = v_value;

    INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
    VALUES ('test', v_option, 'Red', 2);

    RAISE NOTICE 'PASS: m_product_option_value unique (option_id, value)';
END
$$;

-- 4. m_product_sku: unique (product_id, combination_key), default SKU has key ''
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_sku UUID;
BEGIN
    INSERT INTO product.m_product_sku (created_by, product_id, name, description)
    VALUES ('test', v_product, 'Default', 'default sku')
    RETURNING id INTO v_sku;

    IF (SELECT combination_key FROM product.m_product_sku WHERE id = v_sku) <> '' THEN
        RAISE EXCEPTION 'FAIL: combination_key default is not an empty string';
    END IF;

    BEGIN
        INSERT INTO product.m_product_sku (created_by, product_id, name, description, combination_key)
        VALUES ('test', v_product, 'Default 2', 'default sku 2', '');
        RAISE EXCEPTION 'FAIL: second default SKU (combination_key = empty) was accepted';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    UPDATE product.m_product_sku SET row_status = 'DELETED' WHERE id = v_sku;

    INSERT INTO product.m_product_sku (created_by, product_id, name, description, combination_key)
    VALUES ('test', v_product, 'Default again', 'default sku again', '');

    RAISE NOTICE 'PASS: m_product_sku unique (product_id, combination_key)';
END
$$;

-- 5. m_product_sku_option_value: unique (sku_id, option_value_id)
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
    v_value UUID;
    v_sku UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Material', 5)
    RETURNING id INTO v_option;

    INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
    VALUES ('test', v_option, 'Cotton', 1)
    RETURNING id INTO v_value;

    INSERT INTO product.m_product_sku (created_by, product_id, name, description, combination_key)
    VALUES ('test', v_product, 'Cotton', 'cotton sku', v_value::TEXT)
    RETURNING id INTO v_sku;

    INSERT INTO product.m_product_sku_option_value (created_by, sku_id, option_value_id)
    VALUES ('test', v_sku, v_value);

    BEGIN
        INSERT INTO product.m_product_sku_option_value (created_by, sku_id, option_value_id)
        VALUES ('test', v_sku, v_value);
        RAISE EXCEPTION 'FAIL: duplicate (sku_id, option_value_id) was accepted';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;

    RAISE NOTICE 'PASS: m_product_sku_option_value unique (sku_id, option_value_id)';
END
$$;

-- 6. m_product_image.option_value_id: nullable, must reference an existing value
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
    v_value UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Finish', 6)
    RETURNING id INTO v_option;

    INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
    VALUES ('test', v_option, 'Matte', 1)
    RETURNING id INTO v_value;

    INSERT INTO product.m_product_image (created_by, product_id, image_path, option_value_id)
    VALUES ('test', v_product, '/img/general.png', NULL);

    INSERT INTO product.m_product_image (created_by, product_id, image_path, option_value_id)
    VALUES ('test', v_product, '/img/matte.png', v_value);

    BEGIN
        INSERT INTO product.m_product_image (created_by, product_id, image_path, option_value_id)
        VALUES ('test', v_product, '/img/missing.png', GEN_RANDOM_UUID ());
        RAISE EXCEPTION 'FAIL: image with a non-existent option_value_id was accepted';
    EXCEPTION WHEN foreign_key_violation THEN
        NULL;
    END;

    RAISE NOTICE 'PASS: m_product_image.option_value_id nullable and FK enforced';
END
$$;

-- 7. Hard delete of an option value cascades to its SKU links and images
DO $$
DECLARE
    v_product UUID := '00000000-0000-0000-0000-0000000000a4';
    v_option UUID;
    v_value UUID;
    v_sku UUID;
BEGIN
    INSERT INTO product.m_product_option (created_by, product_id, name, level_no)
    VALUES ('test', v_product, 'Edition', 7)
    RETURNING id INTO v_option;

    INSERT INTO product.m_product_option_value (created_by, option_id, value, sort_order)
    VALUES ('test', v_option, 'Limited', 1)
    RETURNING id INTO v_value;

    INSERT INTO product.m_product_sku (created_by, product_id, name, description, combination_key)
    VALUES ('test', v_product, 'Limited', 'limited sku', v_value::TEXT)
    RETURNING id INTO v_sku;

    INSERT INTO product.m_product_sku_option_value (created_by, sku_id, option_value_id)
    VALUES ('test', v_sku, v_value);

    INSERT INTO product.m_product_image (created_by, product_id, image_path, option_value_id)
    VALUES ('test', v_product, '/img/limited.png', v_value);

    DELETE FROM product.m_product_option_value WHERE id = v_value;

    IF EXISTS (SELECT 1 FROM product.m_product_sku_option_value WHERE option_value_id = v_value) THEN
        RAISE EXCEPTION 'FAIL: sku option value link survived the hard delete';
    END IF;

    IF EXISTS (SELECT 1 FROM product.m_product_image WHERE option_value_id = v_value) THEN
        RAISE EXCEPTION 'FAIL: image of the deleted value survived the hard delete';
    END IF;

    RAISE NOTICE 'PASS: hard delete of option value cascades to sku links and images';
END
$$;

ROLLBACK;
