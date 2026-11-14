---
name: User Role Inquiry API Specification
description: Defines verified JWT administration, current credential gating, bound nullable filters and consistent read-only user role pagination; read when reviewing or implementing user role inquiry.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/author/user/role

| Title       | Description                                                                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry User Role API                                                                                                                                    |
| Method      | GET                                                                                                                                                      |
| Endpoint    | v{version}/author/user/role                                                                                                                              |
| Version     | 1                                                                                                                                                        |
| Description | Inquiry the roles of users with paging, Inquiry by id returns a list with one item, Deleted rows are excluded, Only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only a platform administrator can read the roles of users (403, E10009), because they describe who holds which authority.
- Validate timestamp as mandatory UTC and accept only single id/userId/roleId/pageIndex/pageSize/rowStatus query keys, with no body.
- The four nullable filters id/userId/roleId/rowStatus disable only themselves and combine by AND; every supplied value is bound and never interpolated into SQL.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub and the roles claim before BEGIN.
- Begin REPEATABLE READ READ ONLY, capture fresh server UTC now immediately before the joined current credential/user read and recheck JWT exp.
- The order of the checks, the locks and every outcome is in the sequence diagram.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                     | Example                              |
| --- | -------------- | ------------ | -------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | User Role Id filter combined with other filters and normal pagination; missing/DELETED id returns an empty list | 5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | userId         | String: UUID | OPTIONAL | Only the roles of this user                                                                                     | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | roleId         | String: UUID | OPTIONAL | Only the users that have this role                                                                              | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 4   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                       | 1                                    |
| 5   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                              | 10                                   |
| 6   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified          | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/user/role?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/user/role?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                               | M/O       | Source           | Field           | Description                            | Example |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | --------------- | -------------------------------------- | ------- |
| 1   | items          | [Array of User Role](#user-role-object) | MANDATORY | Sequence Diagram | data.items      | User roles, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                 | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                     | 1       |
| 3   | pageSize       | Numeric                                 | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page               | 10      |
| 4   | totalItems     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                  | 2       |
| 5   | totalPages     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                  | 1       |

#### User Role Object

|     | Parameter Name  | Data Type    | M/O       | Source           | Field                        | Description                                     | Example                              |
| --- | --------------- | ------------ | --------- | ---------------- | ---------------------------- | ----------------------------------------------- | ------------------------------------ |
| 1   | userRoleId      | String: UUID | MANDATORY | Sequence Diagram | data.items[].userRoleId      | User Role Id                                    | 5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | userId          | String: UUID | MANDATORY | Sequence Diagram | data.items[].userId          | User Id                                         | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 3   | userDisplayName | String       | OPTIONAL  | Sequence Diagram | data.items[].userDisplayName | Display name of the user, null when not set     | John Doe                             |
| 4   | roleId          | String: UUID | MANDATORY | Sequence Diagram | data.items[].roleId          | Role Id                                         | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 5   | roleName        | String       | MANDATORY | Sequence Diagram | data.items[].roleName        | Role Name                                       | CATALOG_MANAGER                      |
| 6   | rowStatus       | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus       | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userRoleId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
                "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                "userDisplayName": "John Doe",
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "roleName": "CATALOG_MANAGER",
                "rowStatus": "ACTIVE"
            },
            {
                "userRoleId": "7a8b9c0d-1e2f-4a3b-8c4d-5e6f7a8b9c0e",
                "userId": "c2d3e4f5-a6b7-4c8d-9e0f-1a2b3c4d5e6f",
                "userDisplayName": "Jane Roe",
                "roleId": "6f7a8b9c-0d1e-4f2a-9b3c-4d5e6f7a8b9c",
                "roleName": "PLATFORM_ADMIN",
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

Request: `GET v1/author/user/role?id=5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Role Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userRoleId": "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b",
                "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
                "userDisplayName": "John Doe",
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "roleName": "CATALOG_MANAGER",
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
        "bizMessage": "Inquiry User Role Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:20:00.123Z",
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

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "You do not have permission to read user roles.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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

#### Success - Page Beyond Range

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Role Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-user-role-inquiry-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
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

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Get total items

```SQL
SELECT
    COUNT(ur.id) as total_items
FROM author.t_user_role ur
INNER JOIN authen.m_user u
    ON u.id = ur.user_id
INNER JOIN author.m_role r
    ON r.id = ur.role_id
WHERE ur.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR ur.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.filterUserId>' IS NULL OR ur.user_id = '<sequence.filterUserId>') -- only when userId is specified
AND ('<sequence.filterRoleId>' IS NULL OR ur.role_id = '<sequence.filterRoleId>') -- only when roleId is specified
AND ('<sequence.rowStatus>' IS NULL OR ur.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Get user roles

```SQL
SELECT
    ur.id as user_role_id,
    ur.user_id,
    u.display_name,
    ur.role_id,
    r.name as role_name,
    ur.row_status
FROM author.t_user_role ur
INNER JOIN authen.m_user u
    ON u.id = ur.user_id
INNER JOIN author.m_role r
    ON r.id = ur.role_id
WHERE ur.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR ur.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.filterUserId>' IS NULL OR ur.user_id = '<sequence.filterUserId>') -- only when userId is specified
AND ('<sequence.filterRoleId>' IS NULL OR ur.role_id = '<sequence.filterRoleId>') -- only when roleId is specified
AND ('<sequence.rowStatus>' IS NULL OR ur.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
ORDER BY r.name, u.display_name, ur.id
LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'
```
