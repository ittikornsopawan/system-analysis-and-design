-- Tests for the view consent.v_applicable_consent (an ACTIVE consent of an ACTIVE consent type, with no time filter):
--   * an INACTIVE consent, a DELETED consent and an ACTIVE consent of an INACTIVE type are excluded
--   * an ACTIVE consent of an ACTIVE type is included, also when it is not in effect now (callers filter the time)
--   * the view has exactly the columns id, consent_type_id, consent_version, is_required, effective_at, expired_at
-- Run after 00-common.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

DO $$
DECLARE on_type UUID; off_type UUID;
BEGIN
    INSERT INTO consent.m_consent_type (created_by, name) VALUES ('test', 'View on') RETURNING id INTO on_type;
    INSERT INTO consent.m_consent_type (created_by, name, row_status) VALUES ('test', 'View off', 'INACTIVE') RETURNING id INTO off_type;
    INSERT INTO consent.t_consent (created_by, code, consent_type_id, consent_name, row_status, body, effective_at, expired_at) VALUES
        ('test', 'VIEW-ACTIVE', on_type, 'Active', 'ACTIVE', '{}'::jsonb, '2026-01-01', NULL),
        ('test', 'VIEW-FUTURE', on_type, 'Future', 'ACTIVE', '{}'::jsonb, '2999-01-01', NULL),
        ('test', 'VIEW-INACTIVE', on_type, 'Inactive', 'INACTIVE', '{}'::jsonb, '2026-01-01', NULL),
        ('test', 'VIEW-DELETED', on_type, 'Deleted', 'DELETED', '{}'::jsonb, '2026-01-01', NULL),
        ('test', 'VIEW-TYPE-OFF', off_type, 'Type off', 'ACTIVE', '{}'::jsonb, '2026-01-01', NULL);
END $$;

-- test 1: the view has exactly the six agreed columns, in order
DO $$
DECLARE cols TEXT;
BEGIN
    SELECT string_agg(column_name, ',' ORDER BY ordinal_position) INTO cols
    FROM information_schema.columns WHERE table_schema = 'consent' AND table_name = 'v_applicable_consent';
    IF cols IS DISTINCT FROM 'id,consent_type_id,consent_version,is_required,effective_at,expired_at' THEN
        RAISE EXCEPTION 'FAIL: v_applicable_consent columns are %', cols;
    END IF;
    RAISE NOTICE 'PASS test 1: v_applicable_consent has the six agreed columns';
END $$;

-- test 2: an INACTIVE consent, a DELETED consent and an ACTIVE consent of an INACTIVE type are excluded
DO $$
DECLARE code_ TEXT;
BEGIN
    FOREACH code_ IN ARRAY ARRAY['VIEW-INACTIVE', 'VIEW-DELETED', 'VIEW-TYPE-OFF'] LOOP
        IF EXISTS (SELECT 1 FROM consent.v_applicable_consent v JOIN consent.t_consent c ON c.id = v.id WHERE c.code = code_) THEN
            RAISE EXCEPTION 'FAIL: % is in v_applicable_consent', code_;
        END IF;
    END LOOP;
    RAISE NOTICE 'PASS test 2: INACTIVE, DELETED and inactive-type consents are excluded';
END $$;

-- test 3: an ACTIVE consent of an ACTIVE type is included with its own values; the view applies no time filter
DO $$
DECLARE n INT;
BEGIN
    SELECT COUNT(*) INTO n
    FROM consent.v_applicable_consent v JOIN consent.t_consent c ON c.id = v.id
    WHERE c.code IN ('VIEW-ACTIVE', 'VIEW-FUTURE')
    AND v.consent_type_id = c.consent_type_id AND v.consent_version = c.consent_version AND v.is_required = c.is_required
    AND v.effective_at = c.effective_at AND v.expired_at IS NOT DISTINCT FROM c.expired_at;
    IF n <> 2 THEN
        RAISE EXCEPTION 'FAIL: expected the ACTIVE and the future ACTIVE consent in the view, found %', n;
    END IF;
    RAISE NOTICE 'PASS test 3: an ACTIVE consent of an ACTIVE type is included, with no time filter';
END $$;

ROLLBACK;
