# Table: shop.t_shop_product_sku_lot

Description: Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                                           | Column Name         | Data Type | Length | Is Nullable | Description                                                                           | Example           |
| --- | --------------------------------------------------- | ------------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                                     | id                  | UUID      |        | FALSE       | Primary key                                                                           | gen_random_uuid() |
|     |                                                     | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                                  |                   |
|     |                                                     | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                    |                   |
|     |                                                     | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                             |                   |
|     |                                                     | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                               |                   |
|     |                                                     | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED              | ACTIVE            |
| FK  | [shop.t_shop_product_sku.id](t_shop_product_sku.md) | shop_product_sku_id | UUID      |        | FALSE       | Reference to `shop.t_shop_product_sku.id`                                             |                   |
|     |                                                     | lot_no              | VARCHAR   | 64     | FALSE       | Lot number, Unique per shop product SKU among rows where row_status <> 'DELETED'      | LOT-2026-11-01    |
|     |                                                     | cost_price          | NUMERIC   | 16,2   | FALSE       | Cost price of the lot. Must satisfy `cost_price >= 0`                                 |                   |
|     |                                                     | selling_price       | NUMERIC   | 16,2   | FALSE       | Selling price of the lot. Must satisfy `selling_price >= 0`                           |                   |
|     |                                                     | gross_margin        | NUMERIC   | 16,2   | TRUE        | Calculated by the system                                                              |                   |
|     |                                                     | share_margin        | NUMERIC   | 16,2   | TRUE        | Calculated by the system                                                              |                   |
|     |                                                     | platform_margin     | NUMERIC   | 16,2   | TRUE        | Calculated by the system                                                              |                   |
|     |                                                     | quantity            | INT       |        | FALSE       | Remaining quantity of the lot. Must satisfy `quantity >= 0`. Defaults to `0`          | 0                 |
|     |                                                     | is_on_sale          | BOOLEAN   |        | FALSE       | The lot that is currently sold, At most one per shop product SKU. Defaults to `FALSE` | FALSE             |

## Constain

| Key Name                                             | Column Name                 | Description                                                                                         |
| ---------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------- |
| pk_t_shop_product_sku_lot_id                         | id                          | Primary key                                                                                         |
| fk_t_shop_product_sku_lot_shop_product_sku_id        | shop_product_sku_id         | References shop.t_shop_product_sku(id), ON DELETE CASCADE                                           |
| uq_t_shop_product_sku_lot_shop_product_sku_id_lot_no | shop_product_sku_id, lot_no | Unique among rows where row_status <> 'DELETED'                                                     |
| uq_t_shop_product_sku_lot_on_sale                    | shop_product_sku_id         | Unique among rows where is_on_sale AND row_status = 'ACTIVE' (one lot on sale per shop product SKU) |
| ck_t_shop_product_sku_lot_row_status                 | row_status                  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                       |
| ck_t_shop_product_sku_lot_cost_price                 | cost_price                  | CHECK (cost_price >= 0)                                                                             |
| ck_t_shop_product_sku_lot_selling_price              | selling_price               | CHECK (selling_price >= 0)                                                                          |
| ck_t_shop_product_sku_lot_quantity                   | quantity                    | CHECK (quantity >= 0)                                                                               |
| ck_t_shop_product_sku_lot_price_not_below_cost       | selling_price, cost_price   | CHECK (selling_price >= cost_price)                                                                 |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shop.t_shop_product_sku_lot (
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
        shop_product_sku_id UUID NOT NULL REFERENCES shop.t_shop_product_sku (id) ON DELETE CASCADE,
        lot_no VARCHAR(64) NOT NULL,
        cost_price NUMERIC(16, 2) NOT NULL CHECK (cost_price >= 0),
        selling_price NUMERIC(16, 2) NOT NULL CHECK (selling_price >= 0),
        gross_margin NUMERIC(16, 2),
        share_margin NUMERIC(16, 2),
        platform_margin NUMERIC(16, 2),
        quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
        is_on_sale BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT ck_t_shop_product_sku_lot_price_not_below_cost CHECK (selling_price >= cost_price)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_sku_lot_shop_product_sku_id_lot_no ON shop.t_shop_product_sku_lot (shop_product_sku_id, lot_no)
WHERE
    row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_sku_lot_on_sale ON shop.t_shop_product_sku_lot (shop_product_sku_id)
WHERE
    is_on_sale
    AND row_status = 'ACTIVE';
```
