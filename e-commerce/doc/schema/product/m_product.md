# Table: product.m_product

Description: Master table of the `product` schema (defined in `db/migrations/up/03-product.schema.up.sql`).

## Columns

| Key | Reference                                              | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ------------------------------------------------------ | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                                        | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                                        | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                                        | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                                        | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                                        | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                                        | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [product.m_product_type.id](m_product_type.md)         | type_id     | UUID      |        | FALSE       | Reference to `product.m_product_type.id`                                 |                   |
| FK  | [product.m_product_category.id](m_product_category.md) | category_id | UUID      |        | FALSE       | Reference to `product.m_product_category.id`                             |                   |
| FK  | [product.m_product_brand.id](m_product_brand.md)       | brand_id    | UUID      |        | FALSE       | Reference to `product.m_product_brand.id`                                |                   |
|     |                                                        | name        | VARCHAR   | 128    | FALSE       |                                                                          |                   |
|     |                                                        | description | VARCHAR   | 256    | FALSE       |                                                                          |                   |
|     |                                                        | body        | TEXT      |        | FALSE       |                                                                          |                   |
|     |                                                        | slug        | VARCHAR   | 128    | FALSE       | URL friendly name used in the web URL, /{id}/{slug}                      | wireless-mouse    |

## Constain

| Key Name                 | Column Name | Description                                                                   |
| ------------------------ | ----------- | ----------------------------------------------------------------------------- |
| pk_m_product_id          | id          | Primary key                                                                   |
| fk_m_product_type_id     | type_id     | References product.m_product_type(id), ON DELETE CASCADE                      |
| fk_m_product_category_id | category_id | References product.m_product_category(id), ON DELETE CASCADE                  |
| fk_m_product_brand_id    | brand_id    | References product.m_product_brand(id), ON DELETE CASCADE                     |
| ck_m_product_row_status  | row_status  | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED')) |

---

```SQL
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
        type_id UUID NOT NULL REFERENCES product.m_product_type (id) ON DELETE CASCADE,
        category_id UUID NOT NULL REFERENCES product.m_product_category (id) ON DELETE CASCADE,
        brand_id UUID NOT NULL REFERENCES product.m_product_brand (id) ON DELETE CASCADE,
        name VARCHAR(128) NOT NULL,
        description VARCHAR(256) NOT NULL,
        body TEXT NOT NULL,
        slug VARCHAR(128) NOT NULL
    );
```
