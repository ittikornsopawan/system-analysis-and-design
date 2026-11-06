# Table: shop.m_shop_image

Description: Master table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                   | Column Name | Data Type | Length | Is Nullable | Description                                                                                                   | Example           |
| --- | --------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------- | ----------------- |
| PK  |                             | id          | UUID      |        | FALSE       | Primary key                                                                                                   | gen_random_uuid() |
|     |                             | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                                                          |                   |
|     |                             | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                                                            |                   |
|     |                             | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                                                     |                   |
|     |                             | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                                                       |                   |
|     |                             | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED                                      | ACTIVE            |
| FK  | [shop.m_shop.id](m_shop.md) | shop_id     | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                                                                 |                   |
|     |                             | type        | VARCHAR   | 32     | FALSE       | One of: LOGO, BANNER, WALLPAPER. One LOGO and one WALLPAPER per shop among rows where row_status <> 'DELETED' | LOGO              |
|     |                             | seq         | INT       |        | FALSE       | Defaults to `0`                                                                                               | 0                 |
|     |                             | image_path  | TEXT      |        | FALSE       |                                                                                                               |                   |

## Constain

| Key Name                          | Column Name | Description                                                                                     |
| --------------------------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| pk_m_shop_image_id                | id          | Primary key                                                                                     |
| fk_m_shop_image_shop_id           | shop_id     | References shop.m_shop(id), ON DELETE CASCADE                                                   |
| ck_m_shop_image_row_status        | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))                   |
| ck_m_shop_image_type              | type        | CHECK (type IN ('LOGO', 'BANNER', 'WALLPAPER'))                                                 |
| uq_m_shop_image_shop_id_logo      | shop_id     | Unique among rows where type = 'LOGO' AND row_status <> 'DELETED' (one LOGO per shop)           |
| uq_m_shop_image_shop_id_wallpaper | shop_id     | Unique among rows where type = 'WALLPAPER' AND row_status <> 'DELETED' (one WALLPAPER per shop) |

---

```SQL
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
```
