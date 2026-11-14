---
name: "Schema doc: sales.t_order"
description: "Columns, keys, constraints and indexes of the table sales.t_order. Transaction table of the `sales` schema (defined in `db/migrations/up/06-sales.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: sales.t_order

Description: Transaction table of the `sales` schema (defined in `db/migrations/up/06-sales.schema.up.sql`).

## Columns

| Key | Reference                                               | Column Name      | Data Type | Length | Is Nullable | Description                                                                                                                                                              | Example           |
| --- | ------------------------------------------------------- | ---------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| PK  |                                                         | id               | UUID      |        | FALSE       | Primary key                                                                                                                                                              | gen_random_uuid() |
|     |                                                         | created_by       | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                                                                     |                   |
|     |                                                         | created_at       | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                                                                       |                   |
|     |                                                         | updated_by       | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                                                                                |                   |
|     |                                                         | updated_at       | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                                                                                  |                   |
|     |                                                         | row_status       | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                                                                                 | ACTIVE            |
| FK  | [authen.m_user.id](../authen/m_user.md)                 | user_id          | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                                                                                                                          |                   |
| FK  | [shop.m_shop.id](../shop/m_shop.md)                     | shop_id          | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                                                                                                                            |                   |
| FK  | [authen.t_user_address.id](../authen/t_user_address.md) | address_id       | UUID      |        | FALSE       | Reference to `authen.t_user_address.id`                                                                                                                                  |                   |
|     |                                                         | ship_title       | VARCHAR   | 128    | FALSE       | Copy of `authen.t_user_address.title` made when the order was created, later changes of the address do not change the order                                              |                   |
|     |                                                         | ship_address     | BYTEA     |        | FALSE       | Copy of `authen.t_user_address.address` (encrypted) made when the order was created                                                                                      |                   |
|     |                                                         | ship_city        | BYTEA     |        | FALSE       | Copy of `authen.t_user_address.city` (encrypted) made when the order was created                                                                                         |                   |
|     |                                                         | ship_state       | BYTEA     |        | FALSE       | Copy of `authen.t_user_address.state` (encrypted) made when the order was created                                                                                        |                   |
|     |                                                         | ship_postal_code | BYTEA     |        | FALSE       | Copy of `authen.t_user_address.postal_code` (encrypted) made when the order was created                                                                                  |                   |
|     |                                                         | ship_country     | BYTEA     |        | FALSE       | Copy of `authen.t_user_address.country` (encrypted) made when the order was created                                                                                      |                   |
| UQ  |                                                         | code             | VARCHAR   | 64     | FALSE       | Unique                                                                                                                                                                   |                   |
|     |                                                         | total_price      | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_price >= 0`                                                                                                                                          |                   |
|     |                                                         | total_discount   | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_discount >= 0`                                                                                                                                       |                   |
|     |                                                         | total_tax        | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_tax >= 0`                                                                                                                                            |                   |
|     |                                                         | total_shipping   | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_shipping >= 0`                                                                                                                                       |                   |
|     |                                                         | total_amount     | NUMERIC   | 16,2   | FALSE       | Must satisfy `total_amount >= 0`                                                                                                                                         |                   |
|     |                                                         | expires_at       | TIMESTAMP |        | FALSE       | Time until which the order holds the stock, Set when the order is created, A WAIT_PAYMENT order that is not paid by then is cancelled and the stock goes back to the lot |                   |
|     |                                                         | status           | VARCHAR   | 32     | FALSE       | One of: PENDING, PROCESSING, WAIT_PAYMENT, PAYMENT_CONFIRMED, REFUNDED, COMPLETED, CANCELLED                                                                             | PENDING           |

## Constain

| Key Name                    | Column Name                                                          | Description                                                                                                            |
| --------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| pk_t_order_id               | id                                                                   | Primary key                                                                                                            |
| fk_t_order_user_id          | user_id                                                              | References authen.m_user(id), ON DELETE CASCADE                                                                        |
| fk_t_order_shop_id          | shop_id                                                              | References shop.m_shop(id), ON DELETE CASCADE                                                                          |
| fk_t_order_address_id       | address_id                                                           | References authen.t_user_address(id), ON DELETE RESTRICT                                                               |
|                             |                                                                      | ship_title                                                                                                             |
|                             |                                                                      | ship_address                                                                                                           |
|                             |                                                                      | ship_city                                                                                                              |
|                             |                                                                      | ship_state                                                                                                             |
|                             |                                                                      | ship_postal_code                                                                                                       |
|                             |                                                                      | ship_country                                                                                                           |
| uq_t_order_code             | code                                                                 | Unique                                                                                                                 |
| ck_t_order_row_status       | row_status                                                           | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                                          |
| ck_t_order_total_price      | total_price                                                          | CHECK (total_price >= 0)                                                                                               |
| ck_t_order_total_discount   | total_discount                                                       | CHECK (total_discount >= 0)                                                                                            |
| ck_t_order_total_tax        | total_tax                                                            | CHECK (total_tax >= 0)                                                                                                 |
| ck_t_order_total_shipping   | total_shipping                                                       | CHECK (total_shipping >= 0)                                                                                            |
| ck_t_order_total_amount     | total_amount                                                         | CHECK (total_amount >= 0)                                                                                              |
| ck_t_order_total_amount_sum | total_amount, total_price, total_discount, total_tax, total_shipping | CHECK (total_amount = total_price - total_discount + total_tax + total_shipping)                                       |
| ck_t_order_status           | status                                                               | CHECK (status IN ('PENDING', 'PROCESSING', 'WAIT_PAYMENT', 'PAYMENT_CONFIRMED', 'REFUNDED', 'COMPLETED', 'CANCELLED')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS sales.t_order (
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
        address_id UUID NOT NULL REFERENCES authen.t_user_address (id) ON DELETE RESTRICT,
        ship_title VARCHAR(128) NOT NULL,
        ship_address BYTEA NOT NULL,
        ship_city BYTEA NOT NULL,
        ship_state BYTEA NOT NULL,
        ship_postal_code BYTEA NOT NULL,
        ship_country BYTEA NOT NULL,
        code VARCHAR(64) NOT NULL UNIQUE,
        total_price NUMERIC(16, 2) NOT NULL CHECK (total_price >= 0),
        total_discount NUMERIC(16, 2) NOT NULL CHECK (total_discount >= 0),
        total_tax NUMERIC(16, 2) NOT NULL CHECK (total_tax >= 0),
        total_shipping NUMERIC(16, 2) NOT NULL CHECK (total_shipping >= 0),
        total_amount NUMERIC(16, 2) NOT NULL CHECK (total_amount >= 0),
        expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'WAIT_PAYMENT',
                'PAYMENT_CONFIRMED',
                'REFUNDED',
                'COMPLETED',
                'CANCELLED'
            )
        ),
        CONSTRAINT ck_t_order_total_amount_sum CHECK (total_amount = total_price - total_discount + total_tax + total_shipping)
    );
```
