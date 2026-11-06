# Table: shop.m_shop_type

Description: Master table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |           | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |           | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |           | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |           | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |           | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |           | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
|     |           | name        | VARCHAR   | 128    | FALSE       | Unique among rows where row_status <> 'DELETED'                          |                   |
|     |           | description | VARCHAR   | 256    | FALSE       |                                                                          |                   |

## Constain

| Key Name                  | Column Name | Description                                                                   |
| ------------------------- | ----------- | ----------------------------------------------------------------------------- |
| pk_m_shop_type_id         | id          | Primary key                                                                   |
| uq_m_shop_type_name       | name        | Unique among rows where row_status <> 'DELETED'                               |
| ck_m_shop_type_row_status | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
```
