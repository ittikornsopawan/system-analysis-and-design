# Table: shop.m_shop

Description: Master table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                             | Column Name          | Data Type | Length | Is Nullable | Description                                                                                        | Example           |
| --- | ------------------------------------- | -------------------- | --------- | ------ | ----------- | -------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                                       | id                   | UUID      |        | FALSE       | Primary key                                                                                        | gen_random_uuid() |
|     |                                       | created_by           | VARCHAR   | 64     | FALSE       | User or service that created the row                                                               |                   |
|     |                                       | created_at           | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                 |                   |
|     |                                       | updated_by           | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                          |                   |
|     |                                       | updated_at           | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                            |                   |
|     |                                       | row_status           | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                           | ACTIVE            |
| FK  | [shop.m_shop_type.id](m_shop_type.md) | type_id              | UUID      |        | FALSE       | Reference to `shop.m_shop_type.id`                                                                 |                   |
| UQ  |                                       | name                 | VARCHAR   | 128    | FALSE       | Unique                                                                                             |                   |
|     |                                       | description          | VARCHAR   | 256    | FALSE       |                                                                                                    |                   |
|     |                                       | platform_margin_rate | NUMERIC   | 8,2    | FALSE       | Must satisfy `platform_margin_rate >= 0.00 AND platform_margin_rate <= 100.00`. Defaults to `0.00` | 0.00              |
|     |                                       | shop_margin_rate     | NUMERIC   | 8,2    | FALSE       | Must satisfy `shop_margin_rate >= 0.00 AND shop_margin_rate <= 100.00`. Defaults to `0.00`         | 0.00              |

## Constain

| Key Name                       | Column Name          | Description                                                                   |
| ------------------------------ | -------------------- | ----------------------------------------------------------------------------- |
| pk_m_shop_id                   | id                   | Primary key                                                                   |
| fk_m_shop_type_id              | type_id              | References shop.m_shop_type(id), ON DELETE CASCADE                            |
| uq_m_shop_name                 | name                 | Unique                                                                        |
| ck_m_shop_row_status           | row_status           | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |
| ck_m_shop_platform_margin_rate | platform_margin_rate | CHECK (platform_margin_rate >= 0.00 AND platform_margin_rate <= 100.00)       |
| ck_m_shop_shop_margin_rate     | shop_margin_rate     | CHECK (shop_margin_rate >= 0.00 AND shop_margin_rate <= 100.00)               |

---

```SQL
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
```
