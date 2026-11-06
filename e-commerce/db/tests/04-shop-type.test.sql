-- Tests for shop.m_shop_type (name is unique among rows that are not DELETED).
-- Run after 04-shop.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a name used by a non deleted type cannot be used again
DO $$
BEGIN
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Fashion', 'Clothes and accessories');
    BEGIN
        INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Fashion', 'Another description');
        RAISE EXCEPTION 'FAIL: a duplicate name was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 1: name unique among non deleted shop types';
END $$;

-- test 2: INACTIVE, LOCKED and ARCHIVED types still hold their name
DO $$
DECLARE s TEXT;
BEGIN
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO shop.m_shop_type (created_by, name, description, row_status) VALUES ('test', 'Held ' || s, 'held', s);
        BEGIN
            INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Held ' || s, 'again');
            RAISE EXCEPTION 'FAIL: the name of an % type was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 2: INACTIVE, LOCKED and ARCHIVED types keep their name';
END $$;

-- test 3: the name of a DELETED type can be used again, also more than once
DO $$
DECLARE live INT;
BEGIN
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Books', 'Books and magazines');
    UPDATE shop.m_shop_type SET row_status = 'DELETED' WHERE name = 'Books';
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Books', 'Books and magazines');
    UPDATE shop.m_shop_type SET row_status = 'DELETED' WHERE name = 'Books' AND row_status = 'ACTIVE';
    INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Books', 'Books and magazines');
    SELECT COUNT(*) INTO live FROM shop.m_shop_type WHERE name = 'Books' AND row_status <> 'DELETED';
    IF live <> 1 THEN
        RAISE EXCEPTION 'FAIL: expected one live Books type, found %', live;
    END IF;
    BEGIN
        INSERT INTO shop.m_shop_type (created_by, name, description) VALUES ('test', 'Books', 'third live copy');
        RAISE EXCEPTION 'FAIL: a second live Books type was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: the name of a DELETED shop type can be reused';
END $$;

ROLLBACK;
