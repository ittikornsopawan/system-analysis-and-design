# Table: payment.t_payment

Description: Transaction table of the `payment` schema (defined in `db/migrations/up/07-payment.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name      | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | ---------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id               | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by       | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at       | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by       | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at       | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status       | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [sales.t_order.id](../sales/t_order.md) | order_id         | UUID      |        | FALSE       | Reference to `sales.t_order.id`                                          |                   |
|     |                                         | amount           | NUMERIC   | 16,2   | FALSE       | Must satisfy `amount >= 0`                                               |                   |
|     |                                         | status           | VARCHAR   | 32     | FALSE       | One of: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED      | PENDING           |
|     |                                         | payment_method   | VARCHAR   | 32     | FALSE       | One of: CREDIT_CARD, PAYPAL, BANK_TRANSFER, CASH_ON_DELIVERY, THAI_QR    | CREDIT_CARD       |
|     |                                         | payment_name     | VARCHAR   | 64     | TRUE        |                                                                          |                   |
| UQ  |                                         | transaction_code | VARCHAR   | 64     | TRUE        | Unique                                                                   |                   |
|     |                                         | transaction_at   | TIMESTAMP |        | TRUE        |                                                                          |                   |

## Constain

| Key Name                      | Column Name      | Description                                                                                         |
| ----------------------------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| pk_t_payment_id               | id               | Primary key                                                                                         |
| fk_t_payment_order_id         | order_id         | References sales.t_order(id), ON DELETE CASCADE                                                     |
| uq_t_payment_transaction_code | transaction_code | Unique                                                                                              |
| ck_t_payment_row_status       | row_status       | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                       |
| ck_t_payment_amount           | amount           | CHECK (amount >= 0)                                                                                 |
| ck_t_payment_status           | status           | CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', 'REFUNDED'))         |
| ck_t_payment_payment_method   | payment_method   | CHECK (payment_method IN ('CREDIT_CARD', 'PAYPAL', 'BANK_TRANSFER', 'CASH_ON_DELIVERY', 'THAI_QR')) |

---

```SQL
CREATE TABLE
    IF NOT EXISTS payment.t_payment (
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
        amount NUMERIC(16, 2) NOT NULL CHECK (amount >= 0),
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'FAILED',
                'CANCELLED',
                'REFUNDED'
            )
        ),
        payment_method VARCHAR(32) NOT NULL CHECK (
            payment_method IN (
                'CREDIT_CARD',
                'PAYPAL',
                'BANK_TRANSFER',
                'CASH_ON_DELIVERY',
                'THAI_QR'
            )
        ),
        payment_name VARCHAR(64),
        transaction_code VARCHAR(64) UNIQUE,
        transaction_at TIMESTAMP WITHOUT TIME ZONE
    );
```
