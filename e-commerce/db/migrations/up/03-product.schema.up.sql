CREATE SCHEMA IF NOT EXISTS product;

CREATE TABLE
    IF NOT EXISTS product.m_product_type (
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_type_name ON product.m_product_type (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS product.m_product_category (
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
        parent_id UUID REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL UNIQUE,
        description VARCHAR(256) NOT NULL,
        slug VARCHAR(128) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS product.m_product_category_attribute (
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
        category_id UUID NOT NULL REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL UNIQUE,
        description VARCHAR(256) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS product.m_product_brand (
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

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_brand_name ON product.m_product_brand (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS product.m_product (
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
        type_id UUID NOT NULL REFERENCES product.m_product_type (id) ON DELETE RESTRICT,
        category_id UUID NOT NULL REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        brand_id UUID NOT NULL REFERENCES product.m_product_brand (id) ON DELETE RESTRICT,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        body TEXT NOT NULL,
        slug VARCHAR(128) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS product.m_product_attribute (
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
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        attribute_id UUID NOT NULL REFERENCES product.m_product_category_attribute (id) ON DELETE CASCADE,
        value VARCHAR(256) NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS product.m_product_option (
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
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL,
        level_no SMALLINT NOT NULL CHECK (level_no >= 1)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_option_product_id_level_no ON product.m_product_option (product_id, level_no)
WHERE
    row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_option_product_id_name ON product.m_product_option (product_id, name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS product.m_product_option_value (
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
        option_id UUID NOT NULL REFERENCES product.m_product_option (id) ON DELETE CASCADE,
        value VARCHAR(128) NOT NULL,
        sort_order INT NOT NULL DEFAULT 0
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_option_value_option_id_value ON product.m_product_option_value (option_id, value)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS product.m_product_image (
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
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        image_path TEXT NOT NULL,
        option_value_id UUID REFERENCES product.m_product_option_value (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS product.m_product_sku (
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
        product_id UUID NOT NULL REFERENCES product.m_product (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        combination_key TEXT NOT NULL DEFAULT ''
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_product_sku_product_id_combination_key ON product.m_product_sku (product_id, combination_key)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS product.m_product_sku_option_value (
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
        sku_id UUID NOT NULL REFERENCES product.m_product_sku (id) ON DELETE CASCADE,
        option_value_id UUID NOT NULL REFERENCES product.m_product_option_value (id) ON DELETE CASCADE,
        UNIQUE (sku_id, option_value_id)
    );