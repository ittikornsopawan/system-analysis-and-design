-- Seed of the author schema (WP5, approved 2026-11-06).
-- Run it after the migrations, as the system. It can run again and again: every row is inserted only when it is missing.
-- It creates no user and grants nothing. The first administrator is made by grant-platform-admin.sql.
-- run_db_tests.sh does not run this file by itself, only db/tests/02-author-seed.test.sql runs it.

-- the system role: it cannot be changed or deleted through the API, and its holders have every permission in every scope
INSERT INTO
    author.m_role (created_by, name, description)
VALUES
    (
        'system',
        'PLATFORM_ADMIN',
        'Platform administrator: manages the whole platform, has every permission in every scope'
    )
ON CONFLICT (name)
WHERE
    row_status <> 'DELETED' DO NOTHING;

-- scope: how far a permission reaches
INSERT INTO
    author.m_scope (created_by, scope, name, description)
VALUES
    ('system', 'ALL', 'All', 'The whole platform'),
    ('system', 'SHOP', 'Shop', 'The shops where the caller is an ACTIVE member'),
    ('system', 'OWN', 'Own', 'The data of the caller')
ON CONFLICT (scope)
WHERE
    row_status <> 'DELETED' DO NOTHING;

-- permission: a named capability, the list is reference data until an API enforces it
INSERT INTO
    author.m_permission (created_by, name, description)
VALUES
    ('system', 'catalog.manage', 'Manage product types, brands, categories, attributes and shop types'),
    ('system', 'consent.manage', 'Manage consent types and the content of consents'),
    ('system', 'shop.manage', 'Manage shops, their members, SKUs and lots'),
    ('system', 'order.read', 'Read orders'),
    ('system', 'payment.refund', 'Refund payments'),
    ('system', 'shipping.manage', 'Manage shipping'),
    ('system', 'author.manage', 'Manage roles, permissions and scopes')
ON CONFLICT (name)
WHERE
    row_status <> 'DELETED' DO NOTHING;

-- the scopes each permission can have
INSERT INTO
    author.t_permission_scope (created_by, permission_id, scope_id)
SELECT
    'system',
    p.id,
    s.id
FROM
    (
        VALUES
            ('catalog.manage', 'ALL'),
            ('consent.manage', 'ALL'),
            ('shop.manage', 'ALL'),
            ('shop.manage', 'SHOP'),
            ('order.read', 'ALL'),
            ('order.read', 'SHOP'),
            ('order.read', 'OWN'),
            ('payment.refund', 'ALL'),
            ('payment.refund', 'SHOP'),
            ('shipping.manage', 'ALL'),
            ('shipping.manage', 'SHOP'),
            ('author.manage', 'ALL')
    ) AS v (permission, scope)
    INNER JOIN author.m_permission p ON p.name = v.permission
    AND p.row_status <> 'DELETED'
    INNER JOIN author.m_scope s ON s.scope = v.scope
    AND s.row_status <> 'DELETED'
ON CONFLICT (permission_id, scope_id)
WHERE
    row_status <> 'DELETED' DO NOTHING;
