---
name: "Schema doc: campaign.m_campaign"
description: "Columns, keys, constraints and indexes of the table campaign.m_campaign. Master table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: campaign.m_campaign

Description: Master table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

## Columns

| Key | Reference | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |           | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |           | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |           | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |           | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |           | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |           | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
|     |           | name        | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |           | description | TEXT      |        | TRUE        |                                                                          |                   |
|     |           | start_at    | TIMESTAMP |        | FALSE       |                                                                          |                   |
|     |           | end_at      | TIMESTAMP |        | FALSE       |                                                                          |                   |

## Constain

| Key Name                 | Column Name      | Description                                                                                               |
| ------------------------ | ---------------- | --------------------------------------------------------------------------------------------------------- |
| pk_m_campaign_id         | id               | Primary key                                                                                               |
| ck_m_campaign_row_status | row_status       | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                             |
| ck_m_campaign_period     | start_at, end_at | CHECK (end_at > start_at)                                                                                 |
| uq_m_campaign_name       | name             | Unique among rows where row_status <> 'DELETED' (campaign names are not reused while the campaign exists) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.m_campaign (
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
        name VARCHAR(128) NOT NULL,
        description TEXT,
        start_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        end_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        CONSTRAINT ck_m_campaign_period CHECK (end_at > start_at)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_campaign_name ON campaign.m_campaign (name)
WHERE
    row_status <> 'DELETED';
```
