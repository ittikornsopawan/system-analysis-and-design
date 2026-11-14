---
name: "Schema doc: shop.t_shop_product_review"
description: "Columns, keys, constraints and indexes of the table shop.t_shop_product_review. Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: shop.t_shop_product_review

Description: Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                                   | Column Name     | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | ------------------------------------------- | --------------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                             | id              | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                             | created_by      | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                             | created_at      | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                             | updated_by      | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                             | updated_at      | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                             | row_status      | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shop.t_shop_product.id](t_shop_product.md) | shop_product_id | UUID      |        | FALSE       | Reference to `shop.t_shop_product.id`                                    |                   |
| FK  | [authen.m_user.id](../authen/m_user.md)     | user_id         | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
|     |                                             | rating          | INT       |        | FALSE       | Must satisfy `rating >= 1 AND rating <= 5`                               |                   |
|     |                                             | comment         | TEXT      |        | TRUE        |                                                                          |                   |

## Constain

| Key Name                                         | Column Name              | Description                                                                            |
| ------------------------------------------------ | ------------------------ | -------------------------------------------------------------------------------------- |
| pk_t_shop_product_review_id                      | id                       | Primary key                                                                            |
| fk_t_shop_product_review_shop_product_id         | shop_product_id          | References shop.t_shop_product(id), ON DELETE CASCADE                                  |
| fk_t_shop_product_review_user_id                 | user_id                  | References authen.m_user(id), ON DELETE CASCADE                                        |
| ck_t_shop_product_review_row_status              | row_status               | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))          |
| uq_t_shop_product_review_shop_product_id_user_id | shop_product_id, user_id | Unique among rows where row_status <> 'DELETED' (one review per user and shop product) |
| ck_t_shop_product_review_rating                  | rating                   | CHECK (rating >= 1 AND rating <= 5)                                                    |

---

```SQL
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
```
