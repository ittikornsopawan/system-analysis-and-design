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
        name VARCHAR(128) NOT NULL UNIQUE,
        description VARCHAR(256) NOT NULL
    );

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
        type_id UUID NOT NULL REFERENCES shop.m_shop_type (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL UNIQUE,
        description VARCHAR(256) NOT NULL,
        platform_margin_rate NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (
            platform_margin_rate >= 0.00
            AND platform_margin_rate <= 100.00
        ),
        shop_margin_rate NUMERIC(8, 2) NOT NULL DEFAULT 0.00 CHECK (
            shop_margin_rate >= 0.00
            AND shop_margin_rate <= 100.00
        ),
    );

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
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
        UNIQUE (shop_id, product_id)
    );

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
        cost_price NUMERIC(16, 2) NOT NULL,
        selling_price NUMERIC(16, 2) NOT NULL,
        gross_margin NUMERIC(16, 2),
        share_margin NUMERIC(16, 2),
        platform_margin NUMERIC(16, 2),
        quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
        UNIQUE (shop_product_id, sku_id)
    );

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