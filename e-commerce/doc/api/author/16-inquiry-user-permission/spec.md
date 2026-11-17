---
name: User Permission Inquiry API Specification
description: Defines verified JWT administration, current credential gating, bound nullable filters and consistent read-only pagination of the permissions given directly to users with their scope; read when reviewing or implementing user permission inquiry.
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-17T20:23:48+07:00
---

# [GET]: v1/author/user/permission

| Title       | Description                                                                                                                                                                                   |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry User Permission API                                                                                                                                                                   |
| Method      | GET                                                                                                                                                                                           |
| Endpoint    | v{version}/author/user/permission                                                                                                                                                             |
| Version     | 1                                                                                                                                                                                             |
| Description | Inquiry the permissions given directly to users and their scope with paging, Inquiry by id returns a list with one item, Deleted rows are excluded, Only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Governing decisions: WP5 author design A8, A12 (5b restarted by the owner on 2026-11-17), owner answers of 2026-11-17 (Q1–Q6, relayed by Josh; Q6 approved this shape) and owner-confirmed API review Q2/Q4/Q12/Q13.
- Only a platform administrator can read the permissions of users (403, E10009), because they describe who holds which authority.
- Validate timestamp as mandatory UTC and accept only single id/userId/permissionId/pageIndex/pageSize/rowStatus query keys, with no body.
- The four nullable filters id/userId/permissionId/rowStatus disable only themselves and combine by AND; every supplied value is bound and never interpolated into SQL.
- Each item is one direct grant (`author.t_user_permission`) with its scope, the scope fields are null when the permission has no scope.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub and the roles claim before BEGIN.
- Begin REPEATABLE READ READ ONLY, capture fresh server UTC now immediately before the joined current credential/user read and recheck JWT exp.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-17T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                                   | Example                              |
| --- | -------------- | ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | User Permission Id filter combined with other filters and normal pagination; missing/DELETED id returns an empty list         | 6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d |
| 2   | userId         | String: UUID | OPTIONAL | Only the permissions of this user                                                                                             | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | permissionId   | String: UUID | OPTIONAL | Only the users that have this permission directly                                                                             | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 4   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                                     | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                                            | 10                                   |
| 6   | rowStatus      | String       | OPTIONAL | Row status filter of the user permission (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/user/permission?userId=b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e&pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-17T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/user/permission?userId=b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e&pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-17T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'
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

|     | Parameter Name | Data Type                                           | M/O       | Source           | Field           | Description                                  | Example |
| --- | -------------- | --------------------------------------------------- | --------- | ---------------- | --------------- | -------------------------------------------- | ------- |
| 1   | items          | [Array of User Permission](#user-permission-object) | MANDATORY | Sequence Diagram | data.items      | User permissions, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                             | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                           | 1       |
| 3   | pageSize       | Numeric                                             | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                     | 10      |
| 4   | totalItems     | Numeric                                             | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                        | 2       |
| 5   | totalPages     | Numeric                                             | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                        | 1       |

#### User Permission Object

|     | Parameter Name    | Data Type    | M/O       | Source           | Field                          | Description                                                                                         | Example                              |
| --- | ----------------- | ------------ | --------- | ---------------- | ------------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | userPermissionId  | String: UUID | MANDATORY | Sequence Diagram | data.items[].userPermissionId  | User Permission Id                                                                                  | 6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d |
| 2   | userId            | String: UUID | MANDATORY | Sequence Diagram | data.items[].userId            | User Id                                                                                             | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | userDisplayName   | String       | OPTIONAL  | Sequence Diagram | data.items[].userDisplayName   | Display name of the user, null when not set                                                         | John Doe                             |
| 4   | permissionId      | String: UUID | MANDATORY | Sequence Diagram | data.items[].permissionId      | Permission Id                                                                                       | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 5   | permissionName    | String       | MANDATORY | Sequence Diagram | data.items[].permissionName    | Permission Name                                                                                     | shop.manage                          |
| 6   | permissionScopeId | String: UUID | OPTIONAL  | Sequence Diagram | data.items[].permissionScopeId | Permission Scope Id (the scope definition of the permission), null when the permission has no scope | 4d5e6f7a-8b9c-4d0e-9f2a-3b4c5d6e7f8a |
| 7   | scopeId           | String: UUID | OPTIONAL  | Sequence Diagram | data.items[].scopeId           | Scope Id, null when the permission has no scope                                                     | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 8   | scope             | String       | OPTIONAL  | Sequence Diagram | data.items[].scope             | Scope Code, null when the permission has no scope                                                   | SHOP                                 |
| 9   | rowStatus         | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus         | Row status of the user permission (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                              | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-17T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userPermissionId": "7b8c9d0e-1f2a-4b3c-8d4e-5f6a7b8c9d0e",
                "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                "userDisplayName": "John Doe",
                "permissionId": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
                "permissionName": "report.read",
                "permissionScopeId": null,
                "scopeId": null,
                "scope": null,
                "rowStatus": "ACTIVE"
            },
            {
                "userPermissionId": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d",
                "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                "userDisplayName": "John Doe",
                "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
                "permissionName": "shop.manage",
                "permissionScopeId": "4d5e6f7a-8b9c-4d0e-9f2a-3b4c5d6e7f8a",
                "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
                "scope": "SHOP",
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
        "totalPages": 1
    }
}
```

#### Success - By Id

Request: `GET v1/author/user/permission?id=6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Permission Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-17T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userPermissionId": "6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c9d",
                "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                "userDisplayName": "John Doe",
                "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
                "permissionName": "shop.manage",
                "permissionScopeId": "4d5e6f7a-8b9c-4d0e-9f2a-3b4c5d6e7f8a",
                "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
                "scope": "SHOP",
                "rowStatus": "ACTIVE"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 1,
        "totalPages": 1
    }
}
```

#### Success - Not Found

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Permission Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-17T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 0,
        "totalPages": 0
    }
}
```

#### Success - Page Beyond Range

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Permission Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9d",
        "timestamp": "2026-11-17T09:25:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [],
        "pageIndex": 2,
        "pageSize": 10,
        "totalItems": 1,
        "totalPages": 1
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
        "bizMessage": "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
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
        "bizMessage": "Row status must be one of ACTIVE, INACTIVE, LOCKED, ARCHIVED.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:41:47.123Z",
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
        "bizMessage": "You do not have permission to read user permissions.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-17T09:46:22.123Z",
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
        "requestId": "req-user-permission-inquiry-review",
        "timestamp": "2026-11-17T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

All three SELECTs share one REPEATABLE READ READ ONLY transaction; authorization is derived solely from the verified token roles, and current token/user status is read from the database. Bound nullable filters and identical joins and predicates apply to count and page. No locks or writes.

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

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Get total items

```SQL
SELECT
    COUNT(up.id) as total_items
FROM author.t_user_permission up
INNER JOIN authen.m_user u
    ON u.id = up.user_id
INNER JOIN author.m_permission p
    ON p.id = up.permission_id
WHERE up.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR up.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.filterUserId>' IS NULL OR up.user_id = '<sequence.filterUserId>') -- only when userId is specified
AND ('<sequence.filterPermissionId>' IS NULL OR up.permission_id = '<sequence.filterPermissionId>') -- only when permissionId is specified
AND ('<sequence.rowStatus>' IS NULL OR up.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Get user permissions

```SQL
SELECT
    up.id as user_permission_id,
    up.user_id,
    u.display_name,
    up.permission_id,
    p.name as permission_name,
    up.permission_scope_id,
    ps.scope_id,
    s.scope,
    up.row_status
FROM author.t_user_permission up
INNER JOIN authen.m_user u
    ON u.id = up.user_id
INNER JOIN author.m_permission p
    ON p.id = up.permission_id
LEFT JOIN author.t_permission_scope ps
    ON ps.id = up.permission_scope_id
LEFT JOIN author.m_scope s
    ON s.id = ps.scope_id
WHERE up.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR up.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.filterUserId>' IS NULL OR up.user_id = '<sequence.filterUserId>') -- only when userId is specified
AND ('<sequence.filterPermissionId>' IS NULL OR up.permission_id = '<sequence.filterPermissionId>') -- only when permissionId is specified
AND ('<sequence.rowStatus>' IS NULL OR up.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
ORDER BY p.name, u.display_name, s.scope, up.id
LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'
```
