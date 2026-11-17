-- Tests for public.m_parameter:
--   * key is unique among rows that are not DELETED (partial unique index, a DELETED key can be reused)
--   * parent_id references m_parameter(id) ON DELETE RESTRICT
--   * value is required and row_status has the 5 standard values
-- Run after 00-common.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a key used by a non deleted parameter cannot be used again
DO $$
DECLARE s TEXT;
BEGIN
    INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'currency', '"THB"');
    BEGIN
        INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'currency', '"USD"');
        RAISE EXCEPTION 'FAIL: a duplicate parameter key was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO public.m_parameter (created_by, key, value, row_status) VALUES ('test', 'held.' || s, '1', s);
        BEGIN
            INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'held.' || s, '1');
            RAISE EXCEPTION 'FAIL: the key of an % parameter was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 1: key unique among non deleted parameters';
END $$;

-- test 2: the key of a DELETED parameter can be used again, also more than once
DO $$
DECLARE live INT;
BEGIN
    INSERT INTO public.m_parameter (created_by, key, value, row_status) VALUES ('test', 'reusable', '1', 'DELETED');
    INSERT INTO public.m_parameter (created_by, key, value, row_status) VALUES ('test', 'reusable', '2', 'DELETED');
    INSERT INTO public.m_parameter (created_by, key, value) VALUES ('test', 'reusable', '3');
    SELECT count(*) INTO live FROM public.m_parameter WHERE key = 'reusable' AND row_status <> 'DELETED';
    IF live <> 1 THEN RAISE EXCEPTION 'FAIL: expected 1 live reusable key, found %', live; END IF;
    RAISE NOTICE 'PASS test 2: the key of a DELETED parameter can be reused';
END $$;

-- test 3: a parent with children cannot be deleted, and parent_id must point to a real parameter
DO $$
DECLARE p UUID;
BEGIN
    INSERT INTO public.m_parameter (created_by, key, value, title) VALUES ('test', 'country.th', '"TH"', '{"en": "Thailand", "th": "ไทย"}') RETURNING id INTO p;
    INSERT INTO public.m_parameter (created_by, parent_id, key, value) VALUES ('test', p, 'province.th.10', '"10"');
    BEGIN
        DELETE FROM public.m_parameter WHERE id = p;
        RAISE EXCEPTION 'FAIL: a parent parameter with children was deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO public.m_parameter (created_by, parent_id, key, value) VALUES ('test', gen_random_uuid(), 'orphan', '1');
        RAISE EXCEPTION 'FAIL: a parameter with an unknown parent was accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: parent_id is ON DELETE RESTRICT and must exist';
END $$;

-- test 4: value is required and EXPIRED is not a row_status (expired_at says it)
DO $$
BEGIN
    BEGIN
        INSERT INTO public.m_parameter (created_by, key) VALUES ('test', 'no-value');
        RAISE EXCEPTION 'FAIL: a parameter without a value was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO public.m_parameter (created_by, key, value, row_status) VALUES ('test', 'expired', '1', 'EXPIRED');
        RAISE EXCEPTION 'FAIL: row_status EXPIRED was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 4: value is required and row_status has the 5 standard values';
END $$;

ROLLBACK;
