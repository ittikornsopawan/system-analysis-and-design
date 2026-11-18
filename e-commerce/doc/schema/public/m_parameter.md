---
name: "Schema doc: public.m_parameter"
description: "Columns, keys, constraints and indexes of the table public.m_parameter. Master table of the `public` schema (defined in `db/migrations/up/00-common.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: public.m_parameter

Description: Master table of the `public` schema (defined in `db/migrations/up/00-common.schema.up.sql`). Holds reusable reference (master) data as key and value pairs in a parent/child hierarchy through `parent_id`, for example country > province > district > subdistrict > postal code, for other tables and APIs to reuse.

## Columns

| Key | Reference                               | Column Name  | Data Type | Length | Is Nullable | Description                                                              | Example              |
| --- | --------------------------------------- | ------------ | --------- | ------ | ----------- | ------------------------------------------------------------------------ | -------------------- |
| PK  |                                         | id           | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid()    |
|     |                                         | created_by   | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                      |
|     |                                         | created_at   | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                      |
|     |                                         | updated_by   | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                      |
|     |                                         | updated_at   | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                      |
|     |                                         | row_status   | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE               |
|     |                                         | effective_at | TIMESTAMP |        | FALSE       | Defaults to `now()`                                                      |                      |
|     |                                         | expired_at   | TIMESTAMP |        | TRUE        |                                                                          |                      |
| FK  | [public.m_parameter.id](m_parameter.md) | parent_id    | UUID      |        | TRUE        | Reference to `public.m_parameter.id` (optional), the parent parameter    |                      |
|     |                                         | key          | VARCHAR   | 128    | FALSE       | Unique among rows where row_status <> 'DELETED'                          |                      |
|     |                                         | value        | JSONB     |        | FALSE       | Localized text keyed by language code                                    | {"en": "", "th": ""} |
|     |                                         | title        | JSONB     |        | TRUE        | Localized text keyed by language code                                    | {"en": "", "th": ""} |
|     |                                         | display      | JSONB     |        | TRUE        | Localized text keyed by language code                                    | {"en": "", "th": ""} |
|     |                                         | metadata     | JSONB     |        | TRUE        |                                                                          |                      |

## Constain

| Key Name                  | Column Name | Description                                                                             |
| ------------------------- | ----------- | --------------------------------------------------------------------------------------- |
| pk_m_parameter_id         | id          | Primary key                                                                             |
| fk_m_parameter_parent_id  | parent_id   | References public.m_parameter(id), ON DELETE RESTRICT                                   |
| uq_m_parameter_key        | key         | Unique among rows where row_status <> 'DELETED'                                         |
| ix_m_parameter_parent_id  | parent_id   | Index to list the children of a parent and to check children before a delete or archive |
| ck_m_parameter_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))           |

---

```SQL
CREATE TABLE
    IF NOT EXISTS public.m_parameter (
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
        effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        expired_at TIMESTAMP WITHOUT TIME ZONE,
        parent_id UUID REFERENCES public.m_parameter (id) ON DELETE RESTRICT,
        key VARCHAR(128) NOT NULL,
        value JSONB NOT NULL,
        title JSONB,
        display JSONB,
        metadata JSONB
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_parameter_key ON public.m_parameter (key)
WHERE
    row_status <> 'DELETED';

CREATE INDEX IF NOT EXISTS ix_m_parameter_parent_id ON public.m_parameter (parent_id);
```
