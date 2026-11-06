# [POST]: v1/shop/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Upsert Shop Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Endpoint    | v{version}/shop/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Description | Insert, update or delete multiple shops with their images at the same time, Each shop is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All shops are processed in one transaction in the request order, If any shop fails then no shop is changed |

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

|     | Parameter Name | Data Type                     | M/O       | Description                                              | Example |
| --- | -------------- | ----------------------------- | --------- | -------------------------------------------------------- | ------- |
| 1   | shops          | [Array of Shop](#shop-object) | MANDATORY | Shops to insert, update or delete (min 1, max 100 items) |         |

#### Shop Object

|     | Parameter Name     | Data Type                       | M/O       | Description                                                                                                                                                                                                                                                                              | Example                                   |
| --- | ------------------ | ------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | id                 | String: UUID                    | OPTIONAL  | Shop Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED shop counts as not found, Must not be duplicated in the request                                                                                                                        | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d      |
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

### Shop Rules (same as the single upsert, applied per shop)

- Every shop follows the rules of [the single upsert](../08-upsert-shop/spec.md#shop-rules).
- `name` is unique among shops that are not DELETED. The comparison is exact (upper and lower case are different names) and a name held by an INACTIVE, LOCKED or ARCHIVED shop is still taken (409, E10003). The name of a DELETED shop can be used again.
- `typeId`, `name` and `description` are required in every request, including a delete and an archive. `typeId` must be an ACTIVE shop type when the shop is inserted or when `typeId` changes, otherwise 404 (E10005). A shop whose shop type became INACTIVE later can still be updated while it keeps the same `typeId`.
- `platformMarginRate` and `shopMarginRate` are percentages from 0.00 to 100.00 with at most 2 decimals (400, E10001). Their sum must not exceed 100.00 (400, E10001), the ceiling was approved by the product owner and the database enforces it with the check `ck_m_shop_margin_rate_total`.
- Changing the margin rates of a shop never changes the lots that already exist (no retroactive effect): the margins of a lot are calculated when the lot is saved by the shop product SKU API, with the rates of the shop at that time.
- Insert: any caller with a valid access token can create a shop, and the caller becomes the ADMIN of the new shop (a row in `shop.t_shop_user`) in the same transaction. Update, delete and archive need the caller to be an ADMIN of the shop or a platform administrator (a user that has the role `PLATFORM_ADMIN`), otherwise 403 (E10009). Only a platform administrator can send a `platformMarginRate` that differs from the current one (0.00 on insert), otherwise 403 (E10009). This permission model (the role `PLATFORM_ADMIN`, the ADMIN of the shop and the code E10009) was approved by the product owner.
- DELETED is final: a DELETED shop is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the shop again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a shop.
- A shop cannot be deleted while it has a product (`shop.t_shop_product` that is not DELETED) or an order (`sales.t_order` that is not DELETED), 409 (E10006). Deleting a shop deletes (soft) all of its images. Archiving is always allowed and keeps everything.
- Images follow the rule of the nested lists of the project: an image without `id` is inserted, an image with `id` is updated, `rowStatus` DELETED deletes it and images that are not in the list are kept. An `id` that does not belong to the shop is rejected with 404 (E10004), `id` must not be duplicated in the request, `type` and `imagePath` are required (400, E10001), and the id of a DELETED image counts as not found.
- Images of the same type: after the request is applied the shop can have at most 1 LOGO image and 1 WALLPAPER image that are not DELETED. INACTIVE, LOCKED and ARCHIVED images still hold the place. To replace the logo, update the existing image (send its `id`) or delete it in the same request. Sending a new LOGO or WALLPAPER image without `id` while the shop has one that stays is rejected with 409 (E10003) and a message with the type. Two images of the LOGO or WALLPAPER type that are not DELETED in the same request are rejected with 400 (E10001). The shop can have at most 10 BANNER images that are not DELETED (the maximum is configurable), otherwise 400 (E10001). The `type` of an existing image can be changed when the result follows these rules.
- The shops are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no shop and no image is changed.
- `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). The name of a DELETED item is not compared. Swapping the names of two shops in one request is rejected with 409 (E10003) at the first item, because that name is still held by the other shop when the item is checked. Rename them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001). The caller of a batch becomes the ADMIN of every shop that the batch inserts.
- The response is HTTP 200 for every successful batch, including a batch that deletes.
- A shop cannot be deleted while it is in a campaign that is not DELETED and has not ended (a live `campaign.t_campaign_shop` row of a campaign whose `end_at` is after now), 409 (E10006) with the campaign name in the message. Take it out of the campaign first with the upsert campaign API (a campaign that ended or was deleted does not block). Archiving is always allowed. (`docs/superpowers/specs/2026-11-06-campaign-design.md`, C13, approved by the product owner on 2026-11-06)
- Execution order of each item: validate (400) -> existence checks (404) -> permission (403) -> duplicate name (409, E10003) -> in-use check (409, E10006, only when `rowStatus` is DELETED) -> write the shop, the images and the ADMIN row.

#### Example Body Parameters

```JSON
{
    "shops": [
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
                }
            ]
        },
        {
            "id": "7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e0a",
            "typeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Gadget Hub",
            "description": "Phones, accessories and gadgets",
            "platformMarginRate": 8.50,
            "shopMarginRate": 6.00,
            "rowStatus": "ACTIVE",
            "images": [
                {
                    "id": "6b7c8d9e-0011-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "seq": 0,
                    "imagePath": "/shops/gadget-hub/logo.png"
                }
            ]
        },
        {
            "id": "8d9e0f1a-2b3c-4d4e-9f5a-6b7c8d9e0f1b",
            "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
            "name": "Old Corner Shop",
            "description": "Closed shop without products",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/shop/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "shops": [
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
                }
            ]
        },
        {
            "id": "7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e0a",
            "typeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Gadget Hub",
            "description": "Phones, accessories and gadgets",
            "platformMarginRate": 8.50,
            "shopMarginRate": 6.00,
            "rowStatus": "ACTIVE",
            "images": [
                {
                    "id": "6b7c8d9e-0011-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "seq": 0,
                    "imagePath": "/shops/gadget-hub/logo.png"
                }
            ]
        },
        {
            "id": "8d9e0f1a-2b3c-4d4e-9f5a-6b7c8d9e0f1b",
            "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
            "name": "Old Corner Shop",
            "description": "Closed shop without products",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/shop/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "shops": [
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
                }
            ]
        },
        {
            "id": "7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e0a",
            "typeId": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
            "name": "Gadget Hub",
            "description": "Phones, accessories and gadgets",
            "platformMarginRate": 8.50,
            "shopMarginRate": 6.00,
            "rowStatus": "ACTIVE",
            "images": [
                {
                    "id": "6b7c8d9e-0011-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "seq": 0,
                    "imagePath": "/shops/gadget-hub/logo.png"
                }
            ]
        },
        {
            "id": "8d9e0f1a-2b3c-4d4e-9f5a-6b7c8d9e0f1b",
            "typeId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
            "name": "Old Corner Shop",
            "description": "Closed shop without products",
            "rowStatus": "DELETED"
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field      | Description                                    | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------- | ---------------------------------------------- | ------- |
| 1   | shops          | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.shops | Result of each shop, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field               | Description                                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------- | ---------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.shops[].index  | Index of the shop in the request, Starting from 0    | 0                                    |
| 2   | shopId         | String: UUID | MANDATORY | Sequence Diagram | data.shops[].shopId | Inserted, Updated, Deleted or Archived Shop Id       | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.shops[].action | Action of the shop (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Shop Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shops": [
            {
                "index": 0,
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "shopId": "7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e0a",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "shopId": "8d9e0f1a-2b3c-4d4e-9f5a-6b7c8d9e0f1b",
                "action": "DELETE"
            }
        ]
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
        "bizMessage": "shops[1]: Type Id, Name and Description are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Item Count

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Shops must contain 1 to 100 items.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:12.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Id

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "shops[2]: Id is duplicated with shops[1].",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:20.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "shops[2]: Name is duplicated with shops[0].",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:25.123Z",
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
        "bizMessage": "shops[1]: Row status must not be DELETED when inserting a shop.",
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
        "bizMessage": "shops[1]: Platform Margin Rate and Shop Margin Rate must be between 0.00 and 100.00 with at most 2 decimals.",
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
        "bizMessage": "shops[1].images[0]: Type must be LOGO, BANNER or WALLPAPER, Image Path is a required field, Image Id must not be duplicated.",
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
        "bizMessage": "shops[1]: shops[1].images[0]: Type must be LOGO, BANNER or WALLPAPER, Image Path is a required field, Image Id must not be duplicated.",
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
        "bizMessage": "shops[1]: A shop can have at most 10 BANNER images.",
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
        "bizMessage": "shops[1]: Only one LOGO image and one WALLPAPER image are allowed in the request.",
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
        "bizMessage": "shops[1]: You do not have permission to manage this shop.",
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
        "bizMessage": "shops[1]: Only a platform administrator can change the platform margin rate.",
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
        "bizMessage": "shops[1]: Shop not found.",
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
        "bizMessage": "shops[1].images[0]: Shop image not found.",
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
        "bizMessage": "shops[1]: Shop type not found.",
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
        "bizMessage": "shops[0]: Shop name already exists.",
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
        "bizMessage": "shops[1]: The shop already has a LOGO image, update it with its id or delete it in the same request.",
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
        "bizMessage": "shops[2]: Shop is used by products or orders.",
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
        "bizMessage": "shops[2]: The shop is in a campaign that has not ended (Black Friday 2026) and cannot be deleted.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
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
WHERE s.id = '<sequence.shops.id>'
AND s.row_status <> 'DELETED' -- the id of a DELETED shop counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    s.id as shop_id
FROM shop.m_shop s
WHERE s.name = '<sequence.shops.name>'
AND s.row_status <> 'DELETED'
AND s.id <> '<sequence.shops.id>' -- only when id is specified
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
    '<sequence.shops.rowStatus>',
    '<sequence.shops.typeId>',
    '<sequence.shops.name>',
    '<sequence.shops.description>',
    '<sequence.shops.platformMarginRate>', -- 0.00 when not specified
    '<sequence.shops.shopMarginRate>' -- 0.00 when not specified
)
RETURNING id as shop_id
```

#### UPDATE - Update, archive or delete shop

```SQL
UPDATE shop.m_shop
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.shops.rowStatus>',
    type_id = '<sequence.shops.typeId>',
    name = '<sequence.shops.name>',
    description = '<sequence.shops.description>',
    platform_margin_rate = '<sequence.shops.platformMarginRate>', -- only when platformMarginRate is specified
    shop_margin_rate = '<sequence.shops.shopMarginRate>' -- only when shopMarginRate is specified
WHERE id = '<sequence.shops.id>'
RETURNING id as shop_id
```

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Check shop type

```SQL
SELECT
    st.id as type_id
FROM shop.m_shop_type st
WHERE st.id = '<sequence.shops.typeId>' -- only when the shop is inserted or typeId changes
AND st.row_status = 'ACTIVE'
```

### Table: [shop.t_shop_user](../../../schema/shop/t_shop_user.md)

#### QUERY - Check shop administrator

```SQL
SELECT
    su.id as shop_user_id
FROM shop.t_shop_user su
WHERE su.shop_id = '<sequence.shops.id>'
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
WHERE sp.shop_id = '<sequence.shops.id>' -- only when rowStatus is DELETED
AND sp.row_status <> 'DELETED'
```

### Table: [sales.t_order](../../../schema/sales/t_order.md)

#### QUERY - Check shop orders in use

```SQL
SELECT
    o.id as order_id
FROM sales.t_order o
WHERE o.shop_id = '<sequence.shops.id>' -- only when rowStatus is DELETED
AND o.row_status <> 'DELETED'
```

### Table: [shop.m_shop_image](../../../schema/shop/m_shop_image.md)

#### QUERY - Check existing shop images

```SQL
SELECT
    si.id as image_id
FROM shop.m_shop_image si
WHERE si.id IN ('<sequence.shops.images.ids>')
AND si.shop_id = '<sequence.shops.id>'
AND si.row_status <> 'DELETED'
```

#### QUERY - Count the images of the shop that are not in the request

```SQL
SELECT
    si.type,
    COUNT(si.id) as image_count
FROM shop.m_shop_image si
WHERE si.shop_id = '<sequence.shops.id>'
AND si.row_status <> 'DELETED'
AND si.id NOT IN ('<sequence.shops.images.ids>') -- only when images are specified
GROUP BY si.type
```

#### QUERY - Get next seq of the image type

```SQL
SELECT
    COALESCE(MAX(si.seq) + 1, 0) as next_seq
FROM shop.m_shop_image si
WHERE si.shop_id = '<sequence.shops.id>'
AND si.type = '<sequence.shops.images.type>'
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
    '<sequence.shops.images.rowStatus>',
    '<sequence.shopId>',
    '<sequence.shops.images.type>',
    '<sequence.shops.images.seq>', -- next seq of the image type when not specified
    '<sequence.shops.images.imagePath>'
)
RETURNING id as image_id
```

#### UPDATE - Update or delete shop image

```SQL
UPDATE shop.m_shop_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.shops.images.rowStatus>',
    type = '<sequence.shops.images.type>',
    seq = '<sequence.shops.images.seq>', -- only when seq is specified
    image_path = '<sequence.shops.images.imagePath>'
WHERE id = '<sequence.shops.images.id>'
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
WHERE shop_id = '<sequence.shops.id>' -- only when rowStatus is DELETED
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
