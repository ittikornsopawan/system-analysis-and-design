---
name: "Upsert Shop Product Review API"
description: "Insert, update or delete the review of the caller for a product sold by a shop. Read it when you implement, review or test POST v1/shop/product-review/upsert."
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/shop/product-review/upsert

| Title       | Description                                                                                                                                                                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop Product Review API                                                                                                                                                                                                                          |
| Method      | POST                                                                                                                                                                                                                                                    |
| Endpoint    | v{version}/shop/product-review/upsert                                                                                                                                                                                                                   |
| Version     | 1                                                                                                                                                                                                                                                       |
| Description | Insert, update or delete the review of the caller for a product sold by a shop, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Only a buyer can write a review |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The rules of this section were approved by the product owner. The status COMPLETED of an order is set by the delivery API (work package WP3) that has no specification yet, so the rule that only a buyer can write a review depends on that status.
- The caller is the user of the access token, never a field of the request: a review always belongs to the caller. A caller can only change or delete a review of their own.
- The review belongs to a shop product, the product sold by that shop. A review is written only when the product page exists for the shop and the product, with the condition of the product page (shop/04): the shop is ACTIVE, the product is ACTIVE, the shop product is ACTIVE and it has at least one SKU that is ACTIVE for the shop and for the product, otherwise 404 (E10005).
- Only a buyer can write a review: when a review is inserted the caller must have an order with the status COMPLETED (`sales.t_order`) that has an item (`sales.t_order_item`) of the same shop and product, otherwise 403 (E10009). The rule is checked only when a review is inserted: the caller can always change or delete their own review.
- A user can have one review for a shop product among the reviews that are not DELETED. An insert while the caller has one is rejected with 409 (E10003), the caller changes the review with its `id`. After a delete the caller can write a new review (a new row), which needs the rule of the buyer again.
- `rating` is a whole number from 1 to 5 (400, E10001). `comment` is optional: it is trimmed, an empty comment is saved as null, and it must not be longer than 2000 characters (configurable, 400, E10001). An update replaces the comment, so a request without `comment` removes it.
- `shopId`, `productId` and `rating` are required in every request, including a delete. `rowStatus` is ACTIVE or DELETED, `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a review, and every other status (INACTIVE, LOCKED, ARCHIVED) is rejected with 400 (E10001): the customer cannot hide or archive a review and there is no moderation yet.
- `id` must be an ACTIVE review of the caller, otherwise 404 (E10004), also when the review belongs to another user. When it belongs to another shop product than `shopId` and `productId` the request is rejected with 400 (E10001). DELETED is final: the id of a DELETED review counts as not found, a review that is not ACTIVE cannot be changed or deleted by the customer.
- A review can be changed at any time, the system keeps no history: `updated_at` shows that it was changed.
- HTTP status of the upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body). There is no Archive for a customer.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                       | Example                                    |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Review Id, Insert when not specified, Update or Delete when specified, Must be an ACTIVE review of the caller for the shop and the product, otherwise 404         | 7a1b2c3d-0002-4e5f-8a6b-9c0d1e2f3a4b       |
| 2   | shopId         | String: UUID | MANDATORY | Shop Id, The shop that sells the product, Cannot be changed on update                                                                                             | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d       |
| 3   | productId      | String: UUID | MANDATORY | Product Id, The product that is reviewed, Cannot be changed on update                                                                                             | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c       |
| 4   | rating         | Numeric      | MANDATORY | Rating, A whole number from 1 to 5                                                                                                                                | 4                                          |
| 5   | comment        | String       | OPTIONAL  | Comment (max 2000 characters, configurable), Spaces at the start and the end are removed, Empty is saved as null, Not specified on update: the comment is removed | Nice shirt, the sleeves are a little long. |
| 6   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED, DELETED is not allowed when inserting, Other statuses are rejected with 400                | ACTIVE                                     |

#### Example Body Parameters

##### Insert

```JSON
{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "rating": 4,
    "comment": "Fast delivery.",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "7a1b2c3d-0002-4e5f-8a6b-9c0d1e2f3a4b",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "rating": 4,
    "comment": "Nice shirt, the sleeves are a little long.",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "7a1b2c3d-0006-4e5f-8a6b-9c0d1e2f3a4b",
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "rating": 3,
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/product-review/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "rating": 4,
    "comment": "Fast delivery.",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/product-review/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
    "rating": 4,
    "comment": "Fast delivery.",
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field         | Description                                                         | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------- | ------------------------------------------------------------------- | ------------------------------------ |
| 1   | reviewId       | String: UUID | MANDATORY | Sequence Diagram | data.reviewId | Inserted or Updated Review Id, Not returned when deleted (HTTP 204) | 7a1b2c3d-0005-4e5f-8a6b-9c0d1e2f3a4b |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Shop Product Review Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "reviewId": "7a1b2c3d-0005-4e5f-8a6b-9c0d1e2f3a4b"
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
        "bizMessage": "Update Shop Product Review Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "reviewId": "7a1b2c3d-0002-4e5f-8a6b-9c0d1e2f3a4b"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Shop Id, Product Id and Rating are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Rating

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Rating must be a whole number from 1 to 5.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Comment

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Comment must not be longer than 2000 characters.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
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
        "bizMessage": "Row status must be ACTIVE or DELETED, and must not be DELETED when inserting a review.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Shop Product Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Shop Id and Product Id cannot be changed.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.123Z",
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

#### Fail - Forbidden Not A Buyer

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You can review only a product that you have bought.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:40.123Z",
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
        "bizMessage": "Review not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Product

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Product not found.",
        "requestId": "req-414a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:09.123Z",
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
        "bizMessage": "You have already reviewed this product.",
        "requestId": "req-440b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
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

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Get the shop product that has a product page

```SQL
SELECT
    sp.id as shop_product_id
FROM shop.t_shop_product sp
INNER JOIN shop.m_shop s
    ON s.id = sp.shop_id
    AND s.row_status = 'ACTIVE'
INNER JOIN product.m_product p
    ON p.id = sp.product_id
    AND p.row_status = 'ACTIVE'
INNER JOIN shop.t_shop_product_sku ssk
    ON ssk.shop_product_id = sp.id
    AND ssk.row_status = 'ACTIVE'
INNER JOIN product.m_product_sku ps
    ON ps.id = ssk.sku_id
    AND ps.row_status = 'ACTIVE'
WHERE sp.shop_id = '<sequence.shopId>'
AND sp.product_id = '<sequence.productId>'
AND sp.row_status = 'ACTIVE'
LIMIT 1
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Check that the caller has bought the product

```SQL
SELECT
    o.id as order_id
FROM sales.t_order o
INNER JOIN sales.t_order_item oi
    ON oi.order_id = o.id
    AND oi.shop_id = '<sequence.shopId>'
    AND oi.product_id = '<sequence.productId>'
    AND oi.row_status <> 'DELETED'
WHERE o.user_id = '<sequence.userId>' -- only when a review is inserted
AND o.status = 'COMPLETED'
AND o.row_status <> 'DELETED'
LIMIT 1
```

### Table: [shop.t_shop_product_review](../../../schema/shop/t_shop_product_review.md)

#### QUERY - Check existing review

```SQL
SELECT
    r.id as review_id,
    r.shop_product_id
FROM shop.t_shop_product_review r
WHERE r.id = '<sequence.id>'
AND r.user_id = '<sequence.userId>'
AND r.row_status = 'ACTIVE' -- a review of another user, a DELETED review and a review that is not ACTIVE count as not found
```

#### QUERY - Check duplicate review

```SQL
SELECT
    r.id as review_id
FROM shop.t_shop_product_review r
WHERE r.shop_product_id = '<sequence.shopProductId>'
AND r.user_id = '<sequence.userId>'
AND r.row_status <> 'DELETED'
```

#### INSERT - Create review

```SQL
INSERT INTO shop.t_shop_product_review (
    created_by,
    row_status,
    shop_product_id,
    user_id,
    rating,
    comment
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.shopProductId>',
    '<sequence.userId>',
    '<sequence.rating>',
    '<sequence.comment>' -- null when the comment is empty
)
RETURNING id as review_id
```

#### UPDATE - Update or delete review

```SQL
UPDATE shop.t_shop_product_review
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    rating = '<sequence.rating>',
    comment = '<sequence.comment>' -- null when the comment is empty or not specified
WHERE id = '<sequence.id>'
AND user_id = '<sequence.userId>'
AND row_status = 'ACTIVE'
RETURNING id as review_id
```
