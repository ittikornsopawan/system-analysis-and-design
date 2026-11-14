---
name: "Schema doc: author.t_role_permission"
description: "Columns, keys, constraints and indexes of the table author.t_role_permission. Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: author.t_role_permission

Description: Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`).

## Columns

| Key | Reference                                 | Column Name   | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ----------------------------------------- | ------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                           | id            | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                           | created_by    | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                           | created_at    | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                           | updated_by    | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                           | updated_at    | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                           | row_status    | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [author.m_role.id](m_role.md)             | role_id       | UUID      |        | FALSE       | Reference to `author.m_role.id`                                          |                   |
| FK  | [author.m_permission.id](m_permission.md) | permission_id | UUID      |        | FALSE       | Reference to `author.m_permission.id`                                    |                   |

## Constain

| Key Name                                   | Column Name            | Description                                                                   |
| ------------------------------------------ | ---------------------- | ----------------------------------------------------------------------------- |
| pk_t_role_permission_id                    | id                     | Primary key                                                                   |
| fk_t_role_permission_role_id               | role_id                | References author.m_role(id), ON DELETE RESTRICT                              |
| fk_t_role_permission_permission_id         | permission_id          | References author.m_permission(id), ON DELETE RESTRICT                        |
| uq_t_role_permission_role_id_permission_id | role_id, permission_id | Unique among rows where row_status <> 'DELETED'                               |
| ck_t_role_permission_row_status            | row_status             | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
```
