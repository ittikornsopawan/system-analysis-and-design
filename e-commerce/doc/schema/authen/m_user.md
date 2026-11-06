# Table: authen.m_user

Description: Master table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference | Column Name          | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------- | -------------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |           | id                   | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |           | created_by           | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |           | created_at           | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |           | updated_by           | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |           | updated_at           | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |           | row_status           | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| UQ  |           | username             | BYTEA     |        | FALSE       | Unique                                                                   |                   |
| UQ  |           | email_address        | BYTEA     |        | FALSE       | Unique                                                                   |                   |
|     |           | first_name           | BYTEA     |        | TRUE        |                                                                          |                   |
|     |           | last_name            | BYTEA     |        | TRUE        |                                                                          |                   |
|     |           | display_name         | VARCHAR   | 128    | TRUE        |                                                                          |                   |
|     |           | profile_picture_path | TEXT      |        | TRUE        |                                                                          |                   |

## Constain

| Key Name                | Column Name   | Description                                                                   |
| ----------------------- | ------------- | ----------------------------------------------------------------------------- |
| pk_m_user_id            | id            | Primary key                                                                   |
| uq_m_user_username      | username      | Unique                                                                        |
| uq_m_user_email_address | email_address | Unique                                                                        |
| ck_m_user_row_status    | row_status    | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.m_user (
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
        username BYTEA NOT NULL UNIQUE,
        email_address BYTEA NOT NULL UNIQUE,
        first_name BYTEA,
        last_name BYTEA,
        display_name VARCHAR(128),
        profile_picture_path TEXT
    );
```
