---
name: "Schema doc: author.t_user_permission"
description: "Columns, keys, constraints and indexes of the table author.t_user_permission. Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: author.t_user_permission

Description: Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`).

## Columns

| Key | Reference                                             | Column Name         | Data Type | Length | Is Nullable | Description                                                                                                               | Example           |
| --- | ----------------------------------------------------- | ------------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                                       | id                  | UUID      |        | FALSE       | Primary key                                                                                                               | gen_random_uuid() |
|     |                                                       | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                      |                   |
|     |                                                       | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                        |                   |
|     |                                                       | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                                 |                   |
|     |                                                       | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                                   |                   |
|     |                                                       | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                                  | ACTIVE            |
| FK  | [authen.m_user.id](../authen/m_user.md)               | user_id             | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                                                                           |                   |
| FK  | [author.m_permission.id](m_permission.md)             | permission_id       | UUID      |        | FALSE       | Reference to `author.m_permission.id`                                                                                     |                   |
| FK  | [author.t_permission_scope.id](t_permission_scope.md) | permission_scope_id | UUID      |        | TRUE        | Reference to `author.t_permission_scope.id` (a scope that the permission can have), NULL when the permission has no scope |                   |

## Constain

| Key Name                                      | Column Name                                 | Description                                                                         |
| --------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- |
| pk_t_user_permission_id                       | id                                          | Primary key                                                                         |
| fk_t_user_permission_user_id                  | user_id                                     | References authen.m_user(id), ON DELETE CASCADE                                     |
| fk_t_user_permission_permission_id            | permission_id                               | References author.m_permission(id), ON DELETE RESTRICT                              |
| fk_t_user_permission_permission_scope_id      | permission_scope_id                         | References author.t_permission_scope(id), ON DELETE RESTRICT                        |
| uq_t_user_permission_user_id_permission_id    | user_id, permission_id                      | Unique among rows where permission_scope_id IS NULL AND row_status <> 'DELETED'     |
| uq_t_user_permission_user_id_permission_scope | user_id, permission_id, permission_scope_id | Unique among rows where permission_scope_id IS NOT NULL AND row_status <> 'DELETED' |
| ck_t_user_permission_row_status               | row_status                                  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))       |

---

```SQL
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
```
