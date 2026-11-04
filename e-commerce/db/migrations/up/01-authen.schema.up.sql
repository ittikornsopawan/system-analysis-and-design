CREATE SCHEMA IF NOT EXISTS authen;

CREATE TABLE
    IF NOT EXISTS authen.m_user (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        username BYTEA NOT NULL UNIQUE,
        email_address BYTEA NOT NULL UNIQUE,
        first_name BYTEA NOT NULL,
        last_name BYTEA NOT NULL,
        display_name VARCHAR(128) NOT NULL,
        profile_picture_path TEXT
    );

CREATE TABLE
    IF NOT EXISTS authen.t_user_consent (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        consent_id UUID NOT NULL REFERENCES consent.t_consent (id) ON DELETE CASCADE,
        consent_version VARCHAR(8) NOT NULL DEFAULT '1.0.0',
        result BOOLEAN NOT NULL DEFAULT FALSE
    );

CREATE TABLE
    IF NOT EXISTS authen.m_user_password (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        row_type VARCHAR(32) NOT NULL DEFAULT 'PASSWORD' CHECK (row_type IN ('PASSWORD', 'TEMPORARY_PASSWORD')),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        password BYTEA NOT NULL,
        password_salt BYTEA NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS authen.t_user_reset_password (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        reset_token BYTEA NOT NULL UNIQUE,
        expired_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS authen.l_user_referral (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        referrer_id UUID REFERENCES authen.m_user (id) ON DELETE SET NULL
    );

CREATE TABLE
    IF NOT EXISTS authen.m_user_information (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        phone_number BYTEA,
        address BYTEA,
        date_of_birth DATE,
        gender VARCHAR(16) CHECK (gender IN ('MALE', 'FEMALE', '', 'OTHER'))
    );

CREATE TABLE
    IF NOT EXISTS authen.t_user_address (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        title VARCHAR(128) NOT NULL,
        is_default BOOLEAN NOT NULL DEFAULT FALSE,
        address BYTEA NOT NULL,
        city BYTEA NOT NULL,
        state BYTEA NOT NULL,
        postal_code BYTEA NOT NULL,
        country BYTEA NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS authen.t_user_access_token (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        token BYTEA NOT NULL UNIQUE,
        expired_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS authen.t_user_refresh_token (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        updated_by VARCHAR(64),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        row_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (
            row_status IN (
                'ACTIVE',
                'INACTIVE',
                'DELETED',
                'LOCKED',
                'ARCHIVED'
            )
        ),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        token BYTEA NOT NULL UNIQUE,
        expired_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
    );