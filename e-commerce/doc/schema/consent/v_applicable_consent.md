---
name: "Schema doc: consent.v_applicable_consent"
description: "Columns, source tables and filter of the view consent.v_applicable_consent: every ACTIVE consent of an ACTIVE consent type, with no time filter. Read-only view of the `consent` schema (defined in `db/migrations/up/00-common.schema.up.sql`). Read it when you write or review a query or an API spec that needs the consents a user may be asked for."
---

# View: consent.v_applicable_consent

Description: **View, not a table.** Read-only view of the `consent` schema (defined in `db/migrations/up/00-common.schema.up.sql`). One row per [consent.t_consent](t_consent.md) row with `row_status = 'ACTIVE'` whose [consent.m_consent_type](m_consent_type.md) has `row_status = 'ACTIVE'`. It keeps the rule "an ACTIVE consent of an ACTIVE consent type" in one place for every API that reads current consents. It has no key, no constraint, no index and no audit columns of its own, and nothing writes to it.

The view holds no `now()`: the time is the caller's. A caller that wants the consents in effect now adds `effective_at <= '<sequence.now>' AND (expired_at IS NULL OR expired_at > '<sequence.now>')` with the server time it captured, so every statement of one request uses the same time.

## Columns

| Key | Reference                                         | Column Name     | Data Type | Length | Is Nullable | Description                                                    | Example |
| --- | ------------------------------------------------- | --------------- | --------- | ------ | ----------- | -------------------------------------------------------------- | ------- |
|     | [consent.t_consent.id](t_consent.md)              | id              | UUID      |        | FALSE       | Id of the consent (`consent.t_consent.id`)                     |         |
|     | [consent.t_consent.consent_type_id](t_consent.md) | consent_type_id | UUID      |        | FALSE       | Id of its consent type, always an ACTIVE `m_consent_type` row  |         |
|     | [consent.t_consent.consent_version](t_consent.md) | consent_version | VARCHAR   | 8      | FALSE       | Current version of the consent                                 | 1.0.0   |
|     | [consent.t_consent.is_required](t_consent.md)     | is_required     | BOOLEAN   |        | FALSE       | Whether this consent must be accepted (the consent's own flag) | FALSE   |
|     | [consent.t_consent.effective_at](t_consent.md)    | effective_at    | TIMESTAMP |        | FALSE       | Start of the consent; the caller compares it with its now      |         |
|     | [consent.t_consent.expired_at](t_consent.md)      | expired_at      | TIMESTAMP |        | TRUE        | End of the consent, NULL when open; the caller compares it     |         |

## Filter

| Source                                         | Condition                 | Description                                         |
| ---------------------------------------------- | ------------------------- | --------------------------------------------------- |
| [consent.t_consent](t_consent.md) c            | c.row_status = 'ACTIVE'   | INACTIVE, DELETED, LOCKED and ARCHIVED are excluded |
| [consent.m_consent_type](m_consent_type.md) ct | ct.id = c.consent_type_id | Inner join on the consent's type                    |
| [consent.m_consent_type](m_consent_type.md) ct | ct.row_status = 'ACTIVE'  | A consent of a type that is not ACTIVE is excluded  |

---

```SQL
CREATE OR REPLACE VIEW consent.v_applicable_consent AS
SELECT
    c.id,
    c.consent_type_id,
    c.consent_version,
    c.is_required,
    c.effective_at,
    c.expired_at
FROM consent.t_consent c
JOIN consent.m_consent_type ct ON ct.id = c.consent_type_id
WHERE c.row_status = 'ACTIVE'
AND ct.row_status = 'ACTIVE';
```
