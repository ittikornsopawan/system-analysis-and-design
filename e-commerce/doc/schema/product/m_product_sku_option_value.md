---
name: "Schema doc: product.m_product_sku_option_value"
description: "Columns, keys, constraints and indexes of the table product.m_product_sku_option_value. Master table of the `product` schema (defined in `db/migrations/up/03-product.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: product.m_product_sku_option_value

Description: Master table of the `product` schema (defined in `db/migrations/up/03-product.schema.up.sql`).

## Columns

| Key | Reference                                                      | Column Name     | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | -------------------------------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                                | id              | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                                | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                                | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                                | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                                | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                                | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [product.m_product_sku.id](m_product_sku.md)                   | sku_id          | UUID      |        | FALSE       | Reference to `product.m_product_sku.id`                                  |                   |
| FK  | [product.m_product_option_value.id](m_product_option_value.md) | option_value_id | UUID      |        | FALSE       | Reference to `product.m_product_option_value.id`                         |                   |

## Constain

| Key Name                                             | Column Name             | Description                                                                   |
| ---------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------- |
| pk_m_product_sku_option_value_id                     | id                      | Primary key                                                                   |
| fk_m_product_sku_option_value_sku_id                 | sku_id                  | References product.m_product_sku(id), ON DELETE CASCADE                       |
| fk_m_product_sku_option_value_option_value_id        | option_value_id         | References product.m_product_option_value(id), ON DELETE CASCADE              |
| uq_m_product_sku_option_value_sku_id_option_value_id | sku_id, option_value_id | Unique combination                                                            |
| ck_m_product_sku_option_value_row_status             | row_status              | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS product.m_product_sku_option_value (
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
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        option_value_id UUID NOT NULL REFERENCES product.m_product_option_value (id) ON DELETE CASCADE,
        UNIQUE (sku_id, option_value_id)
    );
```
