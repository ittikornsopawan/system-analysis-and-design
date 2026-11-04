# Table: author.t_user_permission

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
| FK  | [authen.m_user.id](../authen/m_user.md)   | user_id       | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
| FK  | [author.m_permission.id](m_permission.md) | permission_id | UUID      |        | FALSE       | Reference to `author.m_permission.id`                                    |                   |

## Constain

| Key Name                                   | Column Name            | Description                                                                   |
| ------------------------------------------ | ---------------------- | ----------------------------------------------------------------------------- |
| pk_t_user_permission_id                    | id                     | Primary key                                                                   |
| fk_t_user_permission_user_id               | user_id                | References authen.m_user(id), ON DELETE CASCADE                               |
| fk_t_user_permission_permission_id         | permission_id          | References author.m_permission(id), ON DELETE CASCADE                         |
| uq_t_user_permission_user_id_permission_id | user_id, permission_id | Unique combination                                                            |
| ck_t_user_permission_row_status            | row_status             | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

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
        permission_id UUID NOT NULL REFERENCES author.m_permission (id) ON DELETE CASCADE,
        UNIQUE (user_id, permission_id)
    );
```
