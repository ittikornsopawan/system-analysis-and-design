---
name: "Schema doc: public.t_parameter"
description: "Columns, keys, constraints and indexes of the table public.t_parameter. Transaction table of the `public` schema (defined in `db/migrations/up/00-common.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: public.t_parameter

Description: Transaction table of the `public` schema (defined in `db/migrations/up/00-common.schema.up.sql`). Holds system parameters as key and value pairs; a parameter can group child parameters through `parent_id`.

## Columns

| Key | Reference                               | Column Name  | Data Type | Length | Is Nullable | Description                                                                       | Example              |
| --- | --------------------------------------- | ------------ | --------- | ------ | ----------- | --------------------------------------------------------------------------------- | -------------------- |
| PK  |                                         | id           | UUID      |        | FALSE       | Primary key                                                                       | gen_random_uuid()    |
|     |                                         | created_by   | VARCHAR   | 64     | FALSE       | User or service that created the row                                              |                      |
|     |                                         | created_at   | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                |                      |
|     |                                         | updated_by   | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                         |                      |
|     |                                         | updated_at   | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                           |                      |
|     |                                         | row_status   | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED, EXPIRED | ACTIVE               |
|     |                                         | effective_at | TIMESTAMP |        | FALSE       | Defaults to `now()`                                                               |                      |
|     |                                         | expired_at   | TIMESTAMP |        | TRUE        |                                                                                   |                      |
| FK  | [public.t_parameter.id](t_parameter.md) | parent_id    | UUID      |        | TRUE        | Reference to `public.t_parameter.id` (optional), the parent parameter             |                      |
| UQ  |                                         | key          | VARCHAR   | 128    | FALSE       | Unique                                                                            |                      |
|     |                                         | value        | JSONB     |        | FALSE       | Localized text keyed by language code                                             | {"en": "", "th": ""} |
|     |                                         | title        | JSONB     |        | TRUE        | Localized text keyed by language code                                             | {"en": "", "th": ""} |
|     |                                         | display      | JSONB     |        | TRUE        | Localized text keyed by language code                                             | {"en": "", "th": ""} |
|     |                                         | metadata     | JSONB     |        | TRUE        |                                                                                   |                      |

## Constain

| Key Name                  | Column Name | Description                                                                              |
| ------------------------- | ----------- | ---------------------------------------------------------------------------------------- |
| pk_t_parameter_id         | id          | Primary key                                                                              |
| fk_t_parameter_parent_id  | parent_id   | References public.t_parameter(id), ON DELETE RESTRICT                                    |
| uq_t_parameter_key        | key         | Unique                                                                                   |
| ck_t_parameter_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED', 'EXPIRED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS public.t_parameter (
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
                'ARCHIVED',
                'EXPIRED'
            )
        ),
        effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        expired_at TIMESTAMP WITHOUT TIME ZONE,
        parent_id UUID REFERENCES public.t_parameter (id) ON DELETE RESTRICT,
        key VARCHAR(128) NOT NULL UNIQUE,
        value JSONB NOT NULL,
        title JSONB,
        display JSONB,
        metadata JSONB
    );
```
