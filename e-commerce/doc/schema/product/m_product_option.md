# Table: product.m_product_option

Description: Master table of the `product` schema (defined in `db/migrations/up/03-product.schema.up.sql`).

## Columns

| Key | Reference                            | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ------------------------------------ | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                      | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                      | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                      | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                      | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                      | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                      | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [product.m_product.id](m_product.md) | product_id  | UUID      |        | FALSE       | Reference to `product.m_product.id`                                      |                   |
|     |                                      | name        | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                                      | level_no    | SMALLINT  |        | FALSE       | Level of the option starting from 1, Order in the product options        | 1                 |

## Constain

| Key Name                                | Column Name          | Description                                                                   |
| --------------------------------------- | -------------------- | ----------------------------------------------------------------------------- |
| pk_m_product_option_id                  | id                   | Primary key                                                                   |
| fk_m_product_option_product_id          | product_id           | References product.m_product(id), ON DELETE CASCADE                           |
| uq_m_product_option_product_id_level_no | product_id, level_no | Unique among rows where row_status <> 'DELETED'                               |
| uq_m_product_option_product_id_name     | product_id, name     | Unique among rows where row_status <> 'DELETED'                               |
| ck_m_product_option_level_no            | level_no             | CHECK (level_no >= 1)                                                         |
| ck_m_product_option_row_status          | row_status           | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
```
