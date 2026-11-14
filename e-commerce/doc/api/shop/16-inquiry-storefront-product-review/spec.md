---
name: "Inquiry Storefront Product Review API"
description: "Inquiry the reviews of a product sold by a shop with the average rating and the number of reviews of each rating, with paging, rating filter and sort. Read it when you implement, review or test GET v1/storefront/product-review."
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/storefront/product-review

| Title       | Description                                                                                                                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Storefront Product Review API                                                                                                                                                        |
| Method      | GET                                                                                                                                                                                          |
| Endpoint    | v{version}/storefront/product-review                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                            |
| Description | Inquiry the reviews of a product sold by a shop with the average rating and the number of reviews of each rating, with paging, rating filter and sort, Public API, no access token is needed |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- The rules of this section were approved by the product owner.
- This API is public: it needs no access token. The reviewer is shown only by the display name and the profile picture, never by the user name, the email address or the user id.
- The reviews are listed only when the product page exists for the shop and the product, with the condition of the product page (shop/04): the shop is ACTIVE, the product is ACTIVE, the shop product is ACTIVE and it has at least one SKU that is ACTIVE for the shop and for the product, otherwise 404 (E10004). A product with a page and no review answers 200 with `items` empty, `ratingCount` 0, `averageRating` null and every count of `ratingBreakdown` 0.
- Only the reviews with `rowStatus` ACTIVE are returned and counted. The summary (`averageRating`, `ratingCount`, `ratingBreakdown`) is calculated from all the ACTIVE reviews of the shop product, it does not change with the `rating` filter or the page. `totalItems` counts the reviews after the `rating` filter.
- `averageRating` is the average of the ratings rounded half up to 2 decimals. `ratingBreakdown` has the 5 ratings from 5 down to 1, also the ones with count 0.
- `sort`: NEWEST (default) orders by `createdAt`, newest first. HIGHEST orders by rating from 5 down to 1 and LOWEST from 1 up to 5. Every sort ends with `reviewId` ascending as the tie-break, so the pages never repeat or skip a review.
- A review that was changed shows `updatedAt`, otherwise `updatedAt` is null. The comment of a review is optional.
- The reviews are about the product sold by that shop: the same product of another shop has its own reviews.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description       | Example                                  |
| --- | -------------- | --------- | --------- | ----------------- | ---------------------------------------- |
| 1   | timestamp      | DateTime  | MANDATORY | Request timestamp | 2026-11-06T09:00:00.123Z                 |
| 2   | requestId      | String    | OPTIONAL  | API Request Id    | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Query Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id                                                                                     | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | productId      | String: UUID | MANDATORY | Product Id                                                                                  | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | rating         | Numeric      | OPTIONAL  | Only the reviews with this rating (a whole number from 1 to 5), The summary is not filtered | 5                                    |
| 4   | sort           | String       | OPTIONAL  | Order of the reviews (NEWEST, HIGHEST, LOWEST), Defaults to NEWEST                          | NEWEST                               |
| 5   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1                                                   | 1                                    |
| 6   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10                                          | 10                                   |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/storefront/product-review?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&sort=NEWEST&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/storefront/product-review?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&sort=NEWEST&pageIndex=1&pageSize=10' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                            | M/O       | Source           | Field           | Description                                                  | Example |
| --- | -------------- | ------------------------------------ | --------- | ---------------- | --------------- | ------------------------------------------------------------ | ------- |
| 1   | summary        | [Object of Summary](#summary-object) | MANDATORY | Sequence Diagram | data.summary    | Summary of all the ACTIVE reviews of the product of the shop |         |
| 2   | items          | [Array of Review](#review-object)    | MANDATORY | Sequence Diagram | data.items      | Reviews, Empty array when there is none                      |         |
| 3   | pageIndex      | Numeric                              | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                                           | 1       |
| 4   | pageSize       | Numeric                              | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                                     | 10      |
| 5   | totalItems     | Numeric                              | MANDATORY | Sequence Diagram | data.totalItems | Total number of reviews after the rating filter              | 5       |
| 6   | totalPages     | Numeric                              | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                                        | 1       |

#### Summary Object

|     | Parameter Name  | Data Type                               | M/O       | Source           | Field                        | Description                                                                                                   | Example |
| --- | --------------- | --------------------------------------- | --------- | ---------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| 1   | averageRating   | Numeric                                 | OPTIONAL  | Sequence Diagram | data.summary.averageRating   | Average of the ratings of all the ACTIVE reviews, Rounded half up to 2 decimals, Null when there is no review | 4.20    |
| 2   | ratingCount     | Numeric                                 | MANDATORY | Sequence Diagram | data.summary.ratingCount     | Number of ACTIVE reviews                                                                                      | 5       |
| 3   | ratingBreakdown | [Array of Breakdown](#breakdown-object) | MANDATORY | Sequence Diagram | data.summary.ratingBreakdown | Number of reviews of each rating, Always 5 items from rating 5 down to rating 1                               |         |

#### Breakdown Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                 | Description                               | Example |
| --- | -------------- | --------- | --------- | ---------------- | ------------------------------------- | ----------------------------------------- | ------- |
| 1   | rating         | Numeric   | MANDATORY | Sequence Diagram | data.summary.ratingBreakdown[].rating | Rating (5 down to 1)                      | 5       |
| 2   | count          | Numeric   | MANDATORY | Sequence Diagram | data.summary.ratingBreakdown[].count  | Number of ACTIVE reviews with this rating | 2       |

#### Review Object

|     | Parameter Name     | Data Type         | M/O       | Source           | Field                           | Description                                                            | Example                              |
| --- | ------------------ | ----------------- | --------- | ---------------- | ------------------------------- | ---------------------------------------------------------------------- | ------------------------------------ |
| 1   | reviewId           | String: UUID      | MANDATORY | Sequence Diagram | data.items[].reviewId           | Review Id                                                              | 7a1b2c3d-0001-4e5f-8a6b-9c0d1e2f3a4b |
| 2   | rating             | Numeric           | MANDATORY | Sequence Diagram | data.items[].rating             | Rating (1 to 5)                                                        | 5                                    |
| 3   | comment            | String            | OPTIONAL  | Sequence Diagram | data.items[].comment            | Comment, Null when the reviewer wrote none                             | Soft fabric, true to size.           |
| 4   | displayName        | String            | OPTIONAL  | Sequence Diagram | data.items[].displayName        | Display name of the reviewer, Null when the user has none              | Somchai Jaidee                       |
| 5   | profilePicturePath | String            | OPTIONAL  | Sequence Diagram | data.items[].profilePicturePath | Profile picture path of the reviewer, Null when the user has none      | /users/somchai/profile.png           |
| 6   | createdAt          | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.items[].createdAt          | When the review was written (UTC)                                      | 2026-11-05T09:30:00.000Z             |
| 7   | updatedAt          | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.items[].updatedAt          | When the review was last changed (UTC), Null when it was never changed | 2026-11-05T08:00:00.000Z             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Product Review Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "summary": {
            "averageRating": 4.20,
            "ratingCount": 5,
            "ratingBreakdown": [
                {
                    "rating": 5,
                    "count": 2
                },
                {
                    "rating": 4,
                    "count": 2
                },
                {
                    "rating": 3,
                    "count": 1
                },
                {
                    "rating": 2,
                    "count": 0
                },
                {
                    "rating": 1,
                    "count": 0
                }
            ]
        },
        "items": [
            {
                "reviewId": "7a1b2c3d-0001-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": "Soft fabric, true to size.",
                "displayName": "Somchai Jaidee",
                "profilePicturePath": null,
                "createdAt": "2026-11-05T09:30:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0002-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 4,
                "comment": "Nice shirt, the sleeves are a little long.",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "createdAt": "2026-11-04T14:10:00.000Z",
                "updatedAt": "2026-11-05T08:00:00.000Z"
            },
            {
                "reviewId": "7a1b2c3d-0003-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": null,
                "displayName": "Malee Rungrat",
                "profilePicturePath": null,
                "createdAt": "2026-11-03T11:45:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0004-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 3,
                "comment": "The color is lighter than the photo.",
                "displayName": null,
                "profilePicturePath": null,
                "createdAt": "2026-11-02T16:20:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0005-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 4,
                "comment": "Fast delivery.",
                "displayName": "Nok Srisuk",
                "profilePicturePath": "/users/nok/profile.png",
                "createdAt": "2026-11-01T08:05:00.000Z",
                "updatedAt": null
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 5,
        "totalPages": 1
    }
}
```

#### Success - Highest

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Product Review Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:08:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "summary": {
            "averageRating": 4.20,
            "ratingCount": 5,
            "ratingBreakdown": [
                {
                    "rating": 5,
                    "count": 2
                },
                {
                    "rating": 4,
                    "count": 2
                },
                {
                    "rating": 3,
                    "count": 1
                },
                {
                    "rating": 2,
                    "count": 0
                },
                {
                    "rating": 1,
                    "count": 0
                }
            ]
        },
        "items": [
            {
                "reviewId": "7a1b2c3d-0001-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": "Soft fabric, true to size.",
                "displayName": "Somchai Jaidee",
                "profilePicturePath": null,
                "createdAt": "2026-11-05T09:30:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0003-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": null,
                "displayName": "Malee Rungrat",
                "profilePicturePath": null,
                "createdAt": "2026-11-03T11:45:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0002-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 4,
                "comment": "Nice shirt, the sleeves are a little long.",
                "displayName": "Aof Sopawan",
                "profilePicturePath": "/users/aof/profile.png",
                "createdAt": "2026-11-04T14:10:00.000Z",
                "updatedAt": "2026-11-05T08:00:00.000Z"
            },
            {
                "reviewId": "7a1b2c3d-0005-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 4,
                "comment": "Fast delivery.",
                "displayName": "Nok Srisuk",
                "profilePicturePath": "/users/nok/profile.png",
                "createdAt": "2026-11-01T08:05:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0004-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 3,
                "comment": "The color is lighter than the photo.",
                "displayName": null,
                "profilePicturePath": null,
                "createdAt": "2026-11-02T16:20:00.000Z",
                "updatedAt": null
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 5,
        "totalPages": 1
    }
}
```

#### Success - Rating Filter

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Product Review Success",
        "requestId": "req-8a1b2c3d-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:08:30.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "summary": {
            "averageRating": 4.20,
            "ratingCount": 5,
            "ratingBreakdown": [
                {
                    "rating": 5,
                    "count": 2
                },
                {
                    "rating": 4,
                    "count": 2
                },
                {
                    "rating": 3,
                    "count": 1
                },
                {
                    "rating": 2,
                    "count": 0
                },
                {
                    "rating": 1,
                    "count": 0
                }
            ]
        },
        "items": [
            {
                "reviewId": "7a1b2c3d-0001-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": "Soft fabric, true to size.",
                "displayName": "Somchai Jaidee",
                "profilePicturePath": null,
                "createdAt": "2026-11-05T09:30:00.000Z",
                "updatedAt": null
            },
            {
                "reviewId": "7a1b2c3d-0003-4e5f-8a6b-9c0d1e2f3a4b",
                "rating": 5,
                "comment": null,
                "displayName": "Malee Rungrat",
                "profilePicturePath": null,
                "createdAt": "2026-11-03T11:45:00.000Z",
                "updatedAt": null
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 2,
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
        "bizMessage": "Inquiry Storefront Product Review Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:09:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "summary": {
            "averageRating": null,
            "ratingCount": 0,
            "ratingBreakdown": [
                {
                    "rating": 5,
                    "count": 0
                },
                {
                    "rating": 4,
                    "count": 0
                },
                {
                    "rating": 3,
                    "count": 0
                },
                {
                    "rating": 2,
                    "count": 0
                },
                {
                    "rating": 1,
                    "count": 0
                }
            ]
        },
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
        "bizMessage": "Shop Id and Product Id are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:04:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Paging

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Page Index and Page Size must be greater than 0, Page Size must not be greater than 100.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:05:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Rating Or Sort

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Rating must be a whole number from 1 to 5 and Sort must be one of NEWEST, HIGHEST, LOWEST.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:54.123Z",
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
        "bizMessage": "Product not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:54.321Z",
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
        "timestamp": "2026-11-06T09:05:30.123Z",
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

### Table: [shop.t_shop_product_review](../../../schema/shop/t_shop_product_review.md)

#### QUERY - Get the summary of the reviews

```SQL
SELECT
    COUNT(r.id) as rating_count,
    ROUND(AVG(r.rating), 2) as average_rating
FROM shop.t_shop_product_review r
WHERE r.shop_product_id = '<sequence.shopProductId>'
AND r.row_status = 'ACTIVE'
```

#### QUERY - Get the number of reviews of each rating

```SQL
SELECT
    r.rating,
    COUNT(r.id) as rating_count
FROM shop.t_shop_product_review r
WHERE r.shop_product_id = '<sequence.shopProductId>'
AND r.row_status = 'ACTIVE'
GROUP BY r.rating
ORDER BY r.rating DESC
```

#### QUERY - Get reviews

```SQL
SELECT
    r.id as review_id,
    r.rating,
    r.comment,
    u.display_name,
    u.profile_picture_path,
    r.created_at,
    r.updated_at
FROM shop.t_shop_product_review r
INNER JOIN authen.m_user u
    ON u.id = r.user_id
WHERE r.shop_product_id = '<sequence.shopProductId>'
AND r.row_status = 'ACTIVE'
AND r.rating = '<sequence.rating>' -- only when rating is specified
ORDER BY r.created_at DESC, r.id -- sort NEWEST (default)
-- ORDER BY r.rating DESC, r.id (sort HIGHEST)
-- ORDER BY r.rating, r.id (sort LOWEST)
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(r.id) as total_items
FROM shop.t_shop_product_review r
WHERE r.shop_product_id = '<sequence.shopProductId>'
AND r.row_status = 'ACTIVE'
AND r.rating = '<sequence.rating>' -- only when rating is specified
```

### Table: [authen.m_user](../../../schema/authen/m_user.md)

The display name and the profile picture come from the join of the query "Get reviews", the user name and the email address are not selected.
