# [GET]: v1/author/scope

| Title       | Description                                                                                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Scope API                                                                                                                                                     |
| Method      | GET                                                                                                                                                                   |
| Endpoint    | v{version}/author/scope                                                                                                                                               |
| Version     | 1                                                                                                                                                                     |
| Description | Inquiry the list of scopes with paging and search, Inquiry by id returns a list with one item, Deleted scopes are excluded, Only a platform administrator can call it |

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
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                            | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Scope Id, Response is a list with one item                                                             | a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                              | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                     | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by scope scope or description                                                                   | region                               |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

### Scope Inquiry Rules

- Only a platform administrator can read scopes (403, E10009), because they describe the security model. Approved by the product owner (answered through the lead SA, 2026-11-06).
- Scopes with `rowStatus` DELETED are never returned. Sorted by `scope` and then by `id`, so that pages never repeat or skip a row.
- Execution order: validate the request (400) -> permission (403) -> read.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/scope?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/scope?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
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

|     | Parameter Name | Data Type                       | M/O       | Source           | Field           | Description                        | Example |
| --- | -------------- | ------------------------------- | --------- | ---------------- | --------------- | ---------------------------------- | ------- |
| 1   | items          | [Array of Scope](#scope-object) | MANDATORY | Sequence Diagram | data.items      | Scopes, Empty array when not found |         |
| 2   | pageIndex      | Numeric                         | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                 | 1       |
| 3   | pageSize       | Numeric                         | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page           | 10      |
| 4   | totalItems     | Numeric                         | MANDATORY | Sequence Diagram | data.totalItems | Total number of items              | 2       |
| 5   | totalPages     | Numeric                         | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages              | 1       |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ----------------------------------------------- | ------------------------------------ |
| 1   | scopeId        | String: UUID | MANDATORY | Sequence Diagram | data.items[].scopeId     | Scope Id                                        | a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d |
| 2   | scope          | String       | MANDATORY | Sequence Diagram | data.items[].scope       | Scope Scope                                     | REGION                               |
| 3   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name        | Scope Name                                      | Region                               |
| 4   | description    | String       | MANDATORY | Sequence Diagram | data.items[].description | Scope Description                               | The shops of one region              |
| 5   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus   | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Scope Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d",
                "scope": "REGION",
                "name": "Region",
                "description": "The shops of one region",
                "rowStatus": "ACTIVE"
            },
            {
                "scopeId": "b8c9d0e1-f2a3-4b4c-9d5e-6f7a8b9c0d1e",
                "scope": "TEAM",
                "name": "Team",
                "description": "The members of one team",
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

Request: `GET v1/author/scope?id=a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Scope Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "scopeId": "a7b8c9d0-e1f2-4a3b-8c4d-5e6f7a8b9c0d",
                "scope": "REGION",
                "name": "Region",
                "description": "The shops of one region",
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
        "bizMessage": "Inquiry Scope Success",
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
        "bizMessage": "You do not have permission to read scopes.",
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

---

## Database Relations

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Get scopes

```SQL
SELECT
    s.id as scope_id,
    s.scope,
    s.name,
    s.description,
    s.row_status
FROM author.m_scope s
WHERE s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND (s.scope ILIKE '%<sequence.search>%' OR s.description ILIKE '%<sequence.search>%') -- only when search is specified
AND s.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY s.scope, s.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(s.id) as total_items
FROM author.m_scope s
WHERE s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND (s.scope ILIKE '%<sequence.search>%' OR s.description ILIKE '%<sequence.search>%') -- only when search is specified
AND s.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
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
