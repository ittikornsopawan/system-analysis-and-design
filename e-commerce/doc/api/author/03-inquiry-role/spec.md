---
name: Role Inquiry API Specification
description: Defines verified JWT administration, current credential gating, bound nullable filters and consistent read-only role pagination.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/author/role

| Title       | Description                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Role API                                                                                                                                                    |
| Method      | GET                                                                                                                                                                 |
| Endpoint    | v{version}/author/role                                                                                                                                              |
| Version     | 1                                                                                                                                                                   |
| Description | Inquiry the list of roles with paging and search, Inquiry by id returns a list with one item, Deleted roles are excluded, Only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only a platform administrator can read roles (403, E10009), because they describe the security model.
- Validate timestamp as mandatory UTC and accept only single id/pageIndex/pageSize/search/rowStatus query keys, with no body.
- search matches name OR description with existing case-insensitive ILIKE wildcard semantics.
- Verify Bearer JWT signature/issuer/audience/expiry/UUID sub and structured roles before BEGIN.
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

|     | Parameter Name | Data Type    | M/O      | Description                                                                                                | Example                              |
| --- | -------------- | ------------ | -------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Role id filter combined with other filters and normal pagination; missing/DELETED id returns an empty list | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                                  | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                         | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by role name or description                                                                         | catalog                              |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified     | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/role?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/role?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
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

|     | Parameter Name | Data Type                     | M/O       | Source           | Field           | Description                       | Example |
| --- | -------------- | ----------------------------- | --------- | ---------------- | --------------- | --------------------------------- | ------- |
| 1   | items          | [Array of Role](#role-object) | MANDATORY | Sequence Diagram | data.items      | Roles, Empty array when not found |         |
| 2   | pageIndex      | Numeric                       | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                | 1       |
| 3   | pageSize       | Numeric                       | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page          | 10      |
| 4   | totalItems     | Numeric                       | MANDATORY | Sequence Diagram | data.totalItems | Total number of items             | 2       |
| 5   | totalPages     | Numeric                       | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages             | 1       |

#### Role Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ----------------------------------------------- | ------------------------------------ |
| 1   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.items[].roleId      | Role Id                                         | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name        | Role Name                                       | CATALOG_MANAGER                      |
| 3   | description    | String       | MANDATORY | Sequence Diagram | data.items[].description | Role Description                                | Manages the product catalogue        |
| 4   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus   | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "name": "CATALOG_MANAGER",
                "description": "Manages the product catalogue",
                "rowStatus": "ACTIVE"
            },
            {
                "roleId": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "name": "SHOP_SUPPORT",
                "description": "Helps shops with their questions",
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

Request: `GET v1/author/role?id=a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Role Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "name": "CATALOG_MANAGER",
                "description": "Manages the product catalogue",
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
        "bizMessage": "Inquiry Role Success",
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
        "bizMessage": "You do not have permission to read roles.",
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
        "bizMessage": "Inquiry Role Success",
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
        "requestId": "req-role-inquiry-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

All three SELECTs share one REPEATABLE READ READ ONLY transaction; authorization is derived solely from the verified token roles, and current token/user status is read from the database. Bound nullable filters and identical role predicates apply to count and page. No locks or writes.

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

#### QUERY - Get total items

```SQL
SELECT
    COUNT(r.id) as total_items
FROM author.m_role r
WHERE r.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR r.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.searchPattern>' IS NULL OR r.name ILIKE '<sequence.searchPattern>' OR r.description ILIKE '<sequence.searchPattern>') -- only when search is specified
AND ('<sequence.rowStatus>' IS NULL OR r.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Get roles

```SQL
SELECT
    r.id as role_id,
    r.name,
    r.description,
    r.row_status
FROM author.m_role r
WHERE r.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR r.id = '<sequence.id>') -- only when id is specified
AND ('<sequence.searchPattern>' IS NULL OR r.name ILIKE '<sequence.searchPattern>' OR r.description ILIKE '<sequence.searchPattern>') -- only when search is specified
AND ('<sequence.rowStatus>' IS NULL OR r.row_status = '<sequence.rowStatus>') -- only when rowStatus is specified
ORDER BY r.name, r.id
LIMIT '<sequence.pageSize>' OFFSET '<sequence.offset>'
```
