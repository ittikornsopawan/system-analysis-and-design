# Table: shipping.t_shipping

Description: Transaction table of the `shipping` schema (defined in `db/migrations/up/08-shipping.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name     | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id              | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [order.t_order.id](../order/t_order.md) | order_id        | UUID      |        | FALSE       | Reference to `order.t_order.id`                                          |                   |
|     |                                         | shipping_method | VARCHAR   | 32     | FALSE       | One of: STANDARD, EXPRESS, SAME_DAY                                      | STANDARD          |
|     |                                         | status          | VARCHAR   | 32     | FALSE       | One of: PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED                 | PENDING           |
| UQ  |                                         | tracking_number | VARCHAR   | 64     | TRUE        | Unique                                                                   |                   |
|     |                                         | shipped_at      | TIMESTAMP |        | TRUE        |                                                                          |                   |
|     |                                         | delivered_at    | TIMESTAMP |        | TRUE        |                                                                          |                   |

## Constain

| Key Name                      | Column Name     | Description                                                                    |
| ----------------------------- | --------------- | ------------------------------------------------------------------------------ |
| pk_t_shipping_id              | id              | Primary key                                                                    |
| fk_t_shipping_order_id        | order_id        | References order.t_order(id), ON DELETE CASCADE                                |
| uq_t_shipping_tracking_number | tracking_number | Unique                                                                         |
| ck_t_shipping_row_status      | row_status      | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))  |
| ck_t_shipping_shipping_method | shipping_method | CHECK (shipping_method IN ('STANDARD', 'EXPRESS', 'SAME_DAY'))                 |
| ck_t_shipping_status          | status          | CHECK (status IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shipping.t_shipping (
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
        order_id UUID NOT NULL REFERENCES order.t_order (id) ON DELETE CASCADE,
        shipping_method VARCHAR(32) NOT NULL CHECK (
            shipping_method IN ('STANDARD', 'EXPRESS', 'SAME_DAY')
        ),
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (
            status IN (
                'PENDING',
                'SHIPPED',
                'DELIVERED',
                'CANCELLED',
                'RETURNED'
            )
        ),
        tracking_number VARCHAR(64) UNIQUE,
        shipped_at TIMESTAMP WITHOUT TIME ZONE,
        delivered_at TIMESTAMP WITHOUT TIME ZONE
    );
```
