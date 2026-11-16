---
name: "Inquiry Shop API"
description: "Inquiry the list of shops with their shop type and images, with paging, search and filters, for any caller with a valid token (verified JWT and current credential check); margin rates are shown to a member of the shop or a platform administrator from the verified roles claim. Read it when you implement, review or test GET v1/shop."
status: approved
approved_by: Ittikorn
approved_at: 2026-11-16T09:24:57+07:00
---

# [GET]: v1/shop

| Title       | Description                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Inquiry Shop API                                                                                                                                                   |
| Method      | GET                                                                                                                                                                |
| Endpoint    | v{version}/shop                                                                                                                                                    |
| Version     | 1                                                                                                                                                                  |
| Description | Inquiry the list of shops with their shop type and images, with paging, search and filters, Inquiry by id returns a list with one item, Deleted shops are excluded |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Shops with `rowStatus` DELETED and images with `rowStatus` DELETED are never returned. INACTIVE, LOCKED and ARCHIVED shops and images are returned with their `rowStatus`.
- `images` is ordered by `type` (alphabetical: BANNER, LOGO, WALLPAPER), then `seq`, then creation time, then `id` (so images with the same `seq` always come in the same order).
- Governing decisions: owner-confirmed API review Q2, Q4, Q10 and Q13 (JWT payload of 2026-11-13).
- `platformMarginRate` and `shopMarginRate` are returned only for the shops that the caller is a member of (a row of `shop.t_shop_user` with the role ADMIN or STAFF that is ACTIVE) and to a caller who has the exact case-sensitive role `PLATFORM_ADMIN` in the verified `roles` claim (an array of role names, an empty array is valid). For every other shop of the same list both fields are null and the keys are kept. This rule was approved by the product owner.
- Any caller with a valid access token can call this API: the JWT is verified and the current credential and user are checked in a read-only transaction (401, E10002), no lock is taken. The platform administrator is read only from the verified `roles` claim: do not query `author.m_role` or `author.t_user_role`, a change of the role assignments does not change a token that was already issued. Membership of a shop is not a token claim and is still read from `shop.t_shop_user`.
- The caller of the examples is an ACTIVE member of the shop `5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d` and is not a platform administrator, so the margin rates of the other shops are null.
- The public shop page of a customer is not served by this API (it needs no access token).

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
| 1   | id             | String: UUID | OPTIONAL | Shop Id, Response is a list with one item                                                              | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | typeId         | String: UUID | OPTIONAL | Shop Type Id, Only the shops of the shop type                                                          | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f |
| 3   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                                              | 1                                    |
| 4   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                                     | 10                                   |
| 5   | search         | String       | OPTIONAL | Search by shop name or shop description                                                                | fashion                              |
| 6   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE, LOCKED, ARCHIVED), All statuses except DELETED when not specified | ACTIVE                               |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/shop?id=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&typeId=c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f&pageIndex=1&pageSize=10&search=fashion&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/shop?id=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&typeId=c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f&pageIndex=1&pageSize=10&search=fashion&rowStatus=ACTIVE' \
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

|     | Parameter Name | Data Type                     | M/O       | Source           | Field           | Description                       | Example |
| --- | -------------- | ----------------------------- | --------- | ---------------- | --------------- | --------------------------------- | ------- |
| 1   | items          | [Array of Shop](#shop-object) | MANDATORY | Sequence Diagram | data.items      | Shops, Empty array when not found |         |
| 2   | pageIndex      | Numeric                       | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                | 1       |
| 3   | pageSize       | Numeric                       | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page          | 10      |
| 4   | totalItems     | Numeric                       | MANDATORY | Sequence Diagram | data.totalItems | Total number of items             | 2       |
| 5   | totalPages     | Numeric                       | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages             | 1       |

#### Shop Object

|     | Parameter Name     | Data Type                       | M/O       | Source           | Field                           | Description                                                                                                                                                         | Example                                   |
| --- | ------------------ | ------------------------------- | --------- | ---------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | shopId             | String: UUID                    | MANDATORY | Sequence Diagram | data.items[].shopId             | Shop Id                                                                                                                                                             | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d      |
| 2   | typeId             | String: UUID                    | MANDATORY | Sequence Diagram | data.items[].typeId             | Shop Type Id                                                                                                                                                        | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f      |
| 3   | typeName           | String                          | MANDATORY | Sequence Diagram | data.items[].typeName           | Shop Type Name, Returned also when the shop type is not ACTIVE                                                                                                      | Fashion Store                             |
| 4   | name               | String                          | MANDATORY | Sequence Diagram | data.items[].name               | Shop Name                                                                                                                                                           | Aof Fashion                               |
| 5   | description        | String                          | MANDATORY | Sequence Diagram | data.items[].description        | Shop Description                                                                                                                                                    | Clothes and accessories for everyday wear |
| 6   | platformMarginRate | Numeric                         | OPTIONAL  | Sequence Diagram | data.items[].platformMarginRate | Platform margin rate in percent, Null when the caller is not an ACTIVE member of the shop and not a platform administrator                                          | 10.00                                     |
| 7   | shopMarginRate     | Numeric                         | OPTIONAL  | Sequence Diagram | data.items[].shopMarginRate     | Shop margin rate in percent, Null when the caller is not an ACTIVE member of the shop and not a platform administrator                                              | 5.00                                      |
| 8   | rowStatus          | String                          | MANDATORY | Sequence Diagram | data.items[].rowStatus          | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                                                                                                                     | ACTIVE                                    |
| 9   | images             | [Array of Image](#image-object) | MANDATORY | Sequence Diagram | data.items[].images             | Images of the shop that are not DELETED, Ordered by type (alphabetical: BANNER, LOGO, WALLPAPER), seq, creation time and id, Empty array when the shop has no image |                                           |

#### Image Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                           | Description                                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------------- | ----------------------------------------------- | ------------------------------------ |
| 1   | imageId        | String: UUID | MANDATORY | Sequence Diagram | data.items[].images[].imageId   | Shop Image Id                                   | 6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e |
| 2   | type           | String       | MANDATORY | Sequence Diagram | data.items[].images[].type      | Image type (LOGO, BANNER, WALLPAPER)            | LOGO                                 |
| 3   | seq            | Numeric      | MANDATORY | Sequence Diagram | data.items[].images[].seq       | Display order in the image type                 | 0                                    |
| 4   | imagePath      | String       | MANDATORY | Sequence Diagram | data.items[].images[].imagePath | Image Path                                      | /shops/aof-fashion/logo.png          |
| 5   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].images[].rowStatus | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Shop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
                "typeName": "Fashion Store",
                "name": "Aof Fashion",
                "description": "Clothes and accessories for everyday wear",
                "platformMarginRate": 10.00,
                "shopMarginRate": 5.00,
                "rowStatus": "ACTIVE",
                "images": [
                    {
                        "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                        "type": "BANNER",
                        "seq": 0,
                        "imagePath": "/shops/aof-fashion/banner-1.png",
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                        "type": "LOGO",
                        "seq": 0,
                        "imagePath": "/shops/aof-fashion/logo.png",
                        "rowStatus": "ACTIVE"
                    }
                ]
            },
            {
                "shopId": "7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e0a",
                "typeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
                "typeName": "Electronics Store",
                "name": "Gadget Hub",
                "description": "Phones, accessories and gadgets",
                "platformMarginRate": null,
                "shopMarginRate": null,
                "rowStatus": "ACTIVE",
                "images": [
                    {
                        "imageId": "6b7c8d9e-0011-4b2c-8d3e-4f5a6b7c8d9e",
                        "type": "LOGO",
                        "seq": 0,
                        "imagePath": "/shops/gadget-hub/logo.png",
                        "rowStatus": "ACTIVE"
                    }
                ]
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
        "bizMessage": "Inquiry Shop Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
                "typeName": "Fashion Store",
                "name": "Aof Fashion",
                "description": "Clothes and accessories for everyday wear",
                "platformMarginRate": 10.00,
                "shopMarginRate": 5.00,
                "rowStatus": "ACTIVE",
                "images": [
                    {
                        "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                        "type": "BANNER",
                        "seq": 0,
                        "imagePath": "/shops/aof-fashion/banner-1.png",
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                        "type": "LOGO",
                        "seq": 0,
                        "imagePath": "/shops/aof-fashion/logo.png",
                        "rowStatus": "ACTIVE"
                    }
                ]
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
        "bizMessage": "Inquiry Shop Success",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:46:10.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One REPEATABLE READ READ ONLY transaction. The caller identity (`callerUserId`, the `sub` of the verified JWT, the same user as `userId` of the member check) is only used to check the current credential and to find the shops the caller is a member of; the fresh UTC time is bound.

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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Get shops

```SQL
SELECT
    s.id as shop_id,
    s.type_id,
    s.name,
    s.description,
    s.platform_margin_rate,
    s.shop_margin_rate,
    s.row_status
FROM shop.m_shop s
WHERE s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.type_id = '<sequence.typeId>' -- only when typeId is specified
AND (s.name ILIKE '%<sequence.search>%' OR s.description ILIKE '%<sequence.search>%') -- only when search is specified
AND s.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY s.created_at DESC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(s.id) as total_items
FROM shop.m_shop s
WHERE s.row_status <> 'DELETED'
AND s.id = '<sequence.id>' -- only when id is specified
AND s.type_id = '<sequence.typeId>' -- only when typeId is specified
AND (s.name ILIKE '%<sequence.search>%' OR s.description ILIKE '%<sequence.search>%') -- only when search is specified
AND s.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
```

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Get shop type names

```SQL
SELECT
    st.id as type_id,
    st.name as type_name
FROM shop.m_shop_type st
WHERE st.id IN ('<sequence.typeIds>')
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop members

```SQL
SELECT
    su.shop_id
FROM shop.t_shop_user su
WHERE su.shop_id IN ('<sequence.shopIds>')
AND su.user_id = '<sequence.userId>'
AND su.role IN ('ADMIN', 'STAFF')
AND su.row_status = 'ACTIVE'
```

### Table: [shop.m_shop_image](../../../schema/shop/m_shop_image.md)

#### QUERY - Get shop images

```SQL
SELECT
    si.id as image_id,
    si.shop_id,
    si.type,
    si.seq,
    si.image_path,
    si.row_status
FROM shop.m_shop_image si
WHERE si.shop_id IN ('<sequence.shopIds>')
AND si.row_status <> 'DELETED'
ORDER BY si.type, si.seq, si.created_at, si.id
```
