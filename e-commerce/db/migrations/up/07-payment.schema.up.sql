CREATE SCHEMA IF NOT EXISTS payment;

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