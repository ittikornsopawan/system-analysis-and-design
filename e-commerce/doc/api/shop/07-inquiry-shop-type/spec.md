---
name: "Inquiry Shop Type API"
description: "Inquiry the list of shop types with paging and search. Read it when you implement, review or test GET v1/shop/type."
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/shop/type

| Title       | Description                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Shop Type API                                                                                                              |
| Method      | GET                                                                                                                                |
| Endpoint    | v{version}/shop/type                                                                                                               |
| Version     | 1                                                                                                                                  |
| Description | Inquiry the list of shop types with paging and search, Inquiry by id returns a list with one item, Deleted shop types are excluded |

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
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                                            | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Shop Type Id, Response is a list with one item                                                         | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                              | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                     | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by shop type name or shop type description                                                      | fashion                              |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop/type?id=c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f&pageIndex=1&pageSize=10&search=fashion&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop/type?id=c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f&pageIndex=1&pageSize=10&search=fashion&rowStatus=ACTIVE' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                               | M/O       | Source           | Field           | Description                            | Example |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | --------------- | -------------------------------------- | ------- |
| 1   | items          | [Array of Shop Type](#shop-type-object) | MANDATORY | Sequence Diagram | data.items      | Shop types, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                 | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                     | 1       |
| 3   | pageSize       | Numeric                                 | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page               | 10      |
| 4   | totalItems     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                  | 2       |
| 5   | totalPages     | Numeric                                 | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                  | 1       |

#### Shop Type Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description                                     | Example                                 |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ----------------------------------------------- | --------------------------------------- |
| 1   | shopTypeId     | String: UUID | MANDATORY | Sequence Diagram | data.items[].shopTypeId  | Shop Type Id                                    | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f    |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name        | Shop Type Name                                  | Fashion Store                           |
| 3   | description    | String       | MANDATORY | Sequence Diagram | data.items[].description | Shop Type Description                           | Shops that sell clothes and accessories |
| 4   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus   | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                                  |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
                "name": "Fashion Store",
                "description": "Shops that sell clothes and accessories",
                "rowStatus": "ACTIVE"
            },
            {
                "shopTypeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
                "name": "Electronics Store",
                "description": "Shops that sell electronic devices",
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

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Type Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopTypeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
                "name": "Fashion Store",
                "description": "Shops that sell clothes and accessories",
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
        "bizMessage": "Inquiry Shop Type Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-05T12:49:00.123Z",
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
        "timestamp": "2026-11-05T12:44:40.123Z",
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
        "timestamp": "2026-11-05T12:45:47.123Z",
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
        "requestId": "req-7a2cba3e-1b2d-4caf-8cce-3b1d7b3dcb6d",
        "timestamp": "2026-11-05T12:43:10.456Z",
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
        "requestId": "req-408a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:30.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Get shop types

```SQL
SELECT
    st.id as shop_type_id,
    st.name,
    st.description,
    st.row_status
FROM shop.m_shop_type st
WHERE st.row_status <> 'DELETED'
AND st.id = '<sequence.id>' -- only when id is specified
AND (st.name ILIKE '%<sequence.search>%' OR st.description ILIKE '%<sequence.search>%') -- only when search is specified
AND st.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY st.created_at DESC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(st.id) as total_items
FROM shop.m_shop_type st
WHERE st.row_status <> 'DELETED'
AND st.id = '<sequence.id>' -- only when id is specified
AND (st.name ILIKE '%<sequence.search>%' OR st.description ILIKE '%<sequence.search>%') -- only when search is specified
AND st.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
```

