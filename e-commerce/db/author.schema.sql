CREATE SCHEMA IF NOT EXISTS author;

CREATE TABLE
    IF NOT EXISTS author.m_attribute (
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
        parent_id UUID REFERENCES author.m_attribute (id) ON DELETE SET NULL,
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256)
    );

CREATE TABLE
    IF NOT EXISTS author.t_attribute_option (
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
        attribute_id UUID NOT NULL REFERENCES author.m_attribute (id) ON DELETE CASCADE,
        value VARCHAR(256) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS author.m_entity (
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
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256)
    );

CREATE TABLE
    IF NOT EXISTS author.t_entity_attribute (
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
        entity_id UUID NOT NULL REFERENCES author.m_entity (id) ON DELETE CASCADE,
        attribute_id UUID NOT NULL REFERENCES author.m_attribute (id) ON DELETE CASCADE,
        value JSONB NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS author.m_resource (
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
        parent_id UUID REFERENCES author.m_resource (id) ON DELETE SET NULL,
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256)
    );

CREATE TABLE
    IF NOT EXISTS author.m_action (
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
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256)
    );

CREATE TABLE
    IF NOT EXISTS author.m_permission (
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
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256)
    );

CREATE TABLE
    IF NOT EXISTS author.m_policy (
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
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256),
        effect VARCHAR(8) NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
        priority INTEGER NOT NULL DEFAULT 0,
        combining_algorithm VARCHAR(32) NOT NULL DEFAULT 'DENY_OVERRIDES' CHECK (
            combining_algorithm IN (
                'DENY_OVERRIDES',
                'PERMIT_OVERRIDES',
                'FIRST_APPLICABLE'
            )
        ),
    );

CREATE TABLE
    IF NOT EXISTS author.t_policy_action (
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
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        action_id UUID NOT NULL REFERENCES author.m_action (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS author.t_policy_permission (
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
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS author.t_policy_condition_group (
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
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        group_condition VARCHAR(32) NOT NULL DEFAULT 'DEFAULT' CHECK (group_condition IN ('DEFAULT', 'AND', 'OR'))
    );

CREATE TABLE
    IF NOT EXISTS author.t_policy_condition (
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
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        attribute_id UUID NOT NULL REFERENCES author.m_attribute (id) ON DELETE CASCADE,
        condition_group_id UUID REFERENCES author.t_policy_condition_group (id) ON DELETE CASCADE,
        operator VARCHAR(16) NOT NULL CHECK (
            operator IN (
                'EQUALS',
                'NOT_EQUALS',
                'GREATER_THAN',
                'LESS_THAN',
                'GREATER_THAN_OR_EQUAL',
                'LESS_THAN_OR_EQUAL',
                'IN',
                'NOT_IN'
            )
        ),
        value VARCHAR(256) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS author.t_attribute_permission (
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
        attribute_id UUID NOT NULL REFERENCES author.m_attribute (id) ON DELETE CASCADE,
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE CASCADE,
        grant VARCHAR(8) NOT NULL CHECK (grant IN ('ALLOW', 'DENY'))
    );

CREATE TABLE
    IF NOT EXISTS t_policy_evaluation (
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
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        resource_id UUID NOT NULL REFERENCES author.m_resource (id) ON DELETE CASCADE,
        action_id UUID NOT NULL REFERENCES author.m_action (id) ON DELETE CASCADE,
        evaluation_result VARCHAR(8) NOT NULL CHECK (evaluation_result IN ('ALLOW', 'DENY'))
    );

CREATE TABLE
    IF NOT EXISTS author.t_policy_evaluation_detail (
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
        evaluation_id UUID NOT NULL REFERENCES author.t_policy_evaluation (id) ON DELETE CASCADE,
        policy_id UUID NOT NULL REFERENCES author.m_policy (id) ON DELETE CASCADE,
        evaluation_result VARCHAR(8) NOT NULL CHECK (evaluation_result IN ('ALLOW', 'DENY'))
    );