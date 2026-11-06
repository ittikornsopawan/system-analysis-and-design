# Table: authen.m_user_information

Description: Master table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                     | Column Name   | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ----------------------------- | ------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                               | id            | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                               | created_by    | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                               | created_at    | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                               | updated_by    | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                               | updated_at    | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                               | row_status    | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [authen.m_user.id](m_user.md) | user_id       | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
|     |                               | phone_number  | BYTEA     |        | TRUE        |                                                                          |                   |
|     |                               | address       | BYTEA     |        | TRUE        |                                                                          |                   |
|     |                               | date_of_birth | DATE      |        | TRUE        |                                                                          |                   |
|     |                               | gender        | VARCHAR   | 16     | TRUE        | One of: MALE, FEMALE, , OTHER                                            | MALE              |

## Constain

| Key Name                         | Column Name | Description                                                                    |
| -------------------------------- | ----------- | ------------------------------------------------------------------------------ |
| pk_m_user_information_id         | id          | Primary key                                                                    |
| fk_m_user_information_user_id    | user_id     | References authen.m_user(id), ON DELETE CASCADE                                |
| ck_m_user_information_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))  |
| ck_m_user_information_gender     | gender      | CHECK (gender IN ('MALE', 'FEMALE', '', 'OTHER'))                              |
| uq_m_user_information_user_id    | user_id     | Unique among rows where row_status <> 'DELETED' (one information row per user) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.m_user_information (
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
        phone_number BYTEA,
        address BYTEA,
        date_of_birth DATE,
        gender VARCHAR(16) CHECK (gender IN ('MALE', 'FEMALE', '', 'OTHER'))
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_user_information_user_id ON authen.m_user_information (user_id)
WHERE
    row_status <> 'DELETED';
```
