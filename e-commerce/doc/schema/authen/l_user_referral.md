---
name: "Schema doc: authen.l_user_referral"
description: "Columns, keys, constraints and indexes of the table authen.l_user_referral. Log table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`). Read it when you write or review a migration, a query or an API spec that uses this table."
---

# Table: authen.l_user_referral

Description: Log table of the `authen` schema (defined in `db/migrations/up/01-authen.schema.up.sql`).

## Columns

| Key | Reference                     | Column Name | Data Type | Length | Is Nullable | Description                                | Example           |
| --- | ----------------------------- | ----------- | --------- | ------ | ----------- | ------------------------------------------ | ----------------- |
| PK  |                               | id          | UUID      |        | FALSE       | Primary key                                | gen_random_uuid() |
|     |                               | created_by  | VARCHAR   | 64     | FALSE       | User or service that created the row       |                   |
|     |                               | created_at  | TIMESTAMP |        | FALSE       | Timestamp when the row was created         |                   |
| FK  | [authen.m_user.id](m_user.md) | user_id     | UUID      |        | FALSE       | Reference to `authen.m_user.id`            |                   |
| FK  | [authen.m_user.id](m_user.md) | referrer_id | UUID      |        | TRUE        | Reference to `authen.m_user.id` (optional) |                   |

## Constain

| Key Name                       | Column Name | Description                                      |
| ------------------------------ | ----------- | ------------------------------------------------ |
| pk_l_user_referral_id          | id          | Primary key                                      |
| fk_l_user_referral_user_id     | user_id     | References authen.m_user(id), ON DELETE CASCADE  |
| fk_l_user_referral_referrer_id | referrer_id | References authen.m_user(id), ON DELETE SET NULL |

---

```SQL
CREATE TABLE
    IF NOT EXISTS authen.l_user_referral (
        id UUID NOT NULL DEFAULT GEN_RANDOM_UUID () PRIMARY KEY,
        created_by VARCHAR(64) NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW (),
        user_id UUID NOT NULL REFERENCES authen.m_user (id) ON DELETE CASCADE,
        referrer_id UUID REFERENCES authen.m_user (id) ON DELETE SET NULL
    );
```
