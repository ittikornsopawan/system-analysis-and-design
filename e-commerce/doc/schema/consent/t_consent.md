# Table: consent.t_consent

Description: Transaction table of the `consent` schema (defined in `db/migrations/up/00-common.schema.up.sql`).

## Columns

| Key | Reference                                      | Column Name         | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ---------------------------------------------- | ------------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                | id                  | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| UQ  |                                                | code                | VARCHAR   | 64     | FALSE       | Unique                                                                   |                   |
| FK  | [consent.m_consent_type.id](m_consent_type.md) | consent_type_id     | UUID      |        | FALSE       | Reference to `consent.m_consent_type.id`                                 |                   |
|     |                                                | consent_version     | VARCHAR   | 8      | FALSE       | Defaults to `'1.0.0'`                                                    | 1.0.0             |
|     |                                                | consent_name        | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                                                | consent_description | TEXT      |        | TRUE        |                                                                          |                   |
|     |                                                | effective_at        | TIMESTAMP |        | FALSE       | Defaults to `now()`                                                      |                   |
|     |                                                | expired_at          | TIMESTAMP |        | TRUE        |                                                                          |                   |
|     |                                                | is_required         | BOOLEAN   |        | FALSE       | Defaults to `FALSE`                                                      | FALSE             |
|     |                                                | body                | JSONB     |        | FALSE       |                                                                          |                   |

## Constain

| Key Name                     | Column Name     | Description                                                                   |
| ---------------------------- | --------------- | ----------------------------------------------------------------------------- |
| pk_t_consent_id              | id              | Primary key                                                                   |
| fk_t_consent_consent_type_id | consent_type_id | References consent.m_consent_type(id), ON DELETE RESTRICT                     |
| uq_t_consent_code            | code            | Unique                                                                        |
| ck_t_consent_row_status      | row_status      | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS consent.t_consent (
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
        code VARCHAR(64) NOT NULL UNIQUE,
        consent_type_id UUID NOT NULL REFERENCES consent.m_consent_type (id) ON DELETE RESTRICT,
        consent_version VARCHAR(8) NOT NULL DEFAULT '1.0.0',
        consent_name VARCHAR(128) NOT NULL,
        consent_description TEXT,
        effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        expired_at TIMESTAMP WITHOUT TIME ZONE,
        is_required BOOLEAN NOT NULL DEFAULT FALSE,
        body JSONB NOT NULL
    );
```
