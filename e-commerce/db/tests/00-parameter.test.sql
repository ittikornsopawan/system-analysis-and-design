-- Tests for public.m_parameter:
--   * key is unique among rows that are not DELETED (a DELETED key can be reused)
--   * row_status takes the 5 standard values
--   * parent_id is indexed
--   * parent_id references m_parameter(id) ON DELETE RESTRICT
--   * value is required
-- Run after 00-common.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a key cannot be used twice
DO $$
BEGIN
    INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'currency', '{"en": "Currency"}');
    BEGIN
        INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'currency', '{"en": "Currency"}');
        RAISE EXCEPTION 'FAIL: a duplicate parameter key was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    UPDATE public.m_parameter SET row_status = 'DELETED' WHERE key = 'currency';
    INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'currency', '{"en": "Currency"}');
    RAISE NOTICE 'PASS test 1: key is unique among rows that are not DELETED';
END $$;

-- test 2: a parent with children cannot be deleted, and parent_id must point to a real parameter
DO $$
DECLARE p UUID;
BEGIN
    INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'country', '{"en": "Country"}') RETURNING id INTO p;
    INSERT INTO public.m_parameter (created_by, parent_id, key, value) VALUES ('test', p, 'country.th', '{"en": "Thailand", "th": "ไทย"}');
    BEGIN
        DELETE FROM public.m_parameter WHERE id = p;
        RAISE EXCEPTION 'FAIL: a parent parameter with children was deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO public.m_parameter (created_by, parent_id, key, value) VALUES ('test', gen_random_uuid(), 'orphan', '{}');
        RAISE EXCEPTION 'FAIL: a parameter with an unknown parent was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 2: parent_id is ON DELETE RESTRICT and must exist';
END $$;

-- test 3: value is required
DO $$
BEGIN
    BEGIN
        INSERT INTO public.m_parameter (created_by, key) VALUES ('test', 'no-value');
        RAISE EXCEPTION 'FAIL: a parameter without a value was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: value is required';
END $$;

-- test 4: EXPIRED is not a row status; expired_at says it
DO $$
BEGIN
    BEGIN
        INSERT INTO public.m_parameter (created_by, key, value, row_status) VALUES ('test', 'old', '{}', 'EXPIRED');
        RAISE EXCEPTION 'FAIL: row_status EXPIRED was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 4: row_status takes the 5 standard values';
END $$;

-- test 5: parent_id has an index, for the public list of children and the children check before a delete
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'm_parameter' AND indexname = 'ix_m_parameter_parent_id') THEN
        RAISE EXCEPTION 'FAIL: index ix_m_parameter_parent_id is missing';
    END IF;
    RAISE NOTICE 'PASS test 5: parent_id is indexed';
END $$;

ROLLBACK;
