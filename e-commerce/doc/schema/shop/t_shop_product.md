# Table: shop.t_shop_product

Description: Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                                       | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ----------------------------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                 | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                 | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                 | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                 | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                 | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                 | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shop.m_shop.id](m_shop.md)                     | shop_id     | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                            |                   |
| FK  | [product.m_product.id](../product/m_product.md) | product_id  | UUID      |        | FALSE       | Reference to `product.m_product.id`                                      |                   |
|     |                                                 | quantity    | INT       |        | FALSE       | Must satisfy `quantity >= 0`. Defaults to `0`                            | 0                 |

## Constain

| Key Name                             | Column Name         | Description                                                                   |
| ------------------------------------ | ------------------- | ----------------------------------------------------------------------------- |
| pk_t_shop_product_id                 | id                  | Primary key                                                                   |
| fk_t_shop_product_shop_id            | shop_id             | References shop.m_shop(id), ON DELETE CASCADE                                 |
| fk_t_shop_product_product_id         | product_id          | References product.m_product(id), ON DELETE CASCADE                           |
| uq_t_shop_product_shop_id_product_id | shop_id, product_id | Unique combination                                                            |
| ck_t_shop_product_row_status         | row_status          | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_t_shop_product_quantity           | quantity            | CHECK (quantity >= 0)                                                         |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shop.t_shop_product (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
        UNIQUE (shop_id, product_id)
    );
```
