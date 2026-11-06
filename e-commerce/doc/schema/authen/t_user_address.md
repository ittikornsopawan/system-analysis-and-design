# Table: authen.t_user_address

Description: Transaction table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                     | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ----------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                               | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                               | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                               | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                               | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                               | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                               | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [authen.m_user.id](m_user.md) | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
|     |                               | title       | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                               | is_default  | BOOLEAN   |        | FALSE       | Defaults to `FALSE`, at most one default per user                        | FALSE             |
|     |                               | address     | BYTEA     |        | FALSE       |                                                                          |                   |
|     |                               | city        | BYTEA     |        | FALSE       |                                                                          |                   |
|     |                               | state       | BYTEA     |        | FALSE       |                                                                          |                   |
|     |                               | postal_code | BYTEA     |        | FALSE       |                                                                          |                   |
|     |                               | country     | BYTEA     |        | FALSE       |                                                                          |                   |

## Constain

| Key Name                          | Column Name | Description                                                                                   |
| --------------------------------- | ----------- | --------------------------------------------------------------------------------------------- |
| pk_t_user_address_id              | id          | Primary key                                                                                   |
| fk_t_user_address_user_id         | user_id     | References authen.m_user(id), ON DELETE CASCADE                                               |
| ck_t_user_address_row_status      | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                 |
| uq_t_user_address_user_id_default | user_id     | Unique among rows where is_default AND row_status <> 'DELETED' (one default address per user) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.t_user_address (
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
        title VARCHAR(128) NOT NULL,
        is_default BOOLEAN NOT NULL DEFAULT FALSE,
        address BYTEA NOT NULL,
        city BYTEA NOT NULL,
        state BYTEA NOT NULL,
        postal_code BYTEA NOT NULL,
        country BYTEA NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_user_address_user_id_default ON authen.t_user_address (user_id)
WHERE
    is_default
    AND row_status <> 'DELETED';
```
