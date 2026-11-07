CREATE SCHEMA IF NOT EXISTS shipping;

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
        order_item_id UUID NOT NULL REFERENCES sales.t_order_item (id) ON DELETE RESTRICT,
        quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_item_shipping_id_order_item_id ON shipping.t_shipping_item (shipping_id, order_item_id)
WHERE
    row_status <> 'DELETED';

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
        stop_type VARCHAR(32) NOT NULL CHECK (
            stop_type IN ('PICKUP', 'TRANSIT', 'DROPOFF')
        ),
        location_name VARCHAR(128) NOT NULL,
        estimated_arrival TIMESTAMP WITHOUT TIME ZONE,
        arrived_at TIMESTAMP WITHOUT TIME ZONE
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shipping_stop_shipping_id_stop_number ON shipping.t_shipping_stop (shipping_id, stop_number)
WHERE
    row_status <> 'DELETED';
