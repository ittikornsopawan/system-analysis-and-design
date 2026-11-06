# Table: author.t_permission_scope

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
| FK  | [author.m_permission.id](m_permission.md) | permission_id | UUID      |        | FALSE       | Reference to `author.m_permission.id`                                    |                   |
| FK  | [author.m_scope.id](m_scope.md)           | scope_id      | UUID      |        | FALSE       | Reference to `author.m_scope.id`                                         |                   |

## Constain

| Key Name                                     | Column Name             | Description                                                                   |
| -------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------- |
| pk_t_permission_scope_id                     | id                      | Primary key                                                                   |
| fk_t_permission_scope_permission_id          | permission_id           | References author.m_permission(id), ON DELETE RESTRICT                        |
| fk_t_permission_scope_scope_id               | scope_id                | References author.m_scope(id), ON DELETE RESTRICT                             |
| uq_t_permission_scope_permission_id_scope_id | permission_id, scope_id | Unique among rows where row_status <> 'DELETED'                               |
| ck_t_permission_scope_row_status             | row_status              | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
```
