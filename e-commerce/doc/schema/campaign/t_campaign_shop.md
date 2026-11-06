# Table: campaign.t_campaign_shop

Description: Transaction table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

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
| FK  | [shop.m_shop.id](../shop/m_shop.md)     | shop_id     | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                            |                   |

## Constain

| Key Name                               | Column Name          | Description                                                                    |
| -------------------------------------- | -------------------- | ------------------------------------------------------------------------------ |
| pk_t_campaign_shop_id                  | id                   | Primary key                                                                    |
| fk_t_campaign_shop_campaign_id         | campaign_id          | References campaign.m_campaign(id), ON DELETE CASCADE                          |
| fk_t_campaign_shop_shop_id             | shop_id              | References shop.m_shop(id), ON DELETE CASCADE                                  |
| ck_t_campaign_shop_row_status          | row_status           | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))  |
| uq_t_campaign_shop_campaign_id_shop_id | campaign_id, shop_id | Unique among rows where row_status <> 'DELETED' (a shop joins a campaign once) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_shop (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_shop_campaign_id_shop_id ON campaign.t_campaign_shop (campaign_id, shop_id)
WHERE
    row_status <> 'DELETED';
```
