---
name: Inquiry Product Brand API Specification
description: Defines the paged list and the by-id read of product brands, the filters, the sort order and the SQL of every step; read when reviewing or implementing the product brand inquiry.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/product-brand

| Title       | Description                                                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Inquiry Product Brand API                                                                                                                  |
| Method      | GET                                                                                                                                        |
| Endpoint    | v{version}/product-brand                                                                                                                   |
| Version     | 1                                                                                                                                          |
| Description | Inquiry the list of product brands with paging and search, Inquiry by id returns a list with one item, Deleted product brands are excluded |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Any caller with a valid access token can read product brands, no role is checked (the data is only names and descriptions). Approved by the product owner (answered through the lead SA, 2026-11-06).
- Product brands with `rowStatus` DELETED are never returned. Without the `rowStatus` filter every other status is returned.
- Sorted by `created_at` descending and then by `id`, so that the pages never repeat or skip a row.

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
| 1   | id             | String: UUID | OPTIONAL | Product Brand Id, Response is a list with one item                                                     | c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                              | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                     | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by product brand name or product brand description                                              | acme                                 |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/product-brand?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/product-brand?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
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

|     | Parameter Name | Data Type                                       | M/O       | Source           | Field           | Description                                | Example |
| --- | -------------- | ----------------------------------------------- | --------- | ---------------- | --------------- | ------------------------------------------ | ------- |
| 1   | items          | [Array of Product Brand](#product-brand-object) | MANDATORY | Sequence Diagram | data.items      | Product brands, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                         | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                         | 1       |
| 3   | pageSize       | Numeric                                         | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                   | 10      |
| 4   | totalItems     | Numeric                                         | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                      | 2       |
| 5   | totalPages     | Numeric                                         | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                      | 1       |

#### Product Brand Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                       | Description                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------- | ----------------------------------------------- | ------------------------------------ |
| 1   | productBrandId | String: UUID | MANDATORY | Sequence Diagram | data.items[].productBrandId | Product Brand Id                                | c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name           | Product Brand Name                              | Acme                                 |
| 3   | description    | String       | MANDATORY | Sequence Diagram | data.items[].description    | Product Brand Description                       | Home appliances and electronics      |
| 4   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus      | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Product Brand Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "productBrandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "name": "Acme",
                "description": "Home appliances and electronics",
                "rowStatus": "ACTIVE"
            },
            {
                "productBrandId": "a3b4c5d6-e7f8-4a9b-8c0d-2e3f4a5b6c7d",
                "name": "Northwind",
                "description": "Outdoor and sports equipment",
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

Request: `GET v1/product-brand?id=c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Product Brand Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "productBrandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "name": "Acme",
                "description": "Home appliances and electronics",
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
        "bizMessage": "Inquiry Product Brand Success",
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

### Table: [product.m_product_brand](../../../schema/product/m_product_brand.md)

#### QUERY - Get product brands

```SQL
SELECT
    pb.id as product_brand_id,
    pb.name,
    pb.description,
    pb.row_status
FROM product.m_product_brand pb
WHERE pb.row_status <> 'DELETED'
AND pb.id = '<sequence.id>' -- only when id is specified
AND (pb.name ILIKE '%<sequence.search>%' OR pb.description ILIKE '%<sequence.search>%') -- only when search is specified
AND pb.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY pb.created_at DESC, pb.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(pb.id) as total_items
FROM product.m_product_brand pb
WHERE pb.row_status <> 'DELETED'
AND pb.id = '<sequence.id>' -- only when id is specified
AND (pb.name ILIKE '%<sequence.search>%' OR pb.description ILIKE '%<sequence.search>%') -- only when search is specified
AND pb.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
```
