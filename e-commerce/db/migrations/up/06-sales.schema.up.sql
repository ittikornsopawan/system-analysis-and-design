CREATE SCHEMA IF NOT EXISTS sales;

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

CREATE TABLE
    IF NOT EXISTS sales.t_order_item (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
        price NUMERIC(16, 2) NOT NULL CHECK (price >= 0),
        discount NUMERIC(16, 2) NOT NULL CHECK (discount >= 0),
        total_price NUMERIC(16, 2) NOT NULL CHECK (
            total_price >= 0
            AND total_price = price * quantity
        ),
        gross_profit NUMERIC(16, 2) NOT NULL CHECK (gross_profit >= 0),
        shop_profit NUMERIC(16, 2),
        platform_profit NUMERIC(16, 2),
        lot_id UUID NOT NULL REFERENCES shop.t_shop_product_sku_lot (id) ON DELETE RESTRICT,
        UNIQUE (order_id, product_id, sku_id)
    );