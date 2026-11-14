---
name: "Schema doc: authen.l_user_login_attempt"
description: "Columns, keys, constraints and indexes of the table authen.l_user_login_attempt. Log table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: authen.l_user_login_attempt

Description: Log table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                     | Column Name     | Data Type | Length | Is Nullable | Description                                                                                                                                                                                                                                | Example           |
| --- | ----------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| PK  |                               | id              | UUID      |        | FALSE       | Primary key                                                                                                                                                                                                                                | gen_random_uuid() |
|     |                               | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                                                                                                                                       |                   |
|     |                               | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                                                                                                                                         |                   |
|     |                               | identifier_hash | BYTEA     |        | FALSE       | SHA-256 of the username that was sent to login, also for names that do not exist                                                                                                                                                           |                   |
| FK  | [authen.m_user.id](m_user.md) | user_id         | UUID      |        | TRUE        | Reference to `authen.m_user.id`, NULL when the username does not exist                                                                                                                                                                     |                   |
|     |                               | result          | VARCHAR   | 16     | FALSE       | SUCCESS: the login was accepted, FAILED: the password was checked and was wrong (or the user was not found or not ACTIVE), REFUSED: the username was blocked and the password was not checked (only FAILED rows are counted for the block) |                   |

## Constain

| Key Name                                           | Column Name                 | Description                                                         |
| -------------------------------------------------- | --------------------------- | ------------------------------------------------------------------- |
| pk_l_user_login_attempt_id                         | id                          | Primary key                                                         |
| fk_l_user_login_attempt_user_id                    | user_id                     | References authen.m_user(id), ON DELETE CASCADE                     |
| ck_l_user_login_attempt_result                     | result                      | CHECK (result IN ('SUCCESS', 'FAILED', 'REFUSED'))                  |
| ix_l_user_login_attempt_identifier_hash_created_at | identifier_hash, created_at | Index to count the failed attempts of one username in a time window |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.l_user_login_attempt (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        identifier_hash BYTEA NOT NULL,
        user_id UUID REFERENCES authen.m_user (id) ON DELETE CASCADE,
        result VARCHAR(16) NOT NULL CHECK (result IN ('SUCCESS', 'FAILED', 'REFUSED'))
    );

CREATE INDEX IF NOT EXISTS ix_l_user_login_attempt_identifier_hash_created_at ON authen.l_user_login_attempt (identifier_hash, created_at);
```
