-- Tests for WP4 (authen): session_id on the token tables, one live row per user for reset password, password,
-- user information and default address, and the login attempt log.
-- Run after 01-authen.schema.up.sql. Everything is rolled back at the end.
\set ON_ERROR_STOP on
BEGIN;

CREATE TEMP TABLE fx_user (n INT PRIMARY KEY, id UUID) ON COMMIT DROP;
WITH u1 AS (
    INSERT INTO authen.m_user (created_by, username, email_address) VALUES ('test', '\x0101'::bytea, '\x0201'::bytea) RETURNING id
), u2 AS (
    INSERT INTO authen.m_user (created_by, username, email_address) VALUES ('test', '\x0102'::bytea, '\x0202'::bytea) RETURNING id
)
INSERT INTO fx_user (n, id) SELECT 1, id FROM u1 UNION ALL SELECT 2, id FROM u2;

-- test 1: every token row belongs to a session (session_id is required), tokens stay unique
DO $$
DECLARE u UUID := (SELECT id FROM fx_user WHERE n = 1); s UUID := GEN_RANDOM_UUID(); t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY['t_user_access_token', 't_user_refresh_token'] LOOP
        BEGIN
            EXECUTE format('INSERT INTO authen.%I (created_by, user_id, token, expired_at) VALUES (%L, %L, ''\xaa01''::bytea, NOW())', t, 'test', u);
            RAISE EXCEPTION 'FAIL: % accepted a row without session_id', t;
        EXCEPTION WHEN not_null_violation THEN NULL;
        END;
        EXECUTE format('INSERT INTO authen.%I (created_by, user_id, session_id, token, expired_at) VALUES (%L, %L, %L, ''\xaa02''::bytea, NOW())', t, 'test', u, s);
        BEGIN
            EXECUTE format('INSERT INTO authen.%I (created_by, user_id, session_id, token, expired_at) VALUES (%L, %L, %L, ''\xaa02''::bytea, NOW())', t, 'test', u, s);
            RAISE EXCEPTION 'FAIL: % accepted the same token twice', t;
        EXCEPTION WHEN unique_violation THEN NULL;
        END;
    END LOOP;
    -- several access tokens of one session are allowed (one per login and refresh)
    INSERT INTO authen.t_user_access_token (created_by, user_id, session_id, token, expired_at) VALUES ('test', u, s, '\xaa03'::bytea, NOW());
    RAISE NOTICE 'PASS test 1: token rows need a session_id, a session may hold several access tokens';
END $$;

-- test 2: one ACTIVE reset row per user, a used or replaced row (INACTIVE) lets the next one in
DO $$
DECLARE u1 UUID := (SELECT id FROM fx_user WHERE n = 1); u2 UUID := (SELECT id FROM fx_user WHERE n = 2);
BEGIN
    INSERT INTO authen.t_user_reset_password (created_by, user_id, reset_token, expired_at) VALUES ('test', u1, '\xbb01'::bytea, NOW());
    BEGIN
        INSERT INTO authen.t_user_reset_password (created_by, user_id, reset_token, expired_at) VALUES ('test', u1, '\xbb02'::bytea, NOW());
        RAISE EXCEPTION 'FAIL: a second ACTIVE reset row of one user was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO authen.t_user_reset_password (created_by, user_id, reset_token, expired_at) VALUES ('test', u2, '\xbb03'::bytea, NOW());
    UPDATE authen.t_user_reset_password SET row_status = 'INACTIVE' WHERE user_id = u1;
    INSERT INTO authen.t_user_reset_password (created_by, user_id, reset_token, expired_at) VALUES ('test', u1, '\xbb04'::bytea, NOW());
    UPDATE authen.t_user_reset_password SET row_status = 'INACTIVE' WHERE user_id = u1;
    INSERT INTO authen.t_user_reset_password (created_by, user_id, reset_token, expired_at) VALUES ('test', u1, '\xbb05'::bytea, NOW());
    RAISE NOTICE 'PASS test 2: one ACTIVE reset row per user';
END $$;

-- test 3: one ACTIVE PASSWORD row per user, history stays, a TEMPORARY_PASSWORD is separate
DO $$
DECLARE u UUID := (SELECT id FROM fx_user WHERE n = 1);
BEGIN
    INSERT INTO authen.m_user_password (created_by, user_id, password, password_salt) VALUES ('test', u, '\xcc01'::bytea, '\xdd01'::bytea);
    BEGIN
        INSERT INTO authen.m_user_password (created_by, user_id, password, password_salt) VALUES ('test', u, '\xcc02'::bytea, '\xdd02'::bytea);
        RAISE EXCEPTION 'FAIL: a second ACTIVE PASSWORD row of one user was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO authen.m_user_password (created_by, row_type, user_id, password, password_salt) VALUES ('test', 'TEMPORARY_PASSWORD', u, '\xcc03'::bytea, '\xdd03'::bytea);
    UPDATE authen.m_user_password SET row_status = 'INACTIVE' WHERE user_id = u AND row_type = 'PASSWORD';
    INSERT INTO authen.m_user_password (created_by, user_id, password, password_salt) VALUES ('test', u, '\xcc04'::bytea, '\xdd04'::bytea);
    IF (SELECT COUNT(*) FROM authen.m_user_password WHERE user_id = u AND row_type = 'PASSWORD') <> 2 THEN
        RAISE EXCEPTION 'FAIL: the old password row should stay as history';
    END IF;
    RAISE NOTICE 'PASS test 3: one ACTIVE PASSWORD per user, history kept';
END $$;

-- test 4: one user information row per user among rows that are not DELETED
DO $$
DECLARE u1 UUID := (SELECT id FROM fx_user WHERE n = 1); u2 UUID := (SELECT id FROM fx_user WHERE n = 2);
BEGIN
    INSERT INTO authen.m_user_information (created_by, user_id) VALUES ('test', u1);
    BEGIN
        INSERT INTO authen.m_user_information (created_by, user_id) VALUES ('test', u1);
        RAISE EXCEPTION 'FAIL: a second information row of one user was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    INSERT INTO authen.m_user_information (created_by, user_id) VALUES ('test', u2);
    UPDATE authen.m_user_information SET row_status = 'DELETED' WHERE user_id = u1;
    INSERT INTO authen.m_user_information (created_by, user_id) VALUES ('test', u1);
    RAISE NOTICE 'PASS test 4: one information row per user';
END $$;

-- test 5: at most one default address per user among rows that are not DELETED
DO $$
DECLARE u1 UUID := (SELECT id FROM fx_user WHERE n = 1); u2 UUID := (SELECT id FROM fx_user WHERE n = 2);
BEGIN
    INSERT INTO authen.t_user_address (created_by, user_id, title, is_default, address, city, state, postal_code, country)
    VALUES ('test', u1, 'Home', TRUE, '\xee01'::bytea, '\xee02'::bytea, '\xee03'::bytea, '\xee04'::bytea, '\xee05'::bytea);
    BEGIN
        INSERT INTO authen.t_user_address (created_by, user_id, title, is_default, address, city, state, postal_code, country)
        VALUES ('test', u1, 'Office', TRUE, '\xee01'::bytea, '\xee02'::bytea, '\xee03'::bytea, '\xee04'::bytea, '\xee05'::bytea);
        RAISE EXCEPTION 'FAIL: a second default address of one user was accepted';
    EXCEPTION WHEN unique_violation THEN NULL;
    END;
    -- many non default addresses, and a default of another user, are fine
    INSERT INTO authen.t_user_address (created_by, user_id, title, address, city, state, postal_code, country)
    VALUES ('test', u1, 'Office', '\xee01'::bytea, '\xee02'::bytea, '\xee03'::bytea, '\xee04'::bytea, '\xee05'::bytea),
           ('test', u1, 'Parents', '\xee01'::bytea, '\xee02'::bytea, '\xee03'::bytea, '\xee04'::bytea, '\xee05'::bytea);
    INSERT INTO authen.t_user_address (created_by, user_id, title, is_default, address, city, state, postal_code, country)
    VALUES ('test', u2, 'Home', TRUE, '\xee01'::bytea, '\xee02'::bytea, '\xee03'::bytea, '\xee04'::bytea, '\xee05'::bytea);
    -- a DELETED default no longer holds the slot
    UPDATE authen.t_user_address SET row_status = 'DELETED' WHERE user_id = u1 AND title = 'Home';
    UPDATE authen.t_user_address SET is_default = TRUE WHERE user_id = u1 AND title = 'Office';
    RAISE NOTICE 'PASS test 5: one default address per user';
END $$;

-- test 6: login attempts: identifier and result are required, the result is SUCCESS, FAILED or REFUSED, the user is optional, the log follows the user
DO $$
DECLARE u UUID := (SELECT id FROM fx_user WHERE n = 1); r TEXT;
BEGIN
    INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, user_id, result) VALUES ('system', '\xff01'::bytea, u, 'FAILED');
    INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, result) VALUES ('system', '\xff02'::bytea, 'FAILED');
    FOREACH r IN ARRAY ARRAY['SUCCESS', 'FAILED', 'REFUSED'] LOOP
        INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, result) VALUES ('system', '\xff04'::bytea, r);
    END LOOP;
    BEGIN
        INSERT INTO authen.l_user_login_attempt (created_by, user_id, result) VALUES ('system', u, 'FAILED');
        RAISE EXCEPTION 'FAIL: an attempt without identifier_hash was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash) VALUES ('system', '\xff03'::bytea);
        RAISE EXCEPTION 'FAIL: an attempt without result was accepted';
    EXCEPTION WHEN not_null_violation THEN NULL;
    END;
    BEGIN
        INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, result) VALUES ('system', '\xff03'::bytea, 'BLOCKED');
        RAISE EXCEPTION 'FAIL: an attempt with an unknown result was accepted';
    EXCEPTION WHEN check_violation THEN NULL;
    END;
    IF (SELECT c.confdeltype FROM pg_constraint c WHERE c.conrelid = 'authen.l_user_login_attempt'::regclass AND c.contype = 'f') IS DISTINCT FROM 'c' THEN
        RAISE EXCEPTION 'FAIL: l_user_login_attempt.user_id must be ON DELETE CASCADE';
    END IF;
    DELETE FROM authen.m_user WHERE id = u;
    IF EXISTS (SELECT 1 FROM authen.l_user_login_attempt WHERE identifier_hash = '\xff01'::bytea) THEN
        RAISE EXCEPTION 'FAIL: the attempt of a deleted user survived';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM authen.l_user_login_attempt WHERE identifier_hash = '\xff02'::bytea) THEN
        RAISE EXCEPTION 'FAIL: the attempt of an unknown username disappeared';
    END IF;
    RAISE NOTICE 'PASS test 6: login attempt log';
END $$;

-- test 7: a refused attempt is logged but is not counted, so a block of 5 failures ends by itself
-- (the count is the query of 02-login: result = FAILED inside the window)
DO $$
DECLARE h BYTEA := '\xff10'; blocked INT; later INT; i INT;
BEGIN
    FOR i IN 1..5 LOOP
        INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, result, created_at)
        VALUES ('system', h, 'FAILED', LOCALTIMESTAMP - make_interval(mins => 16 - 2 * i)); -- 14, 12, 10, 8 and 6 minutes ago
    END LOOP;
    FOR i IN 1..30 LOOP
        INSERT INTO authen.l_user_login_attempt (created_by, identifier_hash, result, created_at)
        VALUES ('system', h, 'REFUSED', LOCALTIMESTAMP - make_interval(secs => i * 10)); -- an attacker keeps sending requests
    END LOOP;
    SELECT COUNT(*) INTO blocked FROM authen.l_user_login_attempt la
    WHERE la.identifier_hash = h AND la.result = 'FAILED' AND la.created_at > LOCALTIMESTAMP - INTERVAL '15 minutes';
    IF blocked <> 5 THEN
        RAISE EXCEPTION 'FAIL: expected 5 counted failures now, found %', blocked;
    END IF;
    -- two minutes later the failure of 14 minutes ago is older than the window, the refused requests must not keep the block
    SELECT COUNT(*) INTO later FROM authen.l_user_login_attempt la
    WHERE la.identifier_hash = h AND la.result = 'FAILED' AND la.created_at > (LOCALTIMESTAMP + INTERVAL '2 minutes') - INTERVAL '15 minutes';
    IF later <> 4 THEN
        RAISE EXCEPTION 'FAIL: expected 4 counted failures two minutes later, found %', later;
    END IF;
    RAISE NOTICE 'PASS test 7: refused attempts are not counted';
END $$;

ROLLBACK;
