# Table: sales.t_order_item

Description: Transaction table of the `sales` schema (defined in `db/migrations/up/06-sales.schema.up.sql`).

## Columns

| Key | Reference                                                           | Column Name     | Data Type | Length | Is Nullable | Description                                                                                                          | Example           |
| --- | ------------------------------------------------------------------- | --------------- | --------- | ------ | ----------- | -------------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                                                     | id              | UUID      |        | FALSE       | Primary key                                                                                                          | gen_random_uuid() |
|     |                                                                     | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                 |                   |
|     |                                                                     | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                   |                   |
|     |                                                                     | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                            |                   |
|     |                                                                     | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                              |                   |
|     |                                                                     | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                             | ACTIVE            |
| FK  | [sales.t_order.id](t_order.md)                                      | order_id        | UUID      |        | FALSE       | Reference to `sales.t_order.id`                                                                                      |                   |
| FK  | [shop.m_shop.id](../shop/m_shop.md)                                 | shop_id         | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                                                                        |                   |
| FK  | [product.m_product.id](../product/m_product.md)                     | product_id      | UUID      |        | FALSE       | Reference to `product.m_product.id`                                                                                  |                   |
| FK  | [product.m_product_sku.id](../product/m_product_sku.md)             | sku_id          | UUID      |        | FALSE       | Reference to `product.m_product_sku.id`, Every product has at least one SKU (the default SKU when it has no level)   |                   |
|     |                                                                     | quantity        | INT       |        | FALSE       | Must satisfy `quantity > 0`. Defaults to `1`                                                                         | 1                 |
|     |                                                                     | price           | NUMERIC   | 16,2   | FALSE       | Must satisfy `price >= 0`                                                                                            |                   |
|     |                                                                     | discount        | NUMERIC   | 16,2   | FALSE       | Must satisfy `discount >= 0`                                                                                         |                   |
|     |                                                                     | total_price     | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_price >= 0 AND total_price = price * quantity`                                                   |                   |
|     |                                                                     | gross_profit    | NUMERIC   | 16,2   | FALSE       | Must satisfy `gross_profit >= 0`                                                                                     |                   |
|     |                                                                     | shop_profit     | NUMERIC   | 16,2   | TRUE        |                                                                                                                      |                   |
|     |                                                                     | platform_profit | NUMERIC   | 16,2   | TRUE        |                                                                                                                      |                   |
| FK  | [shop.t_shop_product_sku_lot.id](../shop/t_shop_product_sku_lot.md) | lot_id          | UUID      |        | FALSE       | Reference to `shop.t_shop_product_sku_lot.id`, Lot that the item was sold from, The cost of the lot gives the profit |                   |

## Constain

| Key Name                                   | Column Name                  | Description                                                                   |
| ------------------------------------------ | ---------------------------- | ----------------------------------------------------------------------------- |
| pk_t_order_item_id                         | id                           | Primary key                                                                   |
| fk_t_order_item_order_id                   | order_id                     | References sales.t_order(id), ON DELETE CASCADE                               |
| fk_t_order_item_shop_id                    | shop_id                      | References shop.m_shop(id), ON DELETE CASCADE                                 |
| fk_t_order_item_product_id                 | product_id                   | References product.m_product(id), ON DELETE CASCADE                           |
| fk_t_order_item_sku_id                     | sku_id                       | References product.m_product_sku(id), ON DELETE CASCADE                       |
| fk_t_order_item_lot_id                     | lot_id                       | References shop.t_shop_product_sku_lot(id), ON DELETE RESTRICT                |
| uq_t_order_item_order_id_product_id_sku_id | order_id, product_id, sku_id | Unique combination                                                            |
| ck_t_order_item_row_status                 | row_status                   | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_t_order_item_quantity                   | quantity                     | CHECK (quantity > 0)                                                          |
| ck_t_order_item_price                      | price                        | CHECK (price >= 0)                                                            |
| ck_t_order_item_discount                   | discount                     | CHECK (discount >= 0)                                                         |
| ck_t_order_item_total_price                | total_price                  | CHECK (total_price >= 0 AND total_price = price * quantity)                   |
| ck_t_order_item_gross_profit               | gross_profit                 | CHECK (gross_profit >= 0)                                                     |

---

```SQL
CREATE TABLE
    IF NOT EXISTS sales.t_order_item (
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
        order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE CASCADE,
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
        price NUMERIC(16, 2) NOT NULL CHECK (price >= 0),
        discount NUMERIC(16, 2) NOT NULL CHECK (discount >= 0),
        total_price NUMERIC(16, 2) NOT NULL CHECK (
            total_price >= 0
            AND total_price = price * quantity
        ),
        gross_profit NUMERIC(16, 2) NOT NULL CHECK (gross_profit >= 0),
        shop_profit NUMERIC(16, 2),
        platform_profit NUMERIC(16, 2),
        lot_id UUID NOT NULL REFERENCES shop.t_shop_product_sku_lot (id) ON DELETE RESTRICT,
        UNIQUE (order_id, product_id, sku_id)
    );
```
