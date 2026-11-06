# Table: payment.t_payment

Description: Transaction table of the `payment` schema (defined in `db/migrations/up/07-payment.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name         | Data Type | Length | Is Nullable | Description                                                                                                                  | Example           |
| --- | --------------------------------------- | ------------------- | --------- | ------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                         | id                  | UUID      |        | FALSE       | Primary key                                                                                                                  | gen_random_uuid() |
|     |                                         | created_by          | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                                         |                   |
|     |                                         | created_at          | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                                           |                   |
|     |                                         | updated_by          | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                                    |                   |
|     |                                         | updated_at          | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                                      |                   |
|     |                                         | row_status          | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                                     | ACTIVE            |
| FK  | [sales.t_order.id](../sales/t_order.md) | order_id            | UUID      |        | FALSE       | Reference to `sales.t_order.id`                                                                                              |                   |
|     |                                         | provider            | VARCHAR   | 32     | FALSE       | Payment provider, one of: STRIPE. Defaults to `STRIPE`                                                                       | STRIPE            |
| UQ  |                                         | provider_payment_id | VARCHAR   | 64     | FALSE       | Id of the provider payment (a Stripe PaymentIntent, one row is one PaymentIntent). Unique                                    | pi_3QxExample     |
|     |                                         | amount              | NUMERIC   | 16,2   | FALSE       | Amount charged, equals the order total_price - total_discount + total_tax + shipping_fee. Must satisfy `amount >= 0`         |                   |
|     |                                         | currency            | VARCHAR   | 3      | FALSE       | Currency code, 3 upper case letters. Defaults to `THB`                                                                       | THB               |
|     |                                         | shipping_method     | VARCHAR   | 32     | FALSE       | Shipping method chosen when the payment starts, one of: STANDARD, EXPRESS, SAME_DAY                                          | STANDARD          |
|     |                                         | shipping_fee        | NUMERIC   | 16,2   | FALSE       | Shipping fee calculated by the system for the shipping method. Must satisfy `shipping_fee >= 0`. Defaults to `0.00`          | 0.00              |
|     |                                         | status              | VARCHAR   | 32     | FALSE       | One of: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED                                                          | PENDING           |
|     |                                         | payment_method      | VARCHAR   | 32     | FALSE       | One of: CREDIT_CARD, PAYPAL, BANK_TRANSFER, CASH_ON_DELIVERY, THAI_QR (only CREDIT_CARD and THAI_QR are accepted by the API) | CREDIT_CARD       |
|     |                                         | payment_name        | VARCHAR   | 64     | TRUE        | Display label of the payment, for example the card brand and the last 4 digits                                               | Visa 4242         |
| UQ  |                                         | transaction_code    | VARCHAR   | 64     | TRUE        | Id of the successful charge at the provider. Unique                                                                          |                   |
|     |                                         | transaction_at      | TIMESTAMP |        | TRUE        | Time the provider confirmed the payment. Required when status is COMPLETED or REFUNDED                                       |                   |
|     |                                         | failure_code        | VARCHAR   | 64     | TRUE        | Failure code from the provider. Only when status is FAILED                                                                   | card_declined     |
|     |                                         | failure_message     | VARCHAR   | 256    | TRUE        | Failure message from the provider. Only when status is FAILED                                                                |                   |
| UQ  |                                         | provider_refund_id  | VARCHAR   | 64     | TRUE        | Id of the refund at the provider. Unique, set together with refunded_at                                                      | re_3QxExample     |
|     |                                         | refunded_at         | TIMESTAMP |        | TRUE        | Time of the refund. Set exactly when status is REFUNDED                                                                      |                   |
|     |                                         | refund_reason       | VARCHAR   | 256    | TRUE        | Reason the shop or the system gave for the refund                                                                            |                   |

## Constain

| Key Name                              | Column Name                             | Description                                                                                                                     |
| ------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| pk_t_payment_id                       | id                                      | Primary key                                                                                                                     |
| fk_t_payment_order_id                 | order_id                                | References sales.t_order(id), ON DELETE RESTRICT (payments are financial history)                                               |
| uq_t_payment_provider_payment_id      | provider_payment_id                     | Unique                                                                                                                          |
| uq_t_payment_transaction_code         | transaction_code                        | Unique                                                                                                                          |
| uq_t_payment_provider_refund_id       | provider_refund_id                      | Unique                                                                                                                          |
| uq_t_payment_order_id_live            | order_id                                | Unique among rows where status IN ('PENDING', 'PROCESSING', 'COMPLETED') AND row_status = 'ACTIVE' (one live payment per order) |
| ck_t_payment_row_status               | row_status                              | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                                                   |
| ck_t_payment_provider                 | provider                                | CHECK (provider IN ('STRIPE'))                                                                                                  |
| ck_t_payment_amount                   | amount                                  | CHECK (amount >= 0)                                                                                                             |
| ck_t_payment_currency                 | currency                                | CHECK (currency ~ '^[A-Z]{3}$')                                                                                                 |
| ck_t_payment_shipping_method          | shipping_method                         | CHECK (shipping_method IN ('STANDARD', 'EXPRESS', 'SAME_DAY'))                                                                  |
| ck_t_payment_shipping_fee             | shipping_fee                            | CHECK (shipping_fee >= 0)                                                                                                       |
| ck_t_payment_status                   | status                                  | CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', 'REFUNDED'))                                     |
| ck_t_payment_payment_method           | payment_method                          | CHECK (payment_method IN ('CREDIT_CARD', 'PAYPAL', 'BANK_TRANSFER', 'CASH_ON_DELIVERY', 'THAI_QR'))                             |
| ck_t_payment_paid_has_transaction_at  | status, transaction_at                  | CHECK (status NOT IN ('COMPLETED', 'REFUNDED') OR transaction_at IS NOT NULL)                                                   |
| ck_t_payment_refund_details           | status, refunded_at, provider_refund_id | CHECK ((status = 'REFUNDED') = (refunded_at IS NOT NULL) AND (refunded_at IS NULL) = (provider_refund_id IS NULL))              |
| ck_t_payment_failure_only_when_failed | failure_code, failure_message, status   | CHECK ((failure_code IS NULL AND failure_message IS NULL) OR status = 'FAILED')                                                 |

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
        order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT,
        provider VARCHAR(32) NOT NULL DEFAULT 'STRIPE' CHECK (provider IN ('STRIPE')),
        provider_payment_id VARCHAR(64) NOT NULL UNIQUE,
        amount NUMERIC(16, 2) NOT NULL CHECK (amount >= 0),
        currency VARCHAR(3) NOT NULL DEFAULT 'THB' CHECK (currency ~ '^[A-Z]{3}$'),
        shipping_method VARCHAR(32) NOT NULL CHECK (
            shipping_method IN ('STANDARD', 'EXPRESS', 'SAME_DAY')
        ),
        shipping_fee NUMERIC(16, 2) NOT NULL DEFAULT 0.00 CHECK (shipping_fee >= 0),
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
        transaction_at TIMESTAMP WITHOUT TIME ZONE,
        failure_code VARCHAR(64),
        failure_message VARCHAR(256),
        provider_refund_id VARCHAR(64) UNIQUE,
        refunded_at TIMESTAMP WITHOUT TIME ZONE,
        refund_reason VARCHAR(256),
        CONSTRAINT ck_t_payment_paid_has_transaction_at CHECK (
            status NOT IN ('COMPLETED', 'REFUNDED')
            OR transaction_at IS NOT NULL
        ),
        CONSTRAINT ck_t_payment_refund_details CHECK (
            (status = 'REFUNDED') = (refunded_at IS NOT NULL)
            AND (refunded_at IS NULL) = (provider_refund_id IS NULL)
        ),
        CONSTRAINT ck_t_payment_failure_only_when_failed CHECK (
            (failure_code IS NULL AND failure_message IS NULL)
            OR status = 'FAILED'
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_payment_order_id_live ON payment.t_payment (order_id)
WHERE
    status IN ('PENDING', 'PROCESSING', 'COMPLETED')
    AND row_status = 'ACTIVE';
```
