---
name: Permission Batch Upsert API Specification
description: Defines atomic indexed permission and scope-link batch writes with JWT administration and final scoping invariants.
status: in-review
approved_by: null
approved_at: null
---

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

- Governing decisions: owner-confirmed API review Q22/Q23 (approved by the product owner).
- Every permission follows the rules of the single upsert: name is the permission code: lower-case letters, DELETED is final, delete and archive are rejected while a role (`author.t_role_permission`) or a user (`author.t_user_permission`) ...
- The permissions are processed in the request order in one transaction, so the checks of an item see the changes of the items before it.
- `scopes` lists the scopes the permission can have (`author.t_permission_scope`).
- Permission: only a platform administrator from the verified JWT roles claim can call this API; exact case-sensitive PLATFORM_ADMIN is required.
- Validate the entire request before SQL: one JSON object containing only permissions, no unknown/repeated keys or query fields, JSON content type and mandatory UTC timestamp.
- The order of the checks, the locks and every outcome is in the sequence diagram.

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

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                                                                     | Example                              |
| --- | -------------- | ------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED permission counts as not found, Must not be duplicated in the request                                                   | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | name           | String                          | MANDATORY | Permission Name, Permission code (max 64 characters): lower-case letters, digits, `_` and `.`, at least two parts, Unique among permissions that are not DELETED                                                                | report.read                          |
| 3   | description    | String                          | MANDATORY | Permission Description (max 256 characters)                                                                                                                                                                                     | Reads the platform reports           |
| 4   | scopes         | [Array of Scope](#scope-object) | OPTIONAL  | Scopes of the permission, same rules as the single upsert                                                                                                                                                                       |                                      |
| 5   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete requires zero final non-DELETED scope definitions (Q24) | ACTIVE                               |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Permission Scope Id, Insert when not specified, Update or Delete when specified, Must belong to this permission and must not be duplicated                                                                            | 3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f |
| 2   | scopeId        | String: UUID | MANDATORY | Scope Id, ACTIVE master required only for ACTIVE links (404 E10005), An owned existing link to a closed master can be removed (Q23), Immutable when id is specified, No duplicate scope among non-DELETED input items | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (not allowed when inserting), A scope that a role or user still uses cannot be deleted                                                          | ACTIVE                               |

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
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
            "rowStatus": "DELETED"
        }
    ]
}
```

The Delete item explicitly withdraws its sole remaining definition. If other non-DELETED definitions exist, include every remaining owned link; omission is not a cascade. The JSON, HTTP and cURL bodies describe the same request.

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
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
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
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
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

#### Fail - Bad Request Scope Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizMessage": "permissions[1]: Scope Id cannot be changed.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10001"
    }
}
```

#### Fail - Not Found Permission Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizMessage": "permissions[1]: Permission scope not found.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10004"
    }
}
```

#### Fail - Conflict Scope

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "permissions[1]: Scope already exists in the permission.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10003"
    }
}
```

#### Fail - Conflict Last Scope

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "permissions[1]: Permission cannot become unscoped while assigned to roles or users.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10006"
    }
}
```

#### Fail - Conflict Remaining Scopes

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "permissions[1]: Permission cannot be deleted while scope definitions remain.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10006"
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
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction for the entire batch. Every placeholder is bound. Global arrays are typed UUID[]; each item's optional request id and derived parent permissionId remain distinct from callerUserId. Before-parent queries use the verified existing parent id or typed SQL NULL for an insert; child writes/final queries use the actual returned parent UUID.

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

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Lock existing permissions

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.id = ANY ('<sequence.targetPermissionIds>'::UUID[])
AND p.row_status <> 'DELETED' -- the id of a DELETED permission counts as not found
ORDER BY p.id
FOR UPDATE
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.id = ANY ('<sequence.activeScopeIds>'::UUID[])
AND s.row_status = 'ACTIVE'
ORDER BY s.id
FOR UPDATE
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check existing permission scope

```SQL
SELECT
    ps.id as permission_scope_id,
    ps.permission_id,
    ps.scope_id
FROM author.t_permission_scope ps
WHERE ps.id = ANY ('<sequence.permissionScopeIds>'::UUID[])
AND ps.permission_id = ANY ('<sequence.targetPermissionIds>'::UUID[])
AND ps.row_status <> 'DELETED' -- supplied ids must belong to this permission
ORDER BY ps.id
FOR UPDATE
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Count permission scope definitions

```SQL
SELECT
    COUNT(ps.id) as definition_count
FROM author.t_permission_scope ps
WHERE ps.permission_id = '<sequence.permissionId>'
AND ps.row_status <> 'DELETED'
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Check duplicate name

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.name = '<sequence.permissions.name>'
AND p.row_status <> 'DELETED'
AND ('<sequence.permissions.id>' IS NULL OR p.id <> '<sequence.permissions.id>') -- omitted insert id is typed SQL NULL
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.permission_id = '<sequence.permissionId>' -- destructive parent check or final Q22 guard
AND rp.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_id = '<sequence.permissionId>' -- destructive parent check or final Q22 guard
AND up.row_status <> 'DELETED'
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check duplicate permission scope

```SQL
SELECT
    ps.id as permission_scope_id
FROM author.t_permission_scope ps
WHERE ps.permission_id = '<sequence.permissionId>'
AND ps.scope_id = '<sequence.permissions.scopes.scopeId>'
AND ps.row_status <> 'DELETED'
AND ('<sequence.permissions.scopes.id>' IS NULL OR ps.id <> '<sequence.permissions.scopes.id>') -- omitted child insert id is typed SQL NULL
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

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### INSERT - Create permission

```SQL
INSERT INTO author.m_permission (
    created_by,
    created_at,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.permissions.rowStatus>',
    '<sequence.permissions.name>',
    '<sequence.permissions.description>'
)
RETURNING id as permission_id
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### UPDATE - Update or delete permission

```SQL
UPDATE author.m_permission
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.permissions.rowStatus>',
    name = '<sequence.permissions.name>',
    description = '<sequence.permissions.description>'
WHERE id = '<sequence.permissions.id>'
AND row_status <> 'DELETED'
RETURNING id as permission_id
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### INSERT - Create permission scope

```SQL
INSERT INTO author.t_permission_scope (
    created_by,
    created_at,
    row_status,
    permission_id,
    scope_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.permissions.scopes.rowStatus>',
    '<sequence.permissionId>',
    '<sequence.permissions.scopes.scopeId>'
)
RETURNING id as permission_scope_id
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### UPDATE - Update or delete permission scope

```SQL
UPDATE author.t_permission_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.permissions.scopes.rowStatus>'
WHERE id = '<sequence.permissions.scopes.id>'
AND permission_id = '<sequence.permissionId>'
AND scope_id = '<sequence.permissions.scopes.scopeId>'
AND row_status <> 'DELETED'
RETURNING id as permission_scope_id
```
