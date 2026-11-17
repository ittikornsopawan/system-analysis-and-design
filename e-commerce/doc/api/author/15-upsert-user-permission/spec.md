---
name: User Permission Upsert API Specification
description: Defines verified JWT administration, current credentials, the users/permission/grant lock order, the scope rule of a direct grant and the atomic lifecycle of a permission given directly to a user; read when reviewing or implementing user permission upsert.
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-17T20:23:48+07:00
---

# [POST]: v1/author/user/permission/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert User Permission API                                                                                                                                                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                                                                                                                                                                |
| Endpoint    | v{version}/author/user/permission/upsert                                                                                                                                                                                                                                                                                            |
| Version     | 1                                                                                                                                                                                                                                                                                                                                   |
| Description | Give a permission directly to a user in one scope, change the status of the grant or take it away, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: WP5 author design A8, A12, A13, A14, A17 (5b restarted by the owner on 2026-11-17), owner answers of 2026-11-17 (Q1–Q6, relayed by Josh) and owner-confirmed API review Q2/Q4/Q12/Q13/Q22. The owner answers supersede the implicit permissions of A2: a platform administrator holds only granted permissions.
- The caller is the user of the verified access token; only a platform administrator can call this API (403, E10009).
- **The user, the permission and the scope must be ACTIVE only when the request gives the permission**, that is an insert, or an update that sets `rowStatus` ACTIVE on a row that is not ACTIVE, otherwise 404 (E10005).
- **One grant is one permission in one scope.** A scoped permission needs `scopeId`, a scope of the permission (`author.t_permission_scope`); a permission without scopes takes no `scopeId`; otherwise 400 (E10001). To give two scopes, send two grants.
- A user can have a permission in a scope once among the rows that are not DELETED (409, E10003).
- DELETED is final: the id of a DELETED row counts as not found (404, E10004).
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

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                               | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | User Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED row counts as not found                                                                                                                      | 6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d |
| 2   | userId         | String: UUID | MANDATORY | User Id, An ACTIVE user when the permission is given (not needed to take it away), Cannot be changed by an update                                                                                                                                         | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | permissionId   | String: UUID | MANDATORY | Permission Id, An ACTIVE permission when the permission is given (not needed to take it away), Cannot be changed by an update                                                                                                                             | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 4   | scopeId        | String: UUID | OPTIONAL  | Scope Id, Required for a permission that has scopes and must be one of its scopes, Not allowed for a permission without scopes, An ACTIVE scope of the permission and an ACTIVE scope master when the permission is given, Cannot be changed by an update | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting                                                                                           | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
    "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d",
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
    "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "rowStatus": "INACTIVE"
}
```

##### Delete

```JSON
{
    "id": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d",
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
    "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/user/permission/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-17T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
    "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/user/permission/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-17T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
    "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
    "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
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
| 1   | userPermissionId | String: UUID | MANDATORY | Sequence Diagram | data.userPermissionId | Inserted, Updated or Archived User Permission Id, Not returned when deleted (HTTP 204) | 6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert User Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-17T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userPermissionId": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d"
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
        "bizMessage": "Update User Permission Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-17T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userPermissionId": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d"
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
        "bizMessage": "Archive User Permission Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-17T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userPermissionId": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d"
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
        "bizMessage": "User Id and Permission Id are required fields.",
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
        "bizMessage": "Row status must not be DELETED when inserting a user permission.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request User Permission Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "User Id, Permission Id and Scope Id cannot be changed.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:42:54.123Z",
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
        "bizMessage": "Scope is not a scope of the permission.",
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
        "bizMessage": "Scope Id is required for a permission that has scopes.",
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
        "bizMessage": "User permission not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Target User

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "User not found.",
        "requestId": "req-485a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:48:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found User Permission Or Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "User, permission or scope not found or not ACTIVE.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:48:36.123Z",
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
        "bizMessage": "The user already has this permission in this scope.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:49:43.123Z",
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
        "requestId": "req-user-permission-upsert-review",
        "timestamp": "2026-11-17T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. Caller identity (`callerUserId`) is distinct from the target user (`userId`); `userIds` is the bound typed UUID[] of both distinct ids. All values and fresh UTC time are bound. Users are locked first in ascending id order, then the permission, then the grant row. `permissionScopeId` is the definition of the permission for `scopeId`, typed SQL NULL for a permission without scopes.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the users

```SQL
SELECT
    u.id as user_id,
    u.row_status
FROM authen.m_user u
WHERE u.id = ANY ('<sequence.userIds>'::UUID[]) -- the caller and the target user, distinct
ORDER BY u.id
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

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Lock existing user permission

```SQL
SELECT
    up.id as user_permission_id,
    up.user_id,
    up.permission_id,
    up.permission_scope_id,
    up.row_status
FROM author.t_user_permission up
WHERE up.id = '<sequence.id>'
AND up.row_status <> 'DELETED' -- the id of a DELETED row counts as not found
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

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check duplicate user permission

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.user_id = '<sequence.userId>'
AND up.permission_id = '<sequence.permissionId>'
AND up.permission_scope_id IS NOT DISTINCT FROM '<sequence.permissionScopeId>' -- NULL matches NULL for a permission without scopes
AND up.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR up.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

#### INSERT - Create user permission

```SQL
INSERT INTO author.t_user_permission (
    created_by,
    created_at,
    row_status,
    user_id,
    permission_id,
    permission_scope_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.userId>',
    '<sequence.permissionId>',
    '<sequence.permissionScopeId>'
)
RETURNING id as user_permission_id
```

#### UPDATE - Update, archive or delete user permission

```SQL
UPDATE author.t_user_permission
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as user_permission_id
```
