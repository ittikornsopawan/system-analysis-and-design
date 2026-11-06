# Table: author.t_user_role

Description: Transaction table of the `author` schema (defined in `db/migrations/up/02-author.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [authen.m_user.id](../authen/m_user.md) | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
| FK  | [author.m_role.id](m_role.md)           | role_id     | UUID      |        | FALSE       | Reference to `author.m_role.id`                                          |                   |

## Constain

| Key Name                       | Column Name      | Description                                                                   |
| ------------------------------ | ---------------- | ----------------------------------------------------------------------------- |
| pk_t_user_role_id              | id               | Primary key                                                                   |
| fk_t_user_role_user_id         | user_id          | References authen.m_user(id), ON DELETE CASCADE                               |
| fk_t_user_role_role_id         | role_id          | References author.m_role(id), ON DELETE RESTRICT                              |
| uq_t_user_role_user_id_role_id | user_id, role_id | Unique among rows where row_status <> 'DELETED'                               |
| ck_t_user_role_row_status      | row_status       | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
```
