# Table: authen.t_user_access_token

Description: Transaction table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                     | Column Name | Data Type | Length | Is Nullable | Description                                                                               | Example           |
| --- | ----------------------------- | ----------- | --------- | ------ | ----------- | ----------------------------------------------------------------------------------------- | ----------------- |
| PK  |                               | id          | UUID      |        | FALSE       | Primary key                                                                               | gen_random_uuid() |
|     |                               | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                                      |                   |
|     |                               | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                        |                   |
|     |                               | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                 |                   |
|     |                               | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                   |                   |
|     |                               | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                  | ACTIVE            |
| FK  | [authen.m_user.id](m_user.md) | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                                           |                   |
|     |                               | session_id  | UUID      |        | FALSE       | One login session: the access and refresh tokens of a login and of its refreshes share it |                   |
| UQ  |                               | token       | BYTEA     |        | FALSE       | SHA-256 of the token (32 bytes), never the token itself, Unique                           |                   |
|     |                               | expired_at  | TIMESTAMP |        | FALSE       |                                                                                           |                   |

## Constain

| Key Name                          | Column Name | Description                                                                   |
| --------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| pk_t_user_access_token_id         | id          | Primary key                                                                   |
| fk_t_user_access_token_user_id    | user_id     | References authen.m_user(id), ON DELETE CASCADE                               |
| uq_t_user_access_token_token      | token       | Unique                                                                        |
| ck_t_user_access_token_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
        session_id UUID NOT NULL,
        token BYTEA NOT NULL UNIQUE,
        expired_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
    );
```
