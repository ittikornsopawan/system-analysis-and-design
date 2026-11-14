---
name: "Schema doc: campaign.t_campaign_discount"
description: "Columns, keys, constraints and indexes of the table campaign.t_campaign_discount. Transaction table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: campaign.t_campaign_discount

Description: Transaction table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name    | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | -------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id             | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by     | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at     | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by     | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at     | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status     | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [campaign.m_campaign.id](m_campaign.md) | campaign_id    | UUID      |        | FALSE       | Reference to `campaign.m_campaign.id`                                    |                   |
|     |                                         | discount_type  | VARCHAR   | 32     | FALSE       | One of: PERCENTAGE, FIXED_AMOUNT                                         | PERCENTAGE        |
|     |                                         | discount_value | NUMERIC   | 16,2   | FALSE       | Must satisfy `discount_value > 0`. A PERCENTAGE value is at most 100     |                   |

## Constain

| Key Name                              | Column Name                   | Description                                                                      |
| ------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------- |
| pk_t_campaign_discount_id             | id                            | Primary key                                                                      |
| fk_t_campaign_discount_campaign_id    | campaign_id                   | References campaign.m_campaign(id), ON DELETE CASCADE                            |
| ck_t_campaign_discount_row_status     | row_status                    | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))    |
| ck_t_campaign_discount_discount_type  | discount_type                 | CHECK (discount_type IN ('PERCENTAGE', 'FIXED_AMOUNT'))                          |
| ck_t_campaign_discount_discount_value | discount_value                | CHECK (discount_value > 0)                                                       |
| ck_t_campaign_discount_percentage     | discount_type, discount_value | CHECK (discount_type <> 'PERCENTAGE' OR discount_value <= 100)                   |
| uq_t_campaign_discount_campaign_id    | campaign_id                   | Unique among rows where row_status <> 'DELETED' (one live discount per campaign) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_discount (
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
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        discount_type VARCHAR(32) NOT NULL CHECK (discount_type IN ('PERCENTAGE', 'FIXED_AMOUNT')),
        discount_value NUMERIC(16, 2) NOT NULL CHECK (discount_value > 0),
        CONSTRAINT ck_t_campaign_discount_percentage CHECK (
            discount_type <> 'PERCENTAGE'
            OR discount_value <= 100
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_discount_campaign_id ON campaign.t_campaign_discount (campaign_id)
WHERE
    row_status <> 'DELETED';
```
