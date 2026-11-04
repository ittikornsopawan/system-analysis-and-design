# Table: shipping.t_shipping_item

Description: Transaction table of the `shipping` schema (defined in `db/migrations/up/08-shipping.schema.up.sql`).

## Columns

| Key | Reference                                         | Column Name   | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ------------------------------------------------- | ------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                   | id            | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                   | created_by    | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                   | created_at    | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                   | updated_by    | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                   | updated_at    | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                   | row_status    | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shipping.t_shipping.id](t_shipping.md)           | shipping_id   | UUID      |        | FALSE       | Reference to `shipping.t_shipping.id`                                    |                   |
| FK  | [order.t_order_item.id](../order/t_order_item.md) | order_item_id | UUID      |        | FALSE       | Reference to `order.t_order_item.id`                                     |                   |
|     |                                                   | quantity      | INT       |        | FALSE       | Must satisfy `quantity > 0`. Defaults to `1`                             | 1                 |

## Constain

| Key Name                         | Column Name   | Description                                                                   |
| -------------------------------- | ------------- | ----------------------------------------------------------------------------- |
| pk_t_shipping_item_id            | id            | Primary key                                                                   |
| fk_t_shipping_item_shipping_id   | shipping_id   | References shipping.t_shipping(id), ON DELETE CASCADE                         |
| fk_t_shipping_item_order_item_id | order_item_id | References order.t_order_item(id), ON DELETE CASCADE                          |
| ck_t_shipping_item_row_status    | row_status    | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_t_shipping_item_quantity      | quantity      | CHECK (quantity > 0)                                                          |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shipping.t_shipping_item (
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
        shipping_id UUID NOT NULL REFERENCES shipping.t_shipping (id) ON DELETE CASCADE,
        order_item_id UUID NOT NULL REFERENCES order.t_order_item (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0)
    );
```
