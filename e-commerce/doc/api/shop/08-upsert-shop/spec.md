# [POST]: v1/shop/upsert

| Title       | Description                                                                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Shop API                                                                                                                                                                                                                        |
| Method      | POST                                                                                                                                                                                                                                   |
| Endpoint    | v{version}/shop/upsert                                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                      |
| Description | Insert, update or delete a shop with its images, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

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
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name     | Data Type                       | M/O       | Description                                                                                                                                                                                                                                                                              | Example                                   |
| --- | ------------------ | ------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | id                 | String: UUID                    | OPTIONAL  | Shop Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop counts as not found                                                                                                                                                               | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d      |
| 2   | typeId             | String: UUID                    | MANDATORY | Shop Type Id, Must be an existing ACTIVE shop type when the shop is inserted or when the type is changed                                                                                                                                                                                 | c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f      |
| 3   | name               | String                          | MANDATORY | Shop Name (max 128 characters), Unique among shops that are not DELETED                                                                                                                                                                                                                  | Aof Fashion                               |
| 4   | description        | String                          | MANDATORY | Shop Description (max 256 characters)                                                                                                                                                                                                                                                    | Clothes and accessories for everyday wear |
| 5   | platformMarginRate | Numeric                         | OPTIONAL  | Platform margin rate in percent (0.00 to 100.00, at most 2 decimals), 0.00 when not specified on insert, Keep the current rate when not specified on update, Only a platform administrator can send a value that differs from the current one (0.00 on insert)                           | 10.00                                     |
| 6   | shopMarginRate     | Numeric                         | OPTIONAL  | Shop margin rate in percent (0.00 to 100.00, at most 2 decimals), platformMarginRate + shopMarginRate must not exceed 100.00, 0.00 when not specified on insert, Keep the current rate when not specified on update                                                                      | 5.00                                      |
| 7   | rowStatus          | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete is allowed only when the shop has no product and no order, Delete and archive need the shop administrator        | ACTIVE                                    |
| 8   | images             | [Array of Image](#image-object) | OPTIONAL  | Shop images (logo, banners, wallpaper), Each image is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, Images that are not in the list are kept, Ignored when rowStatus of the shop is DELETED (all images are deleted with the shop) |                                           |

#### Image Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                                               | Example                              |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Shop Image Id, Insert when not specified, Update or Delete when specified, Must belong to the shop and must not be duplicated in the request, The id of a DELETED image counts as not found                                                                                               | 6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e |
| 2   | type           | String       | MANDATORY | Image type (LOGO, BANNER, WALLPAPER), A shop can have only 1 LOGO and 1 WALLPAPER image that is not DELETED (to change the logo update the existing image with its id, or delete it in the same request), and up to 10 BANNER images (configurable)                                       | LOGO                                 |
| 3   | seq            | Numeric      | OPTIONAL  | Display order in the image type (integer, 0 or more), Next number of the shop and image type when not specified on insert (0 when the shop has none), Keep the current seq when not specified on update, Not unique, images with the same seq are ordered by creation time and then by id | 0                                    |
| 4   | imagePath      | String       | MANDATORY | Image Path                                                                                                                                                                                                                                                                                | /shops/aof-fashion/logo.png          |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (final, never reopened)                                                                                                                                                                 | ACTIVE                               |

### Shop Rules

- `name` is unique among shops that are not DELETED. The comparison is exact (upper and lower case are different names) and a name held by an INACTIVE, LOCKED or ARCHIVED shop is still taken (409, E10003). The name of a DELETED shop can be used again.
- `typeId`, `name` and `description` are required in every request, including a delete and an archive. `typeId` must be an ACTIVE shop type when the shop is inserted or when `typeId` changes, otherwise 404 (E10005). A shop whose shop type became INACTIVE later can still be updated while it keeps the same `typeId`.
- `platformMarginRate` and `shopMarginRate` are percentages from 0.00 to 100.00 with at most 2 decimals (400, E10001). Their sum must not exceed 100.00 (400, E10001), the ceiling was approved by the product owner and the database enforces it with the check `ck_m_shop_margin_rate_total`.
- Changing the margin rates of a shop never changes the lots that already exist (no retroactive effect): the margins of a lot are calculated when the lot is saved by the shop product SKU API, with the rates of the shop at that time.
- Insert: any caller with a valid access token can create a shop, and the caller becomes the ADMIN of the new shop (a row in `shop.t_shop_user`) in the same transaction. Update, delete and archive need the caller to be an ADMIN of the shop or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). Only a platform administrator can send a `platformMarginRate` that differs from the current one (0.00 on insert), otherwise 403 (E10009). This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.
- DELETED is final: a DELETED shop is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the shop again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a shop.
- A shop cannot be deleted while it has a product (`shop.t_shop_product` that is not DELETED) or an order (`sales.t_order` that is not DELETED), 409 (E10006). Deleting a shop deletes (soft) all of its images. Archiving is always allowed and keeps everything.
- Images follow the rule of the nested lists of the project: an image without `id` is inserted, an image with `id` is updated, `rowStatus` DELETED deletes it and images that are not in the list are kept. An `id` that does not belong to the shop is rejected with 404 (E10004), `id` must not be duplicated in the request, `type` and `imagePath` are required (400, E10001), and the id of a DELETED image counts as not found.
- Images of the same type: after the request is applied the shop can have at most 1 LOGO image and 1 WALLPAPER image that are not DELETED. INACTIVE, LOCKED and ARCHIVED images still hold the place. To replace the logo, update the existing image (send its `id`) or delete it in the same request. Sending a new LOGO or WALLPAPER image without `id` while the shop has one that stays is rejected with 409 (E10003) and a message with the type. Two images of the LOGO or WALLPAPER type that are not DELETED in the same request are rejected with 400 (E10001). The shop can have at most 10 BANNER images that are not DELETED (the maximum is configurable), otherwise 400 (E10001). The `type` of an existing image can be changed when the result follows these rules.
- A shop cannot be deleted while it is in a campaign that is not DELETED and has not ended (a live `campaign.t_campaign_shop` row of a campaign whose `end_at` is after now), 409 (E10006) with the campaign name in the message. Take it out of the campaign first with the upsert campaign API (a campaign that ended or was deleted does not block). Archiving is always allowed. (`docs/superpowers/specs/2026-11-06-campaign-design.md`, C13, approved by the product owner on 2026-11-06)
- Execution order: validate the request (400) -> existence checks (404) -> permission (403) -> duplicate name check (409, E10003) -> in-use check (409, E10006, only when `rowStatus` is DELETED) -> write the shop, the images and, for an insert, the ADMIN row.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

#### Example Body Parameters

##### Insert

```JSON
{
    "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Aof Fashion",
    "description": "Clothes and accessories for everyday wear",
    "shopMarginRate": 5.00,
    "rowStatus": "ACTIVE",
    "images": [
        {
            "type": "LOGO",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/logo.png"
        },
        {
            "type": "BANNER",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/banner-1.png"
        },
        {
            "type": "BANNER",
            "seq": 1,
            "imagePath": "/shops/aof-fashion/banner-2.png"
        }
    ]
}
```

##### Update

```JSON
{
    "id": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Aof Fashion Official",
    "description": "Clothes and accessories for everyday wear",
    "platformMarginRate": 10.00,
    "shopMarginRate": 5.00,
    "rowStatus": "ACTIVE",
    "images": [
        {
            "id": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
            "type": "LOGO",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/logo-v2.png"
        },
        {
            "id": "6b7c8d9e-0003-4b2c-8d3e-4f5a6b7c8d9e",
            "type": "BANNER",
            "seq": 1,
            "imagePath": "/shops/aof-fashion/banner-2.png",
            "rowStatus": "DELETED"
        },
        {
            "type": "BANNER",
            "seq": 2,
            "imagePath": "/shops/aof-fashion/banner-3.png"
        }
    ]
}
```

##### Delete

```JSON
{
    "id": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
    "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Aof Fashion Official",
    "description": "Clothes and accessories for everyday wear",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Aof Fashion",
    "description": "Clothes and accessories for everyday wear",
    "shopMarginRate": 5.00,
    "rowStatus": "ACTIVE",
    "images": [
        {
            "type": "LOGO",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/logo.png"
        },
        {
            "type": "BANNER",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/banner-1.png"
        },
        {
            "type": "BANNER",
            "seq": 1,
            "imagePath": "/shops/aof-fashion/banner-2.png"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "name": "Aof Fashion",
    "description": "Clothes and accessories for everyday wear",
    "shopMarginRate": 5.00,
    "rowStatus": "ACTIVE",
    "images": [
        {
            "type": "LOGO",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/logo.png"
        },
        {
            "type": "BANNER",
            "seq": 0,
            "imagePath": "/shops/aof-fashion/banner-1.png"
        },
        {
            "type": "BANNER",
            "seq": 1,
            "imagePath": "/shops/aof-fashion/banner-2.png"
        }
    ]
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field       | Description                                                                 | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------- | --------------------------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Sequence Diagram | data.shopId | Inserted, Updated or Archived Shop Id, Not returned when deleted (HTTP 204) | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Shop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
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
        "bizMessage": "Update Shop Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-05T12:50:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Success - Archive

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Archive Shop Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-05T12:57:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
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
        "bizMessage": "Type Id, Name and Description are required fields.",
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
        "bizMessage": "Row status must not be DELETED when inserting a shop.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Margin Rate

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Platform Margin Rate and Shop Margin Rate must be between 0.00 and 100.00 with at most 2 decimals.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Margin Rate Total

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "images[0]: Type must be LOGO, BANNER or WALLPAPER, Image Path is a required field, Image Id must not be duplicated.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:58.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Image

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "images[0]: Type must be LOGO, BANNER or WALLPAPER, Image Path is a required field, Image Id must not be duplicated.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Image Count

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "A shop can have at most 10 BANNER images.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:30.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Image Type

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Only one LOGO image and one WALLPAPER image are allowed in the request.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:35.123Z",
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

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You do not have permission to manage this shop.",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Forbidden Platform Margin Rate

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "Only a platform administrator can change the platform margin rate.",
        "requestId": "req-413a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:50.123Z",
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
        "bizMessage": "Shop not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Image

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "images[0]: Shop image not found.",
        "requestId": "req-414a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:20.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Shop Type

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Shop type not found.",
        "requestId": "req-424a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
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
        "bizMessage": "Shop name already exists.",
        "requestId": "req-440b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:08.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Image Type

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10003",
        "bizMessage": "The shop already has a LOGO image, update it with its id or delete it in the same request.",
        "requestId": "req-460b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:42:20.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Shop is used by products or orders.",
        "requestId": "req-450b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Campaign In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "The shop is in a campaign that has not ended (Black Friday 2026) and cannot be deleted.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Check existing shop

```SQL
SELECT
    s.id as shop_id,
    s.type_id,
    s.platform_margin_rate,
    s.shop_margin_rate
FROM shop.m_shop s
WHERE s.id = '<sequence.id>'
AND s.row_status <> 'DELETED' -- the id of a DELETED shop counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.name = '<sequence.name>'
AND s.row_status <> 'DELETED'
AND s.id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create shop

```SQL
INSERT INTO shop.m_shop (
    created_by,
    row_status,
    type_id,
    name,
    description,
    platform_margin_rate,
    shop_margin_rate
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.rowStatus>',
    '<sequence.typeId>',
    '<sequence.name>',
    '<sequence.description>',
    '<sequence.platformMarginRate>', -- 0.00 when not specified
    '<sequence.shopMarginRate>' -- 0.00 when not specified
)
RETURNING id as shop_id
```

#### UPDATE - Update, archive or delete shop

```SQL
UPDATE shop.m_shop
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    type_id = '<sequence.typeId>',
    name = '<sequence.name>',
    description = '<sequence.description>',
    platform_margin_rate = '<sequence.platformMarginRate>', -- only when platformMarginRate is specified
    shop_margin_rate = '<sequence.shopMarginRate>' -- only when shopMarginRate is specified
WHERE id = '<sequence.id>'
RETURNING id as shop_id
```

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Check shop type

```SQL
SELECT
    st.id as type_id
FROM shop.m_shop_type st
WHERE st.id = '<sequence.typeId>' -- only when the shop is inserted or typeId changes
AND st.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop administrator

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.id>'
AND su.user_id = '<sequence.userId>'
AND su.role = 'ADMIN'
AND su.row_status = 'ACTIVE'
```

#### INSERT - Add the caller as ADMIN of the new shop

```SQL
INSERT INTO shop.t_shop_user (
    created_by,
    shop_id,
    user_id,
    role
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.shopId>',
    '<sequence.userId>',
    'ADMIN'
)
RETURNING id as shop_user_id
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

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Check shop products in use

```SQL
SELECT
    sp.id as shop_product_id
FROM shop.t_shop_product sp
WHERE sp.shop_id = '<sequence.id>' -- only when rowStatus is DELETED
AND sp.row_status <> 'DELETED'
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Check shop orders in use

```SQL
SELECT
    o.id as order_id
FROM sales.t_order o
WHERE o.shop_id = '<sequence.id>' -- only when rowStatus is DELETED
AND o.row_status <> 'DELETED'
```

### Table: [shop.m_shop_image](../../../schema/shop/m_shop_image.md)

#### QUERY - Check existing shop images

```SQL
SELECT
    si.id as image_id
FROM shop.m_shop_image si
WHERE si.id IN ('<sequence.images.ids>')
AND si.shop_id = '<sequence.id>'
AND si.row_status <> 'DELETED'
```

#### QUERY - Count the images of the shop that are not in the request

```SQL
SELECT
    si.type,
    COUNT(si.id) as image_count
FROM shop.m_shop_image si
WHERE si.shop_id = '<sequence.id>'
AND si.row_status <> 'DELETED'
AND si.id NOT IN ('<sequence.images.ids>') -- only when images are specified
GROUP BY si.type
```

#### QUERY - Get next seq of the image type

```SQL
SELECT
    COALESCE(MAX(si.seq) + 1, 0) as next_seq
FROM shop.m_shop_image si
WHERE si.shop_id = '<sequence.id>'
AND si.type = '<sequence.images.type>'
AND si.row_status <> 'DELETED'
```

#### INSERT - Create shop image

```SQL
INSERT INTO shop.m_shop_image (
    created_by,
    row_status,
    shop_id,
    type,
    seq,
    image_path
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.images.rowStatus>',
    '<sequence.shopId>',
    '<sequence.images.type>',
    '<sequence.images.seq>', -- next seq of the image type when not specified
    '<sequence.images.imagePath>'
)
RETURNING id as image_id
```

#### UPDATE - Update or delete shop image

```SQL
UPDATE shop.m_shop_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.images.rowStatus>',
    type = '<sequence.images.type>',
    seq = '<sequence.images.seq>', -- only when seq is specified
    image_path = '<sequence.images.imagePath>'
WHERE id = '<sequence.images.id>'
AND shop_id = '<sequence.shopId>'
RETURNING id as image_id
```

#### UPDATE - Delete the images of a deleted shop

```SQL
UPDATE shop.m_shop_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE shop_id = '<sequence.id>' -- only when rowStatus is DELETED
AND row_status <> 'DELETED'
```

### Table: [campaign.t_campaign_shop](../../../schema/campaign/t_campaign_shop.md)

#### QUERY - Check shop campaigns in use

```SQL
SELECT
    cs.id as campaign_shop_id,
    c.name
FROM campaign.t_campaign_shop cs
INNER JOIN campaign.m_campaign c
    ON c.id = cs.campaign_id
WHERE cs.shop_id = '<sequence.id>'
AND cs.row_status <> 'DELETED'
AND c.row_status <> 'DELETED'
AND c.end_at > NOW() AT TIME ZONE 'UTC' -- a campaign that ended or was deleted does not block, answer 409 (E10006) when a row is found
LIMIT 1
```
