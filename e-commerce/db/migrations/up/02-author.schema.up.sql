CREATE SCHEMA IF NOT EXISTS author;

CREATE TABLE
    IF NOT EXISTS author.m_role (
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
        description VARCHAR(256) NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_role_name ON author.m_role (name)
WHERE
    row_status <> 'DELETED';

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
        description VARCHAR(256) NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_permission_name ON author.m_permission (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.m_scope (
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
        scope VARCHAR(64) NOT NULL,
        name VARCHAR(64) NOT NULL,
        description VARCHAR(256) NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_scope_scope ON author.m_scope (scope)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.t_permission_scope (
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
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE RESTRICT,
        scope_id UUID NOT NULL REFERENCES author.m_scope (id) ON DELETE RESTRICT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_permission_scope_permission_id_scope_id ON author.t_permission_scope (permission_id, scope_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.t_role_permission (
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
        role_id UUID NOT NULL REFERENCES author.m_role (id) ON DELETE RESTRICT,
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE RESTRICT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_role_permission_role_id_permission_id ON author.t_role_permission (role_id, permission_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.t_role_permission_scope (
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
        role_permission_id UUID NOT NULL REFERENCES author.t_role_permission (id) ON DELETE CASCADE,
        permission_scope_id UUID NOT NULL REFERENCES author.t_permission_scope (id) ON DELETE RESTRICT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_role_permission_scope_role_permission_scope ON author.t_role_permission_scope (role_permission_id, permission_scope_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.t_user_role (
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
        role_id UUID NOT NULL REFERENCES author.m_role (id) ON DELETE RESTRICT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_role_user_id_role_id ON author.t_user_role (user_id, role_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS author.t_user_permission (
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
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE RESTRICT,
        permission_scope_id UUID REFERENCES author.t_permission_scope (id) ON DELETE RESTRICT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_permission_user_id_permission_id ON author.t_user_permission (user_id, permission_id)
WHERE
    permission_scope_id IS NULL
    AND row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_permission_user_id_permission_scope ON author.t_user_permission (user_id, permission_id, permission_scope_id)
WHERE
    permission_scope_id IS NOT NULL
    AND row_status <> 'DELETED';
