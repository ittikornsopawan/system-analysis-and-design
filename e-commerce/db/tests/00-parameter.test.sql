-- Tests for public.t_parameter:
--   * key is unique
--   * parent_id references t_parameter(id) ON DELETE RESTRICT
--   * value is required
-- Run after 00-common.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a key cannot be used twice
DO $$
BEGIN
    INSERT INTO public.t_parameter (created_by, key, value) VALUES ('test', 'currency', '{"en": "Currency"}');
    BEGIN
        INSERT INTO public.t_parameter (created_by, key, value) VALUES ('test', 'currency', '{"en": "Currency"}');
        RAISE EXCEPTION 'FAIL: a duplicate parameter key was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 1: key is unique';
END $$;

-- test 2: a parent with children cannot be deleted, and parent_id must point to a real parameter
DO $$
DECLARE p UUID;
BEGIN
    INSERT INTO public.t_parameter (created_by, key, value) VALUES ('test', 'country', '{"en": "Country"}') RETURNING id INTO p;
    INSERT INTO public.t_parameter (created_by, parent_id, key, value) VALUES ('test', p, 'country.th', '{"en": "Thailand", "th": "ไทย"}');
    BEGIN
        DELETE FROM public.t_parameter WHERE id = p;
        RAISE EXCEPTION 'FAIL: a parent parameter with children was deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO public.t_parameter (created_by, parent_id, key, value) VALUES ('test', gen_random_uuid(), 'orphan', '{}');
        RAISE EXCEPTION 'FAIL: a parameter with an unknown parent was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: parent_id is ON DELETE RESTRICT and must exist';
END $$;

-- test 3: value is required
DO $$
BEGIN
    BEGIN
        INSERT INTO public.t_parameter (created_by, key) VALUES ('test', 'no-value');
        RAISE EXCEPTION 'FAIL: a parameter without a value was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: value is required';
END $$;

ROLLBACK;
