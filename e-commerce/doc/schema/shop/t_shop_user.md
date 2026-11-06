# Table: shop.t_shop_user

Description: Transaction table of the `shop` schema (defined in `db/migrations/up/04-shop.schema.up.sql`).

## Columns

| Key | Reference                               | Column Name | Data Type | Length | Is Nullable | Description                                                              | Example           |
| --- | --------------------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------------------------------------ | ----------------- |
| PK  |                                         | id          | UUID      |        | FALSE       | Primary key                                                              | gen_random_uuid() |
|     |                                         | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row                                     |                   |
|     |                                         | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created                                       |                   |
|     |                                         | updated_by  | VARCHAR   | 64     | TRUE        | User or service that last updated the row                                |                   |
|     |                                         | updated_at  | TIMESTAMP |        | TRUE        | Timestamp when the row was last updated                                  |                   |
|     |                                         | row_status  | VARCHAR   | 32     | FALSE       | Lifecycle status of the row: ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED | ACTIVE            |
| FK  | [shop.m_shop.id](m_shop.md)             | shop_id     | UUID      |        | FALSE       | Reference to `shop.m_shop.id`                                            |                   |
| FK  | [authen.m_user.id](../authen/m_user.md) | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`                                          |                   |
|     |                                         | role        | VARCHAR   | 32     | FALSE       | One of: ADMIN, STAFF                                                     | STAFF             |

## Constain

| Key Name                       | Column Name      | Description                                                                        |
| ------------------------------ | ---------------- | ---------------------------------------------------------------------------------- |
| pk_t_shop_user_id              | id               | Primary key                                                                        |
| fk_t_shop_user_shop_id         | shop_id          | References shop.m_shop(id), ON DELETE CASCADE                                      |
| fk_t_shop_user_user_id         | user_id          | References authen.m_user(id), ON DELETE CASCADE                                    |
| uq_t_shop_user_shop_id_user_id | shop_id, user_id | Unique among rows where row_status <> 'DELETED' (one membership per shop and user) |
| ck_t_shop_user_row_status      | row_status       | CHECK (row_status IN ('ACTIVE', 'INACTIVE', 'DELETED', 'LOCKED', 'ARCHIVED'))      |
| ck_t_shop_user_role            | role             | CHECK (role IN ('ADMIN', 'STAFF'))                                                 |

---

```SQL
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
```
