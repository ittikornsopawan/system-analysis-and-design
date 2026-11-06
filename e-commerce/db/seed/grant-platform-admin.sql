-- Makes one user the first platform administrator (WP5, approved 2026-11-06). Run by hand by the system operator, never by the application:
--
--   psql --single-transaction -v ON_ERROR_STOP=1 -v user_id=<user id> -f grant-platform-admin.sql
--
-- Before you run it, check outside the system that the account with this user id belongs to the real administrator
-- (registration does not verify the email address, so never grant by email address).
-- The command works only when no ACTIVE administrator exists: an administrator is an ACTIVE assignment of the ACTIVE role
-- PLATFORM_ADMIN to an ACTIVE user. "INSERT 0 1" means the user was made an administrator, "INSERT 0 0" means it was refused
-- (an administrator exists, the user is not ACTIVE or does not exist, or the role is missing: run author.seed.sql first).
-- Run in one transaction: the first statement locks the role row, so two commands at the same time cannot both succeed.

SELECT
    r.id
FROM
    author.m_role r
WHERE
    r.name = 'PLATFORM_ADMIN'
    AND r.row_status = 'ACTIVE'
FOR UPDATE;

INSERT INTO
    author.t_user_role (created_by, user_id, role_id)
SELECT
    'system',
    u.id,
    r.id
FROM
    authen.m_user u
    INNER JOIN author.m_role r ON r.name = 'PLATFORM_ADMIN'
    AND r.row_status = 'ACTIVE'
WHERE
    u.id = :'user_id'
    AND u.row_status = 'ACTIVE'
    AND NOT EXISTS (
        SELECT
            1
        FROM
            author.t_user_role ur
            INNER JOIN authen.m_user holder ON holder.id = ur.user_id
            AND holder.row_status = 'ACTIVE'
        WHERE
            ur.role_id = r.id
            AND ur.row_status = 'ACTIVE'
    )
ON CONFLICT (user_id, role_id)
WHERE
    row_status <> 'DELETED' DO UPDATE
SET
    updated_by = 'system',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'ACTIVE';
