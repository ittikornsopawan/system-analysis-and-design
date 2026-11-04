CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE
    IF NOT EXISTS public.t_key (
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
                'ARCHIVED',
                'EXPIRED'
            )
        ),
        effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        expired_at TIMESTAMP WITHOUT TIME ZONE,
        key_name VARCHAR(128) NOT NULL UNIQUE,
        key_value BYTEA NOT NULL
    );

CREATE SCHEMA IF NOT EXISTS consent;

CREATE TABLE
    IF NOT EXISTS consent.m_consent_type (
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
        name VARCHAR(128) NOT NULL UNIQUE,
        description TEXT,
        is_required BOOLEAN NOT NULL DEFAULT FALSE,
    );

CREATE TABLE
    IF NOT EXISTS consent.t_consent (
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
        code VARCHAR(64) NOT NULL UNIQUE,
        consent_type_id UUID NOT NULL REFERENCES consent.m_consent_type (id) ON DELETE CASCADE,
        consent_version VARCHAR(8) NOT NULL DEFAULT '1.0.0',
        consent_name VARCHAR(128) NOT NULL,
        consent_description TEXT,
        effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        expired_at TIMESTAMP WITHOUT TIME ZONE,
        is_required BOOLEAN NOT NULL DEFAULT FALSE,
        body JSONB NOT NULL
    );