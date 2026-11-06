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