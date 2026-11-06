# [POST]: v1/author/permission/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Permission Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Endpoint    | v{version}/author/permission/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description | Insert, update or delete multiple permissions at the same time, only a platform administrator can call it, Each permission is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All permissions are processed in one transaction in the request order, If any permission fails then no permission is changed |

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

|     | Parameter Name | Data Type                                 | M/O       | Description                                                    | Example |
| --- | -------------- | ----------------------------------------- | --------- | -------------------------------------------------------------- | ------- |
| 1   | permissions    | [Array of Permission](#permission-object) | MANDATORY | Permissions to insert, update or delete (min 1, max 100 items) |         |

#### Permission Object

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                   | Example                              |
| --- | -------------- | ------------------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED permission counts as not found, Must not be duplicated in the request | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | name           | String                          | MANDATORY | Permission Name, Permission code (max 64 characters): lower-case letters, digits, `_` and `.`, at least two parts, Unique among permissions that are not DELETED              | report.read                          |
| 3   | description    | String                          | MANDATORY | Permission Description (max 256 characters)                                                                                                                                   | Reads the platform reports           |
| 4   | scopes         | [Array of Scope](#scope-object) | OPTIONAL  | Scopes of the permission, same rules as the single upsert                                                                                                                     |                                      |
| 5   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting               | ACTIVE                               |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                    | Example                              |
| --- | -------------- | ------------ | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Permission Scope Id, Insert when not specified, Update or Delete when specified, Must belong to this permission and must not be duplicated                     | 3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f |
| 2   | scopeId        | String: UUID | MANDATORY | Scope Id, An ACTIVE scope (404 E10005), Cannot be changed when `id` is specified, The same scope must not be listed twice among the items that are not DELETED | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (not allowed when inserting), A scope that a role or user still uses cannot be deleted   | ACTIVE                               |

### Permission Rules (same as the single upsert, applied per permission)

- Every permission follows the rules of [the single upsert](../04-upsert-permission/spec.md#permission-rules): name is the permission code: lower-case letters, DELETED is final, delete and archive are rejected while a role (`author.t_role_permission`) or a user (`author.t_user_permission`) that is not DELETED still holds it.
- The permissions are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no permission is changed. `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001). The response is HTTP 200 for every successful batch, including a batch that deletes. The 403 message has no item position (the permission is the caller's, not the item's).
- `scopes` lists the scopes the permission can have (`author.t_permission_scope`). An item without `id` is added, with `id` is updated, with `rowStatus` DELETED is removed. Scopes that are not listed are kept. A scope that is not ACTIVE or does not exist is 404 (E10005). A scope cannot be deleted from the permission while a role (`author.t_role_permission_scope`) or a user (`author.t_user_permission`) still uses it (409, E10006). A permission without scopes has no scope dimension.
- Permission: only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API, any other caller gets 403 (E10009), after the existence check and before the duplicate check. Approved by the product owner (answered through the lead SA, 2026-11-06).

#### Example Body Parameters

```JSON
{
    "permissions": [
        {
            "name": "report.read",
            "description": "Reads the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/permission/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "permissions": [
        {
            "name": "report.read",
            "description": "Reads the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/permission/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "permissions": [
        {
            "name": "report.read",
            "description": "Reads the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "rowStatus": "DELETED"
        }
    ]
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field            | Description                                          | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------------- | ---------------------------------------------------- | ------- |
| 1   | permissions    | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.permissions | Result of each permission, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                           | Description                                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------------- | ---------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.permissions[].index        | Index of the permission in the request, Starting from 0    | 0                                    |
| 2   | permissionId   | String: UUID | MANDATORY | Sequence Diagram | data.permissions[].permissionId | Inserted, Updated, Deleted or Archived Permission Id       | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.permissions[].action       | Action of the permission (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permissions": [
            {
                "index": 0,
                "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
                "action": "INSERT"
            },
            {
                "index": 1,
                "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "permissionId": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
                "action": "DELETE"
            }
        ]
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
        "bizMessage": "permissions[0]: Name and Description are required fields.",
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
        "bizMessage": "permissions[1]: Permission name must be lower-case letters, digits, _ and ., with at least two parts separated by a dot, at most 64 characters.",
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
        "bizMessage": "permissions[1]: Row status must not be DELETED when inserting a permission.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Item Count

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Permissions must contain 1 to 100 items.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Id

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "permissions[2]: Id is duplicated with permissions[1].",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "permissions[2]: Name is duplicated with permissions[0].",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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
        "bizMessage": "You do not have permission to manage permissions.",
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
        "bizMessage": "permissions[1]: Permission not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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
        "bizMessage": "permissions[0]: Scope not found.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
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
        "bizMessage": "permissions[0]: Permission name already exists.",
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
        "bizMessage": "permissions[2]: Permission is used by roles or users.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Scope In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "permissions[0]: Scope is used by roles or users.",
        "requestId": "req-520a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:04.123Z",
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

---

## Database Relations

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Check existing permission

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.id = '<sequence.permissions.id>'
AND p.row_status <> 'DELETED' -- the id of a DELETED permission counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.name = '<sequence.permissions.name>'
AND p.row_status <> 'DELETED'
AND p.id <> '<sequence.permissions.id>' -- only when id is specified
```

#### INSERT - Create permission

```SQL
INSERT INTO author.m_permission (
    created_by,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.permissions.rowStatus>',
    '<sequence.permissions.name>',
    '<sequence.permissions.description>'
)
RETURNING id as permission_id
```

#### UPDATE - Update or delete permission

```SQL
UPDATE author.m_permission
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.permissions.rowStatus>',
    name = '<sequence.permissions.name>',
    description = '<sequence.permissions.description>'
WHERE id = '<sequence.permissions.id>'
RETURNING id as permission_id
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.permission_id = '<sequence.permissions.id>' -- only when rowStatus is DELETED or ARCHIVED
AND rp.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_id = '<sequence.permissions.id>' -- only when rowStatus is DELETED or ARCHIVED
AND up.row_status <> 'DELETED'
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.id = '<sequence.permissions.scopes.scopeId>'
AND s.row_status = 'ACTIVE'
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check existing permission scope

```SQL
SELECT
    ps.id as permission_scope_id,
    ps.scope_id
FROM author.t_permission_scope ps
WHERE ps.id = '<sequence.permissions.scopes.id>'
AND ps.permission_id = '<sequence.permissions.id>'
AND ps.row_status <> 'DELETED' -- only when the scope item has an id
```

#### QUERY - Check duplicate permission scope

```SQL
SELECT
    ps.id as permission_scope_id
FROM author.t_permission_scope ps
WHERE ps.permission_id = '<sequence.permissions.id>'
AND ps.scope_id = '<sequence.permissions.scopes.scopeId>'
AND ps.row_status <> 'DELETED'
AND ps.id <> '<sequence.permissions.scopes.id>' -- only when the scope item has an id
```

#### INSERT - Create permission scope

```SQL
INSERT INTO author.t_permission_scope (
    created_by,
    row_status,
    permission_id,
    scope_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.permissions.scopes.rowStatus>',
    '<sequence.permissions.id>',
    '<sequence.permissions.scopes.scopeId>'
)
RETURNING id as permission_scope_id
```

#### UPDATE - Update or delete permission scope

```SQL
UPDATE author.t_permission_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.permissions.scopes.rowStatus>'
WHERE id = '<sequence.permissions.scopes.id>'
AND permission_id = '<sequence.permissions.id>'
RETURNING id as permission_scope_id
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### QUERY - Check role permission scope in use

```SQL
SELECT
    rps.id as role_permission_scope_id
FROM author.t_role_permission_scope rps
WHERE rps.permission_scope_id = '<sequence.permissions.scopes.id>' -- only when the scope item is deleted
AND rps.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission scope in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_scope_id = '<sequence.permissions.scopes.id>' -- only when the scope item is deleted
AND up.row_status <> 'DELETED'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Get the platform administrator role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = 'PLATFORM_ADMIN'
AND r.row_status = 'ACTIVE'
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check platform administrator

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.user_id = '<sequence.userId>'
AND ur.role_id = '<sequence.roleId>'
AND ur.row_status = 'ACTIVE'
```
