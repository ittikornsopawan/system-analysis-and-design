# Table: shipping.t_shipping

Description: Transaction table of the `shipping` schema (defined in `db/migrations/up/08-shipping.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name     | Data Type | Length | Is Nullable | Description                                                                                                                                                   | Example           |
| --- | --------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                         | id              | UUID      |        | FALSE       | Primary key                                                                                                                                                   | gen_random_uuid() |
|     |                                         | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                                                          |                   |
|     |                                         | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                                                            |                   |
|     |                                         | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                                                                     |                   |
|     |                                         | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                                                                       |                   |
|     |                                         | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                                                                      | ACTIVE            |
| FK  | [sales.t_order.id](../sales/t_order.md) | order_id        | UUID      |        | FALSE       | Reference to `sales.t_order.id`                                                                                                                               |                   |
|     |                                         | shipping_method | VARCHAR   | 32     | FALSE       | One of: STANDARD, EXPRESS, SAME_DAY                                                                                                                           | STANDARD          |
|     |                                         | status          | VARCHAR   | 32     | FALSE       | One of: PENDING, SHIPPED, DELIVERED, CANCELLED, RETURNED                                                                                                      | PENDING           |
|     |                                         | carrier_name    | VARCHAR   | 64     | TRUE        | Carrier (shipping company) that holds the parcel. Required once the status is SHIPPED, DELIVERED or RETURNED                                                  | KERRY             |
|     |                                         | tracking_number | VARCHAR   | 64     | TRUE        | Tracking number given by the carrier. Required once the status is SHIPPED, DELIVERED or RETURNED. Unique per carrier among rows where row_status <> 'DELETED' | TH0123456789      |
|     |                                         | shipped_at      | TIMESTAMP |        | TRUE        | When the shop handed the parcel to the carrier. Required once the status is SHIPPED, DELIVERED or RETURNED                                                    |                   |
|     |                                         | delivered_at    | TIMESTAMP |        | TRUE        | When the receiver confirmed the parcel. Set exactly when the status is DELIVERED                                                                              |                   |

## Constain

| Key Name                                   | Column Name                                       | Description                                                                                                                                         |
| ------------------------------------------ | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| pk_t_shipping_id                           | id                                                | Primary key                                                                                                                                         |
| fk_t_shipping_order_id                     | order_id                                          | References sales.t_order(id), ON DELETE RESTRICT                                                                                                    |
| uq_t_shipping_carrier_name_tracking_number | carrier_name, tracking_number                     | Unique among rows where row_status <> 'DELETED' and tracking_number is not null                                                                     |
| ix_t_shipping_shipped_at                   | shipped_at                                        | Index (not unique) on rows where status = 'SHIPPED' and row_status <> 'DELETED', for the job that finds the parcels shipped long ago (S26, S31)     |
| ck_t_shipping_row_status                   | row_status                                        | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                                                                       |
| ck_t_shipping_shipping_method              | shipping_method                                   | CHECK (shipping_method IN ('STANDARD', 'EXPRESS', 'SAME_DAY'))                                                                                      |
| ck_t_shipping_shipped_has_tracking         | status, carrier_name, tracking_number, shipped_at | CHECK (status NOT IN ('SHIPPED', 'DELIVERED', 'RETURNED') OR (carrier_name IS NOT NULL AND tracking_number IS NOT NULL AND shipped_at IS NOT NULL)) |
| ck_t_shipping_delivered_at                 | status, delivered_at                              | CHECK ((status = 'DELIVERED') = (delivered_at IS NOT NULL))                                                                                         |
| ck_t_shipping_status                       | status                                            | CHECK (status IN ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED'))                                                                      |

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
        order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT,
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
        carrier_name VARCHAR(64),
        tracking_number VARCHAR(64),
        shipped_at TIMESTAMP WITHOUT TIME ZONE,
        delivered_at TIMESTAMP WITHOUT TIME ZONE,
        CONSTRAINT ck_t_shipping_shipped_has_tracking CHECK (
            status NOT IN ('SHIPPED', 'DELIVERED', 'RETURNED')
            OR (
                carrier_name IS NOT NULL
                AND tracking_number IS NOT NULL
                AND shipped_at IS NOT NULL
            )
        ),
        CONSTRAINT ck_t_shipping_delivered_at CHECK (
            (status = 'DELIVERED') = (delivered_at IS NOT NULL)
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_carrier_name_tracking_number ON shipping.t_shipping (carrier_name, tracking_number)
WHERE
    tracking_number IS NOT NULL
    AND row_status <> 'DELETED';

CREATE INDEX IF NOT EXISTS ix_t_shipping_shipped_at ON shipping.t_shipping (shipped_at)
WHERE
    status = 'SHIPPED'
    AND row_status <> 'DELETED';
```
