---
name: "Schema doc: cart.t_cart"
description: "Columns, keys, constraints and indexes of the table cart.t_cart. Transaction table of the `cart` schema (defined in `db/migrations/up/05-cart.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: cart.t_cart

Description: Transaction table of the `cart` schema (defined in `db/migrations/up/05-cart.schema.up.sql`).

## Columns

| Key | Reference                                               | Column Name | Data Type | Length | Is Nullable | Description                                                                                                        | Example           |
| --- | ------------------------------------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------ | ----------------- |
| PK  |                                                         | id          | UUID      |        | FALSE       | Primary key                                                                                                        | gen_random_uuid() |
|     |                                                         | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                               |                   |
|     |                                                         | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                 |                   |
|     |                                                         | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                          |                   |
|     |                                                         | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                            |                   |
|     |                                                         | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                           | ACTIVE            |
| FK  | [authen.m_user.id](../authen/m_user.md)                 | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                                                                    |                   |
| FK  | [shop.m_shop.id](../shop/m_shop.md)                     | shop_id     | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                                                                      |                   |
| FK  | [product.m_product.id](../product/m_product.md)         | product_id  | UUID      |        | FALSE       | Reference to `product.m_product.id`                                                                                |                   |
| FK  | [product.m_product_sku.id](../product/m_product_sku.md) | sku_id      | UUID      |        | FALSE       | Reference to `product.m_product_sku.id`, Every product has at least one SKU (the default SKU when it has no level) |                   |
|     |                                                         | quantity    | INT       |        | FALSE       | Must satisfy `quantity > 0`. Defaults to `1`                                                                       | 1                 |

## Constain

| Key Name                                    | Column Name                          | Description                                                                   |
| ------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------- |
| pk_t_cart_id                                | id                                   | Primary key                                                                   |
| fk_t_cart_user_id                           | user_id                              | References authen.m_user(id), ON DELETE CASCADE                               |
| fk_t_cart_shop_id                           | shop_id                              | References shop.m_shop(id), ON DELETE CASCADE                                 |
| fk_t_cart_product_id                        | product_id                           | References product.m_product(id), ON DELETE CASCADE                           |
| fk_t_cart_sku_id                            | sku_id                               | References product.m_product_sku(id), ON DELETE CASCADE                       |
| uq_t_cart_user_id_shop_id_product_id_sku_id | user_id, shop_id, product_id, sku_id | Unique among rows where row_status <> 'DELETED'                               |
| ck_t_cart_row_status                        | row_status                           | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_t_cart_quantity                          | quantity                             | CHECK (quantity > 0)                                                          |

---

```SQL
CREATE TABLE
    IF NOT EXISTS cart.t_cart (
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
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_cart_user_id_shop_id_product_id_sku_id ON cart.t_cart (user_id, shop_id, product_id, sku_id)
WHERE
    row_status <> 'DELETED';
```
