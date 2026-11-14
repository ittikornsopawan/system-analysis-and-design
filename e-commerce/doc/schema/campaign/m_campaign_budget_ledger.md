---
name: "Schema doc: campaign.m_campaign_budget_ledger"
description: "Columns, keys, constraints and indexes of the table campaign.m_campaign_budget_ledger. Master table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: campaign.m_campaign_budget_ledger

Description: Master table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

## Columns

| Key | Reference                                             | Column Name        | Data Type | Length | Is Nullable | Description                                                                             | Example           |
| --- | ----------------------------------------------------- | ------------------ | --------- | ------ | ----------- | --------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                                       | id                 | UUID      |        | FALSE       | Primary key                                                                             | gen_random_uuid() |
|     |                                                       | created_by         | VARCHAR   | 64     | FALSE       | User or service that created the row                                                    |                   |
|     |                                                       | created_at         | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                      |                   |
|     |                                                       | updated_by         | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                               |                   |
|     |                                                       | updated_at         | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                 |                   |
|     |                                                       | row_status         | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                | ACTIVE            |
| FK  | [campaign.m_campaign_budget.id](m_campaign_budget.md) | campaign_budget_id | UUID      |        | FALSE       | Reference to `campaign.m_campaign_budget.id`                                            |                   |
| FK  | [campaign.m_campaign.id](m_campaign.md)               | campaign_id        | UUID      |        | FALSE       | Reference to `campaign.m_campaign.id`                                                   |                   |
| FK  | [sales.t_order.id](../sales/t_order.md)               | order_id           | UUID      |        | FALSE       | Reference to `sales.t_order.id`, the order that reserved or released the budget         |                   |
|     |                                                       | entry_type         | VARCHAR   | 16     | FALSE       | One of: RESERVE (the order took the budget), RELEASE (the budget went back)             | RESERVE           |
|     |                                                       | reference          | JSONB     |        | FALSE       |                                                                                         |                   |
|     |                                                       | usage              | NUMERIC   | 16,2   | FALSE       | Amount of the entry, always positive for RESERVE and RELEASE. Must satisfy `usage >= 0` |                   |
|     |                                                       | remaining          | NUMERIC   | 16,2   | FALSE       | Remaining amount of the budget after this entry. Must satisfy `remaining >= 0`          |                   |

## Constain

| Key Name                                                           | Column Name                              | Description                                                                   |
| ------------------------------------------------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------- |
| pk_m_campaign_budget_ledger_id                                     | id                                       | Primary key                                                                   |
| fk_m_campaign_budget_ledger_campaign_budget_id                     | campaign_budget_id                       | References campaign.m_campaign_budget(id), ON DELETE CASCADE                  |
| fk_m_campaign_budget_ledger_campaign_id                            | campaign_id                              | References campaign.m_campaign(id), ON DELETE CASCADE                         |
| fk_m_campaign_budget_ledger_order_id                               | order_id                                 | References sales.t_order(id), ON DELETE RESTRICT                              |
| ck_m_campaign_budget_ledger_row_status                             | row_status                               | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_m_campaign_budget_ledger_entry_type                             | entry_type                               | CHECK (entry_type IN ('RESERVE', 'RELEASE'))                                  |
| ck_m_campaign_budget_ledger_usage                                  | usage                                    | CHECK (usage >= 0)                                                            |
| ck_m_campaign_budget_ledger_remaining                              | remaining                                | CHECK (remaining >= 0)                                                        |
| uq_m_campaign_budget_ledger_campaign_budget_id_order_id_entry_type | campaign_budget_id, order_id, entry_type | Unique combination (an order reserves and releases a budget once each)        |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.m_campaign_budget_ledger (
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
        campaign_budget_id UUID NOT NULL REFERENCES campaign.m_campaign_budget (id) ON DELETE CASCADE,
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT,
        entry_type VARCHAR(16) NOT NULL CHECK (entry_type IN ('RESERVE', 'RELEASE')),
        reference JSONB NOT NULL,
        usage NUMERIC(16, 2) NOT NULL CHECK (usage >= 0),
        remaining NUMERIC(16, 2) NOT NULL CHECK (remaining >= 0),
        UNIQUE (campaign_budget_id, order_id, entry_type)
    );
```
