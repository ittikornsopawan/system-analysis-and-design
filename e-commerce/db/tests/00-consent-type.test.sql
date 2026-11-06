-- Tests for consent.m_consent_type (WP6 B1, B2, B7):
--   * name is unique among rows that are not DELETED (partial unique index, a DELETED name can be reused)
--   * consent.t_consent.consent_type_id is ON DELETE RESTRICT
--   * description is optional and is_required defaults to FALSE (guards the current shape, passes before and after)
-- Run after 00-common.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

-- test 1: a name used by a non deleted consent type cannot be used again
DO $$
BEGIN
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Marketing');
    BEGIN
        INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Marketing');
        RAISE EXCEPTION 'FAIL: a duplicate consent type name was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 1: name unique among non deleted consent types';
END $$;

-- test 2: INACTIVE, LOCKED and ARCHIVED consent types still hold their name
DO $$
DECLARE s TEXT;
BEGIN
    FOREACH s IN ARRAY ARRAY['INACTIVE', 'LOCKED', 'ARCHIVED'] LOOP
        INSERT INTO consent.m_consent_type (created_by, name, row_status) VALUES ('test', 'Held ' || s, s);
        BEGIN
            INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Held ' || s);
            RAISE EXCEPTION 'FAIL: the name of an % consent type was reused', s;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    RAISE NOTICE 'PASS test 2: INACTIVE, LOCKED and ARCHIVED consent types keep their name';
END $$;

-- test 3: the name of a DELETED consent type can be used again, also more than once
DO $$
DECLARE live INT;
BEGIN
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Reusable');
    UPDATE consent.m_consent_type SET row_status = 'DELETED' WHERE name = 'Reusable';
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Reusable');
    UPDATE consent.m_consent_type SET row_status = 'DELETED' WHERE name = 'Reusable' AND row_status = 'ACTIVE';
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Reusable');
    SELECT COUNT(*) INTO live FROM consent.m_consent_type WHERE name = 'Reusable' AND row_status <> 'DELETED';
    IF live <> 1 THEN
        RAISE EXCEPTION 'FAIL: expected one live Reusable consent type, found %', live;
    END IF;
    BEGIN
        INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Reusable');
        RAISE EXCEPTION 'FAIL: a second live Reusable consent type was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    RAISE NOTICE 'PASS test 3: the name of a DELETED consent type can be reused';
END $$;

-- test 4: a consent type used by a consent cannot be deleted for real (RESTRICT), a soft delete is still possible
DO $$
DECLARE ct UUID;
BEGIN
    IF (SELECT c.confdeltype FROM pg_constraint c
        WHERE c.conrelid = 'consent.t_consent'::regclass AND c.contype = 'f'
          AND c.confrelid = 'consent.m_consent_type'::regclass) IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION 'FAIL: t_consent.consent_type_id must be ON DELETE RESTRICT';
    END IF;
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Restrict type') RETURNING id INTO ct;
    INSERT INTO consent.t_consent (created_by, code, consent_type_id, consent_name, body)
    VALUES ('test', 'RESTRICT-001', ct, 'Restrict consent', '{"th": "x"}'::jsonb);
    BEGIN
        DELETE FROM consent.m_consent_type WHERE id = ct;
        RAISE EXCEPTION 'FAIL: a consent type used by a consent was hard deleted';
    EXCEPTION WHEN foreign_key_violation THEN NULL;
    END;
    IF NOT EXISTS (SELECT 1 FROM consent.t_consent WHERE code = 'RESTRICT-001') THEN
        RAISE EXCEPTION 'FAIL: the consent disappeared';
    END IF;
    UPDATE consent.m_consent_type SET row_status = 'DELETED' WHERE id = ct;
    RAISE NOTICE 'PASS test 4: t_consent.consent_type_id restricts the delete of its consent type';
END $$;

-- test 5: description is optional and is_required defaults to FALSE
DO $$
DECLARE d TEXT; r BOOLEAN;
BEGIN
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'Bare type');
    SELECT description, is_required INTO d, r FROM consent.m_consent_type WHERE name = 'Bare type';
    IF d IS NOT NULL OR r IS DISTINCT FROM FALSE THEN
        RAISE EXCEPTION 'FAIL: description should be NULL and is_required FALSE, found % / %', d, r;
    END IF;
    RAISE NOTICE 'PASS test 5: consent type description is optional and is_required defaults to FALSE';
END $$;

ROLLBACK;
