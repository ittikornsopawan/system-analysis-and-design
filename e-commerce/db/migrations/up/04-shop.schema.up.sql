CREATE SCHEMA IF NOT EXISTS shop;

CREATE TABLE
    IF NOT EXISTS shop.m_shop_type (
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
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_type_name ON shop.m_shop_type (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS shop.m_shop (
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
        type_id UUID NOT NULL REFERENCES shop.m_shop_type (id) ON DELETE RESTRICT,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        platform_margin_rate NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (
            platform_margin_rate >= 0.00
            AND platform_margin_rate <= 100.00
        ),
        shop_margin_rate NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (
            shop_margin_rate >= 0.00
            AND shop_margin_rate <= 100.00
        ),
        CONSTRAINT ck_m_shop_margin_rate_total CHECK (platform_margin_rate + shop_margin_rate <= 100.00)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_name ON shop.m_shop (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS shop.t_shop_user (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        role VARCHAR(32) NOT NULL DEFAULT 'STAFF' CHECK (role IN ('ADMIN', 'STAFF'))
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_user_shop_id_user_id ON shop.t_shop_user (shop_id, user_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS shop.m_shop_image (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        type VARCHAR(32) NOT NULL DEFAULT 'LOGO' CHECK (type IN ('LOGO', 'BANNER', 'WALLPAPER')),
        seq INT NOT NULL DEFAULT 0,
        image_path TEXT NOT NULL
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_image_shop_id_logo ON shop.m_shop_image (shop_id)
WHERE
    type = 'LOGO'
    AND row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_shop_image_shop_id_wallpaper ON shop.m_shop_image (shop_id)
WHERE
    type = 'WALLPAPER'
    AND row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS shop.t_shop_product (
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
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE,
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_shop_id_product_id ON shop.t_shop_product (shop_id, product_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS shop.t_shop_product_sku (
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
        shop_product_id UUID NOT NULL REFERENCES shop.t_shop_product (id) ON DELETE CASCADE,
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        code VARCHAR(64) NOT NULL,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        UNIQUE (shop_product_id, sku_id)
    );

CREATE TABLE
    IF NOT EXISTS shop.t_shop_product_sku_lot (
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
        shop_product_sku_id UUID NOT NULL REFERENCES shop.t_shop_product_sku (id) ON DELETE CASCADE,
        lot_no VARCHAR(64) NOT NULL,
        cost_price NUMERIC(16, 2) NOT NULL CHECK (cost_price >= 0),
        selling_price NUMERIC(16, 2) NOT NULL CHECK (selling_price >= 0),
        gross_margin NUMERIC(16, 2),
        share_margin NUMERIC(16, 2),
        platform_margin NUMERIC(16, 2),
        quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
        is_on_sale BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT ck_t_shop_product_sku_lot_price_not_below_cost CHECK (selling_price >= cost_price)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_sku_lot_shop_product_sku_id_lot_no ON shop.t_shop_product_sku_lot (shop_product_sku_id, lot_no)
WHERE
    row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_sku_lot_on_sale ON shop.t_shop_product_sku_lot (shop_product_sku_id)
WHERE
    is_on_sale
    AND row_status = 'ACTIVE';

CREATE TABLE
    IF NOT EXISTS shop.t_shop_product_review (
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
        shop_product_id UUID NOT NULL REFERENCES shop.t_shop_product (id) ON DELETE CASCADE,
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        rating INT NOT NULL CHECK (
            rating >= 1
            AND rating <= 5
        ),
        comment TEXT
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_shop_product_review_shop_product_id_user_id ON shop.t_shop_product_review (shop_product_id, user_id)
WHERE
    row_status <> 'DELETED';
