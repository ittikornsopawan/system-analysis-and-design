---
name: "Schema doc: shop.t_shop_product_sku"
description: "Columns, keys, constraints and indexes of the table shop.t_shop_product_sku. Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: shop.t_shop_product_sku

Description: Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                                               | Column Name     | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ------------------------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                         | id              | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                         | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                         | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                         | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                         | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                         | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shop.t_shop_product.id](t_shop_product.md)             | shop_product_id | UUID      |        | FALSE       | Reference to `shop.t_shop_product.id`                                    |                   |
| FK  | [product.m_product_sku.id](../product/m_product_sku.md) | sku_id          | UUID      |        | FALSE       | Reference to `product.m_product_sku.id`                                  |                   |
|     |                                                         | code            | VARCHAR   | 64     | FALSE       |                                                                          |                   |
|     |                                                         | name            | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                                                         | description     | VARCHAR   | 256    | FALSE       |                                                                          |                   |

## Constain

| Key Name                                     | Column Name             | Description                                                                   |
| -------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------- |
| pk_t_shop_product_sku_id                     | id                      | Primary key                                                                   |
| fk_t_shop_product_sku_shop_product_id        | shop_product_id         | References shop.t_shop_product(id), ON DELETE CASCADE                         |
| fk_t_shop_product_sku_sku_id                 | sku_id                  | References product.m_product_sku(id), ON DELETE CASCADE                       |
| uq_t_shop_product_sku_shop_product_id_sku_id | shop_product_id, sku_id | Unique combination                                                            |
| ck_t_shop_product_sku_row_status             | row_status              | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shop.t_shop_product_sku (
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
        shop_product_id UUID NOT NULL REFERENCES shop.t_shop_product (id) ON DELETE CASCADE,
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        code VARCHAR(64) NOT NULL,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        UNIQUE (shop_product_id, sku_id)
    );
```
