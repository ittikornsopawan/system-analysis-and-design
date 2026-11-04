# Table: campaign.m_campaign_budget

Description: Master table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [campaign.m_campaign.id](m_campaign.md) | campaign_id | UUID      |        | FALSE       | Reference to `campaign.m_campaign.id`                                    |                   |
|     |                                         | budget      | NUMERIC   | 16,2   | FALSE       | Must satisfy `budget >= 0`                                               |                   |

## Constain

| Key Name                         | Column Name | Description                                                                   |
| -------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| pk_m_campaign_budget_id          | id          | Primary key                                                                   |
| fk_m_campaign_budget_campaign_id | campaign_id | References campaign.m_campaign(id), ON DELETE CASCADE                         |
| ck_m_campaign_budget_row_status  | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_m_campaign_budget_budget      | budget      | CHECK (budget >= 0)                                                           |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.m_campaign_budget (
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
        budget NUMERIC(16, 2) NOT NULL CHECK (budget >= 0)
    );
```
