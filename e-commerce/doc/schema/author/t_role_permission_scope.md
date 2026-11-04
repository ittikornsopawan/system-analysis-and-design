# Table: author.t_role_permission_scope

Description: Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`).

## Columns

| Key | Reference                                           | Column Name         | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------------------- | ------------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                     | id                  | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                     | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                     | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                     | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                     | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                     | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [author.t_role_permission.id](t_role_permission.md) | role_permission_id  | UUID      |        | FALSE       | Reference to `author.t_role_permission.id`                               |                   |
| FK  | [author.m_scope.id](m_scope.md)                     | permission_scope_id | UUID      |        | FALSE       | Reference to `author.m_scope.id`                                         |                   |

## Constain

| Key Name                                                          | Column Name                             | Description                                                                   |
| ----------------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| pk_t_role_permission_scope_id                                     | id                                      | Primary key                                                                   |
| fk_t_role_permission_scope_role_permission_id                     | role_permission_id                      | References author.t_role_permission(id), ON DELETE CASCADE                    |
| fk_t_role_permission_scope_permission_scope_id                    | permission_scope_id                     | References author.m_scope(id), ON DELETE CASCADE                              |
| uq_t_role_permission_scope_role_permission_id_permission_scope_id | role_permission_id, permission_scope_id | Unique combination                                                            |
| ck_t_role_permission_scope_row_status                             | row_status                              | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
        permission_scope_id UUID NOT NULL REFERENCES author.m_scope (id) ON DELETE CASCADE,
        UNIQUE (role_permission_id, permission_scope_id)
    );
```
