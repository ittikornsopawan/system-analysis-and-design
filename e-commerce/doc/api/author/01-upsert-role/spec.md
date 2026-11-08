---
name: Single Role Upsert API Specification
description: Defines JWT-claim authorization, current credentials, immutable system role, guarded lifecycle writes and complete transactional outcomes for a single role.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/role/upsert

| Title       | Description                                                                                                                                                                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Role API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                              |
| Endpoint    | v{version}/author/role/upsert                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                 |
| Description | Insert, update or delete a role, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Role Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED role counts as not found                                                                                                            | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | name           | String       | MANDATORY | Role Name, Role code (max 64 characters): capital letters, digits and `_`, starting with a letter, Unique among roles that are not DELETED, The role `PLATFORM_ADMIN` cannot be changed                                               | CATALOG_MANAGER                      |
| 3   | description    | String       | MANDATORY | Role Description (max 256 characters)                                                                                                                                                                                                 | Manages the product catalogue        |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when no user or permission uses it | ACTIVE                               |

### Role Rules

- `name` is unique among roles that are not DELETED. The comparison is exact and a value held by an INACTIVE, LOCKED or ARCHIVED role is still taken (409, E10003). The value of a DELETED role can be used again.
- `name` is the role code: capital letters, digits and `_`, starting with a letter (max 64 characters) (400, E10001). Every field that is not optional is required in every request, including a delete and an archive.
- DELETED is final: a DELETED role is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the role again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a role. A role that is not ACTIVE is excluded when resolving new login/refresh claims; an already-issued token keeps its role snapshot until expiry (owner Q4/Q7).
- A role cannot be deleted or archived while a user (`author.t_user_role`) or a permission (`author.t_role_permission`) that is not DELETED still uses it (409, E10006). INACTIVE and LOCKED are allowed, the rows that use it are not changed.
- **`PLATFORM_ADMIN` is the system role.** It cannot be renamed, changed, deleted, archived, locked or set INACTIVE through this API: any request that names it by `id` is rejected with 409 (E10006) `System role cannot be changed.` Giving another role the name `PLATFORM_ADMIN` is a duplicate name (409, E10003). The role is created by the seed, see `e-commerce/db/seed/author.seed.sql`.
- Permission: only a platform administrator from the verified JWT roles claim can call this API; require an exact case-sensitive role name PLATFORM_ADMIN. Empty roles or other valid role names give 403 E10009 after the existence check and before conflicts. Never authorize from live author.t_user_role/author.m_role assignment queries, request flags, permission names or a separate isPlatformAdmin claim. Approved by the product owner (Q2/Q4/Q10/Q13, 2026-11-07); this supersedes the earlier live-assignment guard.
- Execution order: validate the request (400) -> verify JWT (401) -> begin transaction (READ COMMITTED) -> caller user lock -> fresh current credential check (401) -> locked target existence check (404, only for id) -> permission (403, E10009) -> system role check (409, E10006) -> duplicate check (409, E10003) -> in-use check (409, E10006, only for existing id with DELETED or ARCHIVED) -> guarded write -> map returned roleId -> COMMIT -> response. Insert skips target/system/in-use checks; every post-BEGIN rejection rolls back.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

### Credential, Concurrency and Mapping Rules

- Governing design: [owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q2/Q4/Q7/Q10/Q13/Q15. This detailed revision remains in-review; no backend/schema change is included.
- Validate one JSON object with only id/name/description/rowStatus, reject repeated keys, wrong content type, unknown query/body fields and invalid UTC timestamp before SQL (400 E10001). id is optional only by omission; if present it must be a non-empty UUID, not null. name/description are non-null, nonblank strings, at most 64/256 characters, and name matches ^[A-Z][A-Z0-9_]{0,63}$. Do not trim or case-normalize either field. rowStatus defaults to ACTIVE only when omitted and otherwise is ACTIVE/INACTIVE/DELETED/LOCKED/ARCHIVED; insert-DELETED is 400. All required fields remain mandatory even on delete/archive. Generate requestId if omitted.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub and structured roles from login. roles must be an array (including []), every role has UUID roleId and non-empty string name, and roleIds are unique. Malformed/missing roles is 401, not an empty-list fallback; verify before BEGIN. Compute callerUserId from verified sub and accessTokenHash as SHA-256 of the exact JWT. Missing/invalid credentials use generic 401 E10002 `Invalid or expired access token.`
- BEGIN READ COMMITTED and lock the caller's authen.m_user first. A missing user is 401 with rollback. Capture fresh server UTC now after that lock, recheck JWT exp, then require the matching ACTIVE token/hash/caller, strict expired_at > now and ACTIVE user from a joined current credential read. This query does not reload grants. A revoked/expired token or non-ACTIVE user is 401 before any target-role lookup. Logout/reset share the user-first lock; a request that waits for them must see their committed revocation. Grant withdrawal alone does not invalidate an otherwise-current old PLATFORM_ADMIN claim (Q4); refresh constructs a newer snapshot.
- For an existing id, lock the non-DELETED target role FOR UPDATE before the 404/403/conflict checks; concurrent deletion cannot be followed by resurrection. Use typed SQL NULL for omitted id on insert, never the string NULL. Duplicate name exclusion is null-safe and applies to all non-DELETED statuses; the current row may retain its name. Protect the system role by its stored target name before duplicate checking, not by the proposed request name. A new role named PLATFORM_ADMIN conflicts with the seeded role as 409 E10003. Reversible-status changes leave binding rows unchanged.
- Lock order is caller user -> target role -> binding checks/write. Reference/assignment writers must lock and recheck their target role before creating/reopening a binding, with target users first and role locks ordered by id; a soft lifecycle flag is not protected by a foreign key alone. The matching reference-writer migration is delivered in its own API PR; these SQL tests must not be presented as certification of an unmigrated cross-API writer. This contract does not add role grants or rewrite existing bindings.
- Check non-DELETED t_user_role and t_role_permission only for an existing target requested DELETED/ARCHIVED; either result is 409 E10006, including inactive/locked/archived bindings. Insert-ARCHIVED is allowed (201 insert); it has no prior bindings. INACTIVE/LOCKED updates may keep bindings. These are business-invariant reads, not caller authorization.
- Bind all values; createdBy/updatedBy are the verified caller UUID string and now is the fresh server value, never request fields or the supplied timestamp. INSERT explicitly sets created_at and must return exactly one role_id; missing insert result is internal 500. UPDATE is guarded by id, non-DELETED status and stored name <> PLATFORM_ADMIN; zero returned rows is 404 E10004 with rollback. One returned id must equal the requested id; an unexpected result/mapping failure is internal 500. Do not change creation audit fields on update.
- Map response data to exactly roleId from RETURNING, then COMMIT before success. Insert returns 201 S10000 Insert Role Success (also insert-ARCHIVED), existing delete returns 204 with no body/status/data, existing archive 200 S10000 Archive Role Success, other updates 200 S10000 Update Role Success. No token, caller id, row, audit fields or grants are returned.
- The partial unique index uq_m_role_name is the final concurrent duplicate guard. SQLSTATE 23505 from that constraint rolls back the whole transaction and returns 409 E10003, including races after the pre-check; other constraints/unexpected SQL/mapping failures roll back and return generic 500 with no bizCode. Timeout before COMMIT rolls back and returns 408 E90001. Never commit a partial write or return success before commit. No retry is promised after an unknown commit result.

#### Scenario correspondence with sequence.wsd

| Scenario                                                                   | Expected outcome                                         | Side effects                  |
| -------------------------------------------------------------------------- | -------------------------------------------------------- | ----------------------------- |
| Invalid input / malformed JWT or roles                                     | 400 E10001 / 401 E10002 before SQL                       | None                          |
| Missing caller, expiry during user-lock wait, revoked token, inactive user | 401 E10002 with rollback before target read              | None                          |
| Missing/DELETED target, including deletion during lock wait                | 404 E10004 before permission                             | None                          |
| Valid current token without exact PLATFORM_ADMIN claim                     | 403 E10009 after target existence (insert has no target) | None                          |
| Stored system role target                                                  | 409 E10006 before duplicate                              | None                          |
| Non-DELETED name collision / concurrent unique-index collision             | 409 E10003                                               | Whole transaction rolled back |
| Existing destructive target has any non-DELETED binding                    | 409 E10006                                               | Bindings and role unchanged   |
| Insert (including ARCHIVED)                                                | 201, exactly roleId after commit                         | One created role              |
| Update / archive / delete                                                  | 200 roleId / 200 roleId / 204 no body                    | One guarded target mutation   |
| Timeout / unexpected SQL or mapping error                                  | 408 E90001 / 500 without bizCode                         | Rollback before error         |

#### Example Body Parameters

##### Insert

```JSON
{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "name": "CATALOG_EDITOR",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "name": "CATALOG_EDITOR",
    "description": "Manages the product catalogue",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/role/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/role/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "CATALOG_MANAGER",
    "description": "Manages the product catalogue",
    "rowStatus": "ACTIVE"
}'
```

---

## Response Parameters

|     | Parameter Name | Data Type                          | M/O       | Source           | Field           | Description     | Example |
| --- | -------------- | ---------------------------------- | --------- | ---------------- | --------------- | --------------- | ------- |
| 1   | status         | [Object of Status](#status-object) | MANDATORY | Sequence Diagram | response.status | Response Status |         |
| 2   | data           | [Data of Status](#data-object)     | OPTIONAL  | Sequence Diagram | response.data   | Response Data   |         |

### Status Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                      | Description                                   | Example                                  |
| --- | -------------- | ----------------- | --------- | ---------------- | -------------------------- | --------------------------------------------- | ---------------------------------------- |
| 1   | code           | Numeric           | MANDATORY | Sequence Diagram | response.status.code       | HTTP Status Code                              | 200                                      |
| 2   | message        | String            | MANDATORY | Sequence Diagram | response.status.message    | HTTP Status Message                           | Ok                                       |
| 3   | bizCode        | String            | OPTIONAL  | Sequence Diagram | response.status.bizCode    | Business Code Success or Fail                 | S10000                                   |
| 4   | bizMessage     | String            | OPTIONAL  | Sequence Diagram | response.status.bizMessage | Business Message Success or Fail              | Success                                  |
| 5   | requestId      | String            | MANDATORY | Sequence Diagram | response.status.requestId  | API Request Id                                | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field       | Description                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------- | --------------------------------------------------------------------------- | ------------------------------------ |
| 1   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.roleId | Inserted, Updated or Archived Role Id, Not returned when deleted (HTTP 204) | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    }
}
```

#### Success - Update

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Update Role Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Success - Archive

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Archive Role Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
    }
}
```

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Name and Description are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Role name must be capital letters, digits and _, starting with a letter, at most 64 characters.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Row Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Row status must not be DELETED when inserting a role.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Unauthorized

```JSON
{
    "status": {
        "code": 401,
        "message": "Unauthorized",
        "bizCode": "E10002",
        "bizMessage": "Invalid or expired access token.",
        "requestId": "req-70a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:07:49.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You do not have permission to manage roles.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "Role not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "Role name already exists.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Role is assigned to users or has permissions.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict System Role

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "System role cannot be changed.",
        "requestId": "req-510a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:57.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Request Timeout

```JSON
{
    "status": {
        "code": 408,
        "message": "Request Timeout",
        "bizCode": "E90001",
        "bizMessage": "The server timed out waiting for the request.",
        "requestId": "req-80a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:08:56.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-role-upsert-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

All statements use bound server/request values within one READ COMMITTED transaction. callerUserId is distinct from target id. Omitted insert id is typed SQL NULL. The target role is locked before lifecycle/in-use checks; roles authorize exclusively from the verified token snapshot.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the caller user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.callerUserId>'
FOR UPDATE
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check current credential and user

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
JOIN authen.m_user u ON u.id = at.user_id
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.callerUserId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND u.row_status = 'ACTIVE'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check existing role

```SQL
SELECT
    r.id as role_id,
    r.name
FROM author.m_role r
WHERE r.id = '<sequence.id>'
AND r.row_status <> 'DELETED' -- the id of a DELETED role counts as not found
FOR UPDATE
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check system role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.id = '<sequence.id>'
AND r.name = 'PLATFORM_ADMIN' -- the request is rejected (409) when a row is found, only when id is specified
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check duplicate name

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = '<sequence.name>'
AND r.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR r.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check user in use

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.role_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND ur.row_status <> 'DELETED'
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.role_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND rp.row_status <> 'DELETED'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### INSERT - Create role

```SQL
INSERT INTO author.m_role (
    created_by,
    created_at,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.name>',
    '<sequence.description>'
)
RETURNING id as role_id
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### UPDATE - Update or delete role

```SQL
UPDATE author.m_role
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>',
    name = '<sequence.name>',
    description = '<sequence.description>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
AND name <> 'PLATFORM_ADMIN'
RETURNING id as role_id
```
