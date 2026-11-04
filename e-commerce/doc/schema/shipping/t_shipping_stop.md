# Table: shipping.t_shipping_stop

Description: Transaction table of the `shipping` schema (defined in `db/migrations/up/08-shipping.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name       | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | ----------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id                | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by        | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at        | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by        | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at        | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status        | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shipping.t_shipping.id](t_shipping.md) | shipping_id       | UUID      |        | FALSE       | Reference to `shipping.t_shipping.id`                                    |                   |
|     |                                         | stop_number       | INT       |        | FALSE       | Must satisfy `stop_number > 0`                                           |                   |
|     |                                         | stop_type         | VARCHAR   | 32     | FALSE       | One of: PICKUP, DROPOFF                                                  | PICKUP            |
|     |                                         | location_name     | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                                         | estimated_arrival | TIMESTAMP |        | TRUE        |                                                                          |                   |

## Constain

| Key Name                       | Column Name | Description                                                                   |
| ------------------------------ | ----------- | ----------------------------------------------------------------------------- |
| pk_t_shipping_stop_id          | id          | Primary key                                                                   |
| fk_t_shipping_stop_shipping_id | shipping_id | References shipping.t_shipping(id), ON DELETE CASCADE                         |
| ck_t_shipping_stop_row_status  | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_t_shipping_stop_stop_number | stop_number | CHECK (stop_number > 0)                                                       |
| ck_t_shipping_stop_stop_type   | stop_type   | CHECK (stop_type IN ('PICKUP', 'DROPOFF'))                                    |

---

```SQL
CREATE TABLE
    IF NOT EXISTS shipping.t_shipping_stop (
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
        stop_number INT NOT NULL CHECK (stop_number > 0),
        stop_type VARCHAR(32) NOT NULL CHECK (stop_type IN ('PICKUP', 'DROPOFF')),
        location_name VARCHAR(128) NOT NULL,
        estimated_arrival TIMESTAMP WITHOUT TIME ZONE
    );
```
