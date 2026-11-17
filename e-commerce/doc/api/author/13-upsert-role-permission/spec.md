---
name: Role Permission Upsert API Specification
description: Defines verified JWT administration, current credentials, the caller/role/permission/grant lock order, scope links that must be scopes of the permission, the final scoped-grant rule and the atomic lifecycle of a role permission with its scope links; read when reviewing or implementing role permission upsert.
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-17T20:23:48+07:00
---

# [POST]: v1/author/role/permission/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Role Permission API                                                                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                                                                         |
| Endpoint    | v{version}/author/role/permission/upsert                                                                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                                                                            |
| Description | Give a permission and its scopes to a role, change the status of the grant or take it away, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: WP5 author design A8, A12, A14, A17 (5b restarted by the owner on 2026-11-17), owner answers of 2026-11-17 (Q1–Q6, relayed by Josh) and owner-confirmed API review Q2/Q4/Q12/Q13/Q22. The owner answers supersede the implicit permissions of A2: `PLATFORM_ADMIN` holds only the permissions granted to it.
- The caller is the user of the verified access token; only a platform administrator can call this API (403, E10009).
- **The role and the permission must be ACTIVE only when the request gives the permission**, that is an insert, or an update that sets `rowStatus` ACTIVE on a row that is not ACTIVE, otherwise 404 (E10005).
- A role can have a permission once among the rows that are not DELETED (409, E10003).
- `scopes` are the scopes the role gets for this permission (`author.t_role_permission_scope`); each `scopeId` must be a scope of the permission (`author.t_permission_scope`), otherwise 400 (E10001). Scopes that are not listed are kept.
- **A scoped permission needs a scope.** After the whole request, an ACTIVE grant of a permission that has scopes must have at least one ACTIVE scope, otherwise 400 (E10001) and the request is rolled back.
- Deleting the grant deletes its scopes. DELETED is final: the id of a DELETED row counts as not found (404, E10004).
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-17T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                                          | Example                              |
| --- | -------------- | ------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Role Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED row counts as not found                                                                 | 8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e |
| 2   | roleId         | String: UUID                    | MANDATORY | Role Id, An ACTIVE role when the permission is given (not needed to take it away), Cannot be changed by an update                                                                                    | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | permissionId   | String: UUID                    | MANDATORY | Permission Id, An ACTIVE permission when the permission is given (not needed to take it away), Cannot be changed by an update                                                                        | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 4   | scopes         | [Array of Scope](#scope-object) | OPTIONAL  | Scopes the role gets for this permission, Each item is inserted when `id` is not specified, updated when `id` is specified, deleted when `rowStatus` is DELETED, Scopes that are not listed are kept |                                      |
| 5   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (its scopes are deleted with it), Archive when ARCHIVED, DELETED is not allowed when inserting     | ACTIVE                               |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Role Permission Scope Id, Insert when not specified, Update or Delete when specified, Must belong to this role permission and must not be duplicated                                                                                                  | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | scopeId        | String: UUID | MANDATORY | Scope Id, Must be a scope of the permission (400 E10001), An ACTIVE scope of the permission and an ACTIVE scope master when the scope is given (404 E10005), Cannot be changed when id is specified, No duplicate scope among non-DELETED input items | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (not allowed when inserting)                                                                                                                                                    | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "rowStatus": "INACTIVE"
}
```

##### Delete

```JSON
{
    "id": "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/role/permission/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-17T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/role/permission/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-17T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-17T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name   | Data Type    | M/O       | Source           | Field                 | Description                                                                            | Example                              |
| --- | ---------------- | ------------ | --------- | ---------------- | --------------------- | -------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | rolePermissionId | String: UUID | MANDATORY | Sequence Diagram | data.rolePermissionId | Inserted, Updated or Archived Role Permission Id, Not returned when deleted (HTTP 204) | 8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Role Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-17T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "rolePermissionId": "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Update Role Permission Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-17T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "rolePermissionId": "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Archive Role Permission Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-17T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "rolePermissionId": "8b9c0d1e-2f3a-4b4c-9d5e-6f7a8b9c0d1e"
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
        "bizMessage": "Role Id and Permission Id are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:40:40.123Z",
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
        "bizMessage": "Row status must not be DELETED when inserting a role permission.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Role And Permission Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Role Id and Permission Id cannot be changed.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Scope Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "scopes[0]: Scope Id cannot be changed.",
        "requestId": "req-425a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:42:58.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Scope Of Permission

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "scopes[0]: Scope is not a scope of the permission.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:43:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Scope Required

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "An ACTIVE grant of a scoped permission needs at least one ACTIVE scope.",
        "requestId": "req-435a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:43:08.123Z",
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
        "timestamp": "2026-11-17T09:07:49.123Z",
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
        "bizMessage": "You do not have permission to assign permissions.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:46:22.123Z",
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
        "bizMessage": "Role permission not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Role Permission Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "scopes[0]: Role permission scope not found.",
        "requestId": "req-475a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:47:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Role Or Permission

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Role or permission not found or not ACTIVE.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:48:36.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "scopes[0]: Scope not found or not ACTIVE.",
        "requestId": "req-485a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:48:50.123Z",
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
        "bizMessage": "The role already has this permission.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:49:43.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Scope

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "scopes[0]: The role already has this scope for the permission.",
        "requestId": "req-495a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:49:55.123Z",
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
        "timestamp": "2026-11-17T09:08:56.123Z",
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
        "requestId": "req-role-permission-upsert-review",
        "timestamp": "2026-11-17T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. All values and fresh UTC time are bound; arrays are typed UUID[]. The caller user is locked first, then the role, then the permission, then the grant row and its scope links. Scope checks and duplicate prechecks use the existing grant id (SQL NULL for an insert); scope writes and the final count use the grant id from RETURNING.

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

#### QUERY - Lock the role

```SQL
SELECT
    r.id as role_id,
    r.row_status
FROM author.m_role r
WHERE r.id = '<sequence.roleId>'
FOR UPDATE
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Lock the permission

```SQL
SELECT
    p.id as permission_id,
    p.row_status
FROM author.m_permission p
WHERE p.id = '<sequence.permissionId>'
FOR UPDATE
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Lock existing role permission

```SQL
SELECT
    rp.id as role_permission_id,
    rp.role_id,
    rp.permission_id,
    rp.row_status
FROM author.t_role_permission rp
WHERE rp.id = '<sequence.id>'
AND rp.row_status <> 'DELETED' -- the id of a DELETED row counts as not found
FOR UPDATE
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Get the scopes of the permission

```SQL
SELECT
    ps.id as permission_scope_id,
    ps.scope_id,
    ps.row_status,
    s.row_status as scope_row_status
FROM author.t_permission_scope ps
INNER JOIN author.m_scope s
    ON s.id = ps.scope_id
WHERE ps.permission_id = '<sequence.permissionId>'
AND ps.row_status <> 'DELETED' -- every scope definition of the permission, regardless of the master status
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### QUERY - Lock the scopes of the role permission

```SQL
SELECT
    rps.id as role_permission_scope_id,
    rps.permission_scope_id,
    rps.row_status
FROM author.t_role_permission_scope rps
WHERE rps.role_permission_id = '<sequence.id>' -- only when id is specified
AND rps.row_status <> 'DELETED'
ORDER BY rps.id
FOR UPDATE
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check duplicate role permission

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.role_id = '<sequence.roleId>'
AND rp.permission_id = '<sequence.permissionId>'
AND rp.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR rp.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

#### INSERT - Create role permission

```SQL
INSERT INTO author.t_role_permission (
    created_by,
    created_at,
    row_status,
    role_id,
    permission_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.roleId>',
    '<sequence.permissionId>'
)
RETURNING id as role_permission_id
```

#### UPDATE - Update, archive or delete role permission

```SQL
UPDATE author.t_role_permission
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as role_permission_id
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### INSERT - Create role permission scope

```SQL
INSERT INTO author.t_role_permission_scope (
    created_by,
    created_at,
    row_status,
    role_permission_id,
    permission_scope_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.scopes.rowStatus>',
    '<sequence.rolePermissionId>',
    '<sequence.scopes.permissionScopeId>'
)
RETURNING id as role_permission_scope_id
```

#### UPDATE - Update or delete role permission scope

```SQL
UPDATE author.t_role_permission_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.scopes.rowStatus>'
WHERE id = '<sequence.scopes.id>'
AND role_permission_id = '<sequence.rolePermissionId>'
AND row_status <> 'DELETED'
RETURNING id as role_permission_scope_id
```

#### UPDATE - Delete the scopes of a deleted role permission

```SQL
UPDATE author.t_role_permission_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = 'DELETED'
WHERE role_permission_id = '<sequence.rolePermissionId>' -- only when the grant is deleted
AND row_status <> 'DELETED'
```

#### QUERY - Count active scopes after the write

```SQL
SELECT
    COUNT(rps.id) as active_scopes
FROM author.t_role_permission_scope rps
WHERE rps.role_permission_id = '<sequence.rolePermissionId>'
AND rps.row_status = 'ACTIVE' -- 400 when 0 for an ACTIVE grant of a permission that has scopes
```
