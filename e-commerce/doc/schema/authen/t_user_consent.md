# Table: authen.t_user_consent

Description: Transaction table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                                       | Column Name     | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ----------------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                 | id              | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                 | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                 | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                 | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                 | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                 | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [authen.m_user.id](m_user.md)                   | user_id         | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
| FK  | [consent.t_consent.id](../consent/t_consent.md) | consent_id      | UUID      |        | FALSE       | Reference to `consent.t_consent.id`                                      |                   |
|     |                                                 | consent_version | VARCHAR   | 8      | FALSE       | Defaults to `'1.0.0'`                                                    | 1.0.0             |
|     |                                                 | result          | BOOLEAN   |        | FALSE       | Defaults to `FALSE`                                                      | FALSE             |
|     |                                                 | is_read         | BOOLEAN   |        | FALSE       | Defaults to `FALSE`                                                      | FALSE             |
|     |                                                 | read_at         | TIMESTAMP |        | TRUE        | Timestamp when the user read the consent                                 |                   |

## Constain

| Key Name                     | Column Name | Description                                                                   |
| ---------------------------- | ----------- | ----------------------------------------------------------------------------- |
| pk_t_user_consent_id         | id          | Primary key                                                                   |
| fk_t_user_consent_user_id    | user_id     | References authen.m_user(id), ON DELETE CASCADE                               |
| fk_t_user_consent_consent_id | consent_id  | References consent.t_consent(id), ON DELETE CASCADE                           |
| ck_t_user_consent_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.t_user_consent (
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
        consent_id UUID NOT NULL REFERENCES consent.t_consent (id) ON DELETE CASCADE,
        consent_version VARCHAR(8) NOT NULL DEFAULT '1.0.0',
        result BOOLEAN NOT NULL DEFAULT FALSE,
        is_read BOOLEAN NOT NULL DEFAULT FALSE,
        read_at TIMESTAMP WITHOUT TIME ZONE
    );
```
