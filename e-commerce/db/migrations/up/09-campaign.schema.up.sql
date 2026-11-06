CREATE SCHEMA IF NOT EXISTS campaign;

CREATE TABLE
    IF NOT EXISTS campaign.m_campaign (
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
        description TEXT,
        start_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        end_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        CONSTRAINT ck_m_campaign_period CHECK (end_at > start_at)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_campaign_name ON campaign.m_campaign (name)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS campaign.m_campaign_budget (
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
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        budget NUMERIC(16, 2) NOT NULL CHECK (budget >= 0),
        remaining NUMERIC(16, 2) NOT NULL CHECK (remaining >= 0),
        CONSTRAINT ck_m_campaign_budget_remaining_within_budget CHECK (remaining <= budget)
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_m_campaign_budget_campaign_id ON campaign.m_campaign_budget (campaign_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS campaign.m_campaign_budget_ledger (
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
        campaign_budget_id UUID NOT NULL REFERENCES campaign.m_campaign_budget (id) ON DELETE CASCADE,
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        order_id UUID NOT NULL REFERENCES sales.t_order (id) ON DELETE RESTRICT,
        entry_type VARCHAR(16) NOT NULL CHECK (entry_type IN ('RESERVE', 'RELEASE')),
        reference JSONB NOT NULL,
        usage NUMERIC(16, 2) NOT NULL CHECK (usage >= 0),
        remaining NUMERIC(16, 2) NOT NULL CHECK (remaining >= 0),
        UNIQUE (campaign_budget_id, order_id, entry_type)
    );

CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_product (
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
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        product_category_id UUID REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        product_id UUID REFERENCES product.m_product (id) ON DELETE CASCADE,
        CONSTRAINT ck_t_campaign_product_target CHECK (
            (product_category_id IS NULL) <> (product_id IS NULL)
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_id ON campaign.t_campaign_product (campaign_id, product_id)
WHERE
    product_id IS NOT NULL
    AND row_status <> 'DELETED';

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_product_campaign_id_product_category_id ON campaign.t_campaign_product (campaign_id, product_category_id)
WHERE
    product_category_id IS NOT NULL
    AND row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_shop (
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
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        shop_id UUID NOT NULL REFERENCES shop.m_shop (id) ON DELETE CASCADE
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_shop_campaign_id_shop_id ON campaign.t_campaign_shop (campaign_id, shop_id)
WHERE
    row_status <> 'DELETED';

CREATE TABLE
    IF NOT EXISTS campaign.t_campaign_discount (
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
        campaign_id UUID NOT NULL REFERENCES campaign.m_campaign (id) ON DELETE CASCADE,
        discount_type VARCHAR(32) NOT NULL CHECK (discount_type IN ('PERCENTAGE', 'FIXED_AMOUNT')),
        discount_value NUMERIC(16, 2) NOT NULL CHECK (discount_value > 0),
        CONSTRAINT ck_t_campaign_discount_percentage CHECK (
            discount_type <> 'PERCENTAGE'
            OR discount_value <= 100
        )
    );

CREATE UNIQUE INDEX IF NOT EXISTS uq_t_campaign_discount_campaign_id ON campaign.t_campaign_discount (campaign_id)
WHERE
    row_status <> 'DELETED';
