---
name: Inquiry Product Category API Specification
description: Defines the product category list inquiry with paging and search, inquiry by id and the parent of each category; read when reviewing or implementing the product category inquiry.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/product-category

| Title       | Description                                                                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Product Category API                                                                                                                       |
| Method      | GET                                                                                                                                                |
| Endpoint    | v{version}/product-category                                                                                                                        |
| Version     | 1                                                                                                                                                  |
| Description | Inquiry the list of product categories with paging and search, Inquiry by id returns a list with one item, Deleted product categories are excluded |

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

|     | Parameter Name | Data Type    | M/O      | Description                                                     | Example                              |
| --- | -------------- | ------------ | -------- | --------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Product Category Id, Response is a list with one item           | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                       | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10              | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by product category name or product category description | computer                             |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/product-category?id=b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e&pageIndex=1&pageSize=10&search=computer HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/product-category?id=b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e&pageIndex=1&pageSize=10&search=computer' \
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

|     | Parameter Name | Data Type                                             | M/O       | Source           | Field           | Description                                    | Example |
| --- | -------------- | ----------------------------------------------------- | --------- | ---------------- | --------------- | ---------------------------------------------- | ------- |
| 1   | items          | [Array of Product Category](#product-category-object) | MANDATORY | Sequence Diagram | data.items      | Product categories, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                               | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                             | 1       |
| 3   | pageSize       | Numeric                                               | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                       | 10      |
| 4   | totalItems     | Numeric                                               | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                          | 2       |
| 5   | totalPages     | Numeric                                               | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                          | 1       |

#### Product Category Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description                                             | Example                               |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ------------------------------------------------------- | ------------------------------------- |
| 1   | categoryId     | String: UUID | MANDATORY | Sequence Diagram | data.items[].categoryId  | Product Category Id                                     | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e  |
| 2   | parentId       | String: UUID | OPTIONAL  | Sequence Diagram | data.items[].parentId    | Parent Product Category Id, Null when root category     | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d  |
| 3   | parentName     | String       | OPTIONAL  | Sequence Diagram | data.items[].parentName  | Parent Product Category Name, Null when root category   | Electronics                           |
| 4   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name        | Product Category Name                                   | Computer Accessories                  |
| 5   | slug           | String       | MANDATORY | Sequence Diagram | data.items[].slug        | Product Category Slug, Used in the web URL /{id}/{slug} | computer-accessories                  |
| 6   | description    | String       | MANDATORY | Sequence Diagram | data.items[].description | Product Category Description                            | Accessories for computers and laptops |
| 7   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus   | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)         | ACTIVE                                |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Product Category Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "parentName": "Electronics",
                "name": "Computer Accessories",
                "slug": "computer-accessories",
                "description": "Accessories for computers and laptops",
                "rowStatus": "ACTIVE"
            },
            {
                "categoryId": "d4e5f6a7-b8c9-4d0e-8f1a-2b3c4d5e6f7a",
                "parentId": null,
                "parentName": null,
                "name": "Electronics",
                "slug": "electronics",
                "description": "Electronic devices and gadgets",
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
        "bizMessage": "Inquiry Product Category Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "parentId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "parentName": "Electronics",
                "name": "Computer Accessories",
                "slug": "computer-accessories",
                "description": "Accessories for computers and laptops",
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
        "bizMessage": "Inquiry Product Category Success",
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

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Get product categories

```SQL
SELECT
    pc.id as category_id,
    pc.parent_id,
    pc.name,
    pc.slug,
    pc.description,
    pc.row_status
FROM product.m_product_category pc
WHERE pc.row_status <> 'DELETED'
AND pc.id = '<sequence.id>' -- only when id is specified
AND (pc.name ILIKE '%<sequence.search>%' OR pc.description ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY pc.created_at DESC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(pc.id) as total_items
FROM product.m_product_category pc
WHERE pc.row_status <> 'DELETED'
AND pc.id = '<sequence.id>' -- only when id is specified
AND (pc.name ILIKE '%<sequence.search>%' OR pc.description ILIKE '%<sequence.search>%') -- only when search is specified
```

#### QUERY - Get parent product categories

```SQL
SELECT
    pc.id as parent_id,
    pc.name as parent_name
FROM product.m_product_category pc
WHERE pc.id IN ('<sequence.parentIds>')
```
