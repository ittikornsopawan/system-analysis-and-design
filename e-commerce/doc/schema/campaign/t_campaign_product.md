# Table: campaign.t_campaign_product

Description: Transaction table of the `campaign` schema (defined in `db/migrations/up/09-campaign.schema.up.sql`).

## Columns

| Key | Reference                                                         | Column Name         | Data Type | Length | Is Nullable | Description                                                                                                                                              | Example           |
| --- | ----------------------------------------------------------------- | ------------------- | --------- | ------ | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                                                   | id                  | UUID      |        | FALSE       | Primary key                                                                                                                                              | gen_random_uuid() |
|     |                                                                   | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                                                     |                   |
|     |                                                                   | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                                                       |                   |
|     |                                                                   | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                                                                |                   |
|     |                                                                   | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                                                                  |                   |
|     |                                                                   | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                                                                 | ACTIVE            |
| FK  | [campaign.m_campaign.id](m_campaign.md)                           | campaign_id         | UUID      |        | FALSE       | Reference to `campaign.m_campaign.id`                                                                                                                    |                   |
| FK  | [product.m_product_category.id](../product/m_product_category.md) | product_category_id | UUID      |        | TRUE        | Reference to `product.m_product_category.id`. Exactly one of `product_category_id` and `product_id` is set (the category itself, not its sub categories) |                   |
| FK  | [product.m_product.id](../product/m_product.md)                   | product_id          | UUID      |        | TRUE        | Reference to `product.m_product.id`. Exactly one of `product_category_id` and `product_id` is set                                                        |                   |

## Constain

| Key Name                                              | Column Name                      | Description                                                                         |
| ----------------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------- |
| pk_t_campaign_product_id                              | id                               | Primary key                                                                         |
| fk_t_campaign_product_campaign_id                     | campaign_id                      | References campaign.m_campaign(id), ON DELETE CASCADE                               |
| fk_t_campaign_product_product_category_id             | product_category_id              | References product.m_product_category(id), ON DELETE CASCADE                        |
| fk_t_campaign_product_product_id                      | product_id                       | References product.m_product(id), ON DELETE CASCADE                                 |
| ck_t_campaign_product_row_status                      | row_status                       | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))       |
| ck_t_campaign_product_target                          | product_category_id, product_id  | CHECK ((product_category_id IS NULL) <> (product_id IS NULL))                       |
| uq_t_campaign_product_campaign_id_product_id          | campaign_id, product_id          | Unique among rows where row_status <> 'DELETED' and product_id is not null          |
| uq_t_campaign_product_campaign_id_product_category_id | campaign_id, product_category_id | Unique among rows where row_status <> 'DELETED' and product_category_id is not null |

---

```SQL
CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_product (
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
        product_category_id UUID REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        product_id UUID REFERENCES product.m_product (id) ON DELETE CASCADE,
        CONSTRAINT ck_t_campaign_product_target CHECK (
            (product_category_id IS NULL) <> (product_id IS NULL)
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_id ON campaign.t_campaign_product (campaign_id, product_id)
WHERE
    product_id IS NOT NULL
    AND row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_category_id ON campaign.t_campaign_product (campaign_id, product_category_id)
WHERE
    product_category_id IS NOT NULL
    AND row_status <> 'DELETED';
```
