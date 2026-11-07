# [POST]: v1/product/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Product Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Endpoint    | v{version}/product/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Description | Insert, update or delete multiple products at the same time, Each product is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), Each product can define options (levels) with values and SKUs are generated from them, All products are processed in one transaction, If any product fails then no product is changed, only a platform administrator can call it |

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

|     | Parameter Name | Data Type                           | M/O       | Description                                                 | Example |
| --- | -------------- | ----------------------------------- | --------- | ----------------------------------------------------------- | ------- |
| 1   | products       | [Array of Product](#product-object) | MANDATORY | Products to insert, update or delete (min 1, max 100 items) |         |

#### Product Object

|     | Parameter Name | Data Type                               | M/O       | Description                                                                                                                                                                                                                                                                                                                                                                                                         | Example                                                       |
| --- | -------------- | --------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1   | id             | String: UUID                            | OPTIONAL  | Product Id, Insert when not specified, Update or Delete when specified, Must not be duplicated in the request                                                                                                                                                                                                                                                                                                       | f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d                          |
| 2   | typeId         | String: UUID                            | MANDATORY | Product Type Id                                                                                                                                                                                                                                                                                                                                                                                                     | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d                          |
| 3   | categoryId     | String: UUID                            | MANDATORY | Product Category Id                                                                                                                                                                                                                                                                                                                                                                                                 | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e                          |
| 4   | brandId        | String: UUID                            | MANDATORY | Product Brand Id                                                                                                                                                                                                                                                                                                                                                                                                    | c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f                          |
| 5   | name           | String                                  | MANDATORY | Product Name (max 128 characters)                                                                                                                                                                                                                                                                                                                                                                                   | Wireless Mouse                                                |
| 6   | slug           | String                                  | OPTIONAL  | URL friendly name (max 128 characters, a-z, 0-9 and hyphen), Used in the web URL /{id}/{slug}, Generated from name when not specified on insert, Keep the current slug when not specified on update                                                                                                                                                                                                                 | wireless-mouse                                                |
| 7   | description    | String                                  | MANDATORY | Product Description (max 256 characters)                                                                                                                                                                                                                                                                                                                                                                            | Ergonomic wireless mouse with 2.4GHz receiver                 |
| 8   | body           | String                                  | MANDATORY | Product Detail                                                                                                                                                                                                                                                                                                                                                                                                      | Ergonomic design, silent click, battery life up to 12 months. |
| 9   | rowStatus      | String                                  | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED                                                                                                                                                                                                                                                                                            | ACTIVE                                                        |
| 10  | attributes     | [Array of Attribute](#attribute-object) | OPTIONAL  | Product attributes, Replace all attributes of the product when specified (attributes that are not in the list are deleted), Keep the current attributes when not specified, Required when category is changed on update, Each attribute id must not be duplicated                                                                                                                                                   |                                                               |
| 11  | images         | [Array of Image](#image-object)         | OPTIONAL  | Product level images, Images of option values are in options[].values[].images, Each image is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, Images that are not in the list are kept, Id must belong to the product and must not be duplicated                                                                                                                |                                                               |
| 12  | options        | [Array of Option](#option-object)       | OPTIONAL  | Product options (levels), Specified: the complete definition of the options of the product (options that are not in the list are deleted together with their values and the SKUs that use them are closed), Not specified: keep the current options, Maximum 3 levels (configurable), Level number is the position in the array ignoring DELETED options, Empty array deletes all levels and leaves one default SKU |                                                               |

#### Attribute Object

|     | Parameter Name | Data Type    | M/O       | Description                                                        | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------ | ------------------------------------ |
| 1   | attributeId    | String: UUID | MANDATORY | Product Category Attribute Id, Must belong to the product category | 11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d |
| 2   | value          | String       | MANDATORY | Attribute Value (max 256 characters)                               | Black                                |

#### Image Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Product Image Id, Insert when not specified, Update or Delete when specified, Must belong to the product and must be a product level image | 33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f |
| 2   | imagePath      | String       | MANDATORY | Image Path                                                                                                                                 | /products/wireless-mouse/1.png       |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED                                          | ACTIVE                               |

#### Option Object

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                                                   | Example                              |
| --- | -------------- | ------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Product Option Id, Insert when not specified, Update or Delete when specified, Must belong to the product and must not be duplicated                                                                          | 55e6f7a8-0005-4e4f-8a5b-6c7d8e9fa0b1 |
| 2   | name           | String                          | MANDATORY | Option Name (max 128 characters), Must not be duplicated in the product                                                                                                                                       | Color                                |
| 3   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED, DELETED is final (never reopened) and deletes the values of the option, Other statuses are rejected with 400                           | ACTIVE                               |
| 4   | values         | [Array of Value](#value-object) | MANDATORY | Option values, Replace all values of the option (values that are not in the list are deleted), Must contain at least 1 value that is not DELETED, The position in the array is the display order of the value |                                      |

#### Value Object

|     | Parameter Name | Data Type                                   | M/O       | Description                                                                                                                                                                                                                                                                       | Example                              |
| --- | -------------- | ------------------------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                                | OPTIONAL  | Product Option Value Id, Insert when not specified, Update or Delete when specified, Must belong to the option and must not be duplicated                                                                                                                                         | dda4b5c6-0013-4ac1-8cd3-e4f5a6b7c8d9 |
| 2   | value          | String                                      | MANDATORY | Option Value (max 128 characters), Must not be duplicated in the option                                                                                                                                                                                                           | Red                                  |
| 3   | rowStatus      | String                                      | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED (final, never reopened), INACTIVE, LOCKED and ARCHIVED close the SKUs that use the value, SKUs are reopened when the value is ACTIVE again and every value of the SKU is ACTIVE | ACTIVE                               |
| 4   | images         | [Array of Value Image](#value-image-object) | OPTIONAL  | Images of the option value, Each image is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, Images that are not in the list are kept, Images of a deleted value are deleted                                                     |                                      |

#### Value Image Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                              | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Product Image Id, Insert when not specified, Update or Delete when specified, Must belong to the option value and must not be duplicated | ffc6d7e8-0015-4ce3-8ef5-a6b7c8d9eafb |
| 2   | imagePath      | String       | MANDATORY | Image Path                                                                                                                               | /products/wireless-mouse/red-1.png   |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED                                        | ACTIVE                               |

#### Option and SKU Rules

All rules below apply to each product of the request on its own. The error message names the position of the failing item (for example `products[1].options[0]`).

- The level number (`level_no`) of an option is its position in `options` ignoring DELETED options, counted from 1, and the order of a value (`sort_order`) is its position in `values`, counted from 1 (the first value has `sort_order` 1), so neither is sent in the request. A DELETED option keeps its current `level_no` (it is not taken from the request and not renumbered).
- When `options` is specified it is the complete definition: options that are not in the list are deleted (soft delete) together with their values, and values that are not in the list of an option are deleted. The SKUs that use a deleted option or value are closed, and the images of a deleted value are deleted. An empty array deletes all levels and leaves one default SKU.
- Images in `values[].images` keep the rule of `images`: images that are not in the list are kept.
- DELETED is final for options and values: it is never reopened, and adding the same name or value again creates a new row. The id of a DELETED option or value counts as not found and is rejected with 404 (E10004). The row status of an option is ACTIVE or DELETED only, any other status is rejected with 400.
- INACTIVE, LOCKED and ARCHIVED values are reversible: the SKUs that use the value are closed with that status, and setting the value back to ACTIVE reopens the SKUs only when every value of the SKU is ACTIVE (a DELETED SKU is never reopened).
- A product has at most 3 levels (configurable), a level name must not be duplicated in the product, a value must not be duplicated in its level, and every option must contain at least 1 value that is not DELETED.
- SKUs are generated from every combination of the ACTIVE values of all levels. `name` is the value names joined by ` / ` (truncated to 128 characters), `description` is the same text (truncated to 256 characters) and `combination_key` is the value ids joined by `-` in level order (value ids are fixed length UUIDs, so the key stays unique).
- SKU names follow renames: when the value of an option value is renamed, the `name` of every SKU that uses the value is recomputed (value names joined by ` / ` in level order, truncated to 128 characters, and `description` truncated to 256 characters), and when the product name or description changes, the default SKU (`combination_key` is empty) takes the new product name and description.
- A rename to a name or value that is currently held by another listed option or value (a swap or a chain of renames) is applied in two steps: the rows involved are first set to the temporary name `'~' || id`, then to the final name, so the unique name and value indexes never conflict.
- A product without any level has 1 default SKU (`combination_key` is empty), the default SKU is closed when the first level is added and generated again when all levels are removed.
- The number of generated SKUs of a product must not exceed the maximum of 500 (configurable). Only ACTIVE combinations are counted: it is calculated from the request as the product of the ACTIVE value counts of each option after the rules above are applied (INACTIVE, LOCKED, ARCHIVED and DELETED values and closed SKUs are not counted), and validated for every product before any write.
- Adding a value or reopening a value generates the SKU combinations that are missing.
- Adding, removing or reordering (changing the position of) a level closes the current SKUs of that product and generates new ones, and it is rejected with 409 when any SKU of that product is used in `shop.t_shop_product_sku`, `cart.t_cart` or `sales.t_order_item`.
- All products are processed in one transaction (all or nothing). The request based validation (400, including the SKU maximum) of all products runs first in the order of the request, then the database based checks (404, then 409) in the order of the request, then the writes. The error of the first failing product is returned and nothing is changed.
- A product cannot be deleted while it is in a campaign that is not DELETED and has not ended (a live `campaign.t_campaign_product` row of a campaign whose `end_at` is after now), 409 (E10006) with the campaign name in the message. Take it out of the campaign first with the upsert campaign API (a campaign that ended or was deleted does not block). Archiving is always allowed. (`docs/superpowers/specs/2026-11-06-campaign-design.md`, C13, approved by the product owner on 2026-11-06)
- Execution order of each product: validate the request (400, including the SKU maximum), existence checks (404, the id of a DELETED option or value counts as not found, E10004), permission check (403, E10009, once for the request in a batch), in-use check (409), move levels aside, delete the options and values that are not in the list, update the listed options and values (renames that collide are set to temporary names first), insert new options and values, images, close or reopen SKUs, then generate SKUs.

#### Permission Rules

- Permission: the same as the single upsert, only a platform administrator (a user with an ACTIVE `author.t_user_role` row for the ACTIVE role `PLATFORM_ADMIN`) can call this API, any other caller gets 403 (E10009). The check is made once for the request, after the existence checks of all items and before the duplicate, in-use and other conflict checks, so the 403 message has no item position. Approved by the product owner (answered through the lead SA, 2026-11-06).
- Order of checks: validate the request (400) -> existence checks (404) -> permission (403, E10009) -> duplicate, in-use and other conflicts (409) -> write.

#### Example Body Parameters

```JSON
{
    "products": [
        {
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Mouse",
            "slug": "wireless-mouse",
            "description": "Ergonomic wireless mouse with 2.4GHz receiver",
            "body": "Ergonomic design, silent click, battery life up to 12 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "Black"
                },
                {
                    "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                    "value": "2.4GHz Wireless"
                }
            ],
            "images": [
                {
                    "imagePath": "/products/wireless-mouse/1.png"
                },
                {
                    "imagePath": "/products/wireless-mouse/2.png"
                }
            ],
            "options": [
                {
                    "name": "ลาย",
                    "rowStatus": "ACTIVE",
                    "values": [
                        {
                            "value": "A"
                        },
                        {
                            "value": "B"
                        }
                    ]
                },
                {
                    "name": "ไซส์",
                    "values": [
                        {
                            "value": "S"
                        },
                        {
                            "value": "M"
                        },
                        {
                            "value": "L"
                        }
                    ]
                },
                {
                    "name": "สี",
                    "values": [
                        {
                            "value": "แดง",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/red-1.png",
                                    "rowStatus": "ACTIVE"
                                },
                                {
                                    "imagePath": "/products/wireless-mouse/red-2.png"
                                }
                            ]
                        },
                        {
                            "value": "ดำ",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/black-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Keyboard Pro",
            "slug": "wireless-keyboard-pro",
            "description": "Slim wireless keyboard with numeric keypad",
            "body": "Slim profile, quiet keys, battery life up to 18 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "White"
                }
            ],
            "images": [
                {
                    "id": "88a1b2c3-0103-4d2e-9f3a-5b6c7d8e9f01",
                    "imagePath": "/products/wireless-keyboard-pro/1.png"
                },
                {
                    "id": "99b2c3d4-0104-4e3f-8a4b-6c7d8e9fa012",
                    "imagePath": "/products/wireless-keyboard/2.png",
                    "rowStatus": "DELETED"
                }
            ],
            "options": [
                {
                    "id": "aac3d4e5-0107-4f4a-9b5c-7d8e9fa0b123",
                    "name": "สี",
                    "values": [
                        {
                            "id": "bbd4e5f6-0113-4a5b-8c6d-8e9fa0b1c234",
                            "value": "ดำ",
                            "images": [
                                {
                                    "id": "ddf6a7b8-0115-4c7d-8e8f-a0b1c2d3e456",
                                    "imagePath": "/products/wireless-keyboard-pro/black-1.png"
                                }
                            ]
                        },
                        {
                            "id": "cce5f6a7-0114-4b6c-9d7e-9fa0b1c2d345",
                            "value": "ขาว"
                        },
                        {
                            "value": "เทา",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-keyboard-pro/grey-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "a3c4d5e6-f7a8-4b9c-8d0e-2f3a4b5c6d7e",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "USB Cable",
            "slug": "usb-cable",
            "description": "USB-C charging cable 1 meter",
            "body": "Braided cable, supports fast charging.",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/product/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "products": [
        {
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Mouse",
            "slug": "wireless-mouse",
            "description": "Ergonomic wireless mouse with 2.4GHz receiver",
            "body": "Ergonomic design, silent click, battery life up to 12 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "Black"
                },
                {
                    "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                    "value": "2.4GHz Wireless"
                }
            ],
            "images": [
                {
                    "imagePath": "/products/wireless-mouse/1.png"
                },
                {
                    "imagePath": "/products/wireless-mouse/2.png"
                }
            ],
            "options": [
                {
                    "name": "ลาย",
                    "rowStatus": "ACTIVE",
                    "values": [
                        {
                            "value": "A"
                        },
                        {
                            "value": "B"
                        }
                    ]
                },
                {
                    "name": "ไซส์",
                    "values": [
                        {
                            "value": "S"
                        },
                        {
                            "value": "M"
                        },
                        {
                            "value": "L"
                        }
                    ]
                },
                {
                    "name": "สี",
                    "values": [
                        {
                            "value": "แดง",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/red-1.png",
                                    "rowStatus": "ACTIVE"
                                },
                                {
                                    "imagePath": "/products/wireless-mouse/red-2.png"
                                }
                            ]
                        },
                        {
                            "value": "ดำ",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/black-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Keyboard Pro",
            "slug": "wireless-keyboard-pro",
            "description": "Slim wireless keyboard with numeric keypad",
            "body": "Slim profile, quiet keys, battery life up to 18 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "White"
                }
            ],
            "images": [
                {
                    "id": "88a1b2c3-0103-4d2e-9f3a-5b6c7d8e9f01",
                    "imagePath": "/products/wireless-keyboard-pro/1.png"
                },
                {
                    "id": "99b2c3d4-0104-4e3f-8a4b-6c7d8e9fa012",
                    "imagePath": "/products/wireless-keyboard/2.png",
                    "rowStatus": "DELETED"
                }
            ],
            "options": [
                {
                    "id": "aac3d4e5-0107-4f4a-9b5c-7d8e9fa0b123",
                    "name": "สี",
                    "values": [
                        {
                            "id": "bbd4e5f6-0113-4a5b-8c6d-8e9fa0b1c234",
                            "value": "ดำ",
                            "images": [
                                {
                                    "id": "ddf6a7b8-0115-4c7d-8e8f-a0b1c2d3e456",
                                    "imagePath": "/products/wireless-keyboard-pro/black-1.png"
                                }
                            ]
                        },
                        {
                            "id": "cce5f6a7-0114-4b6c-9d7e-9fa0b1c2d345",
                            "value": "ขาว"
                        },
                        {
                            "value": "เทา",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-keyboard-pro/grey-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "a3c4d5e6-f7a8-4b9c-8d0e-2f3a4b5c6d7e",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "USB Cable",
            "slug": "usb-cable",
            "description": "USB-C charging cable 1 meter",
            "body": "Braided cable, supports fast charging.",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/product/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "products": [
        {
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Mouse",
            "slug": "wireless-mouse",
            "description": "Ergonomic wireless mouse with 2.4GHz receiver",
            "body": "Ergonomic design, silent click, battery life up to 12 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "Black"
                },
                {
                    "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                    "value": "2.4GHz Wireless"
                }
            ],
            "images": [
                {
                    "imagePath": "/products/wireless-mouse/1.png"
                },
                {
                    "imagePath": "/products/wireless-mouse/2.png"
                }
            ],
            "options": [
                {
                    "name": "ลาย",
                    "rowStatus": "ACTIVE",
                    "values": [
                        {
                            "value": "A"
                        },
                        {
                            "value": "B"
                        }
                    ]
                },
                {
                    "name": "ไซส์",
                    "values": [
                        {
                            "value": "S"
                        },
                        {
                            "value": "M"
                        },
                        {
                            "value": "L"
                        }
                    ]
                },
                {
                    "name": "สี",
                    "values": [
                        {
                            "value": "แดง",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/red-1.png",
                                    "rowStatus": "ACTIVE"
                                },
                                {
                                    "imagePath": "/products/wireless-mouse/red-2.png"
                                }
                            ]
                        },
                        {
                            "value": "ดำ",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-mouse/black-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "Wireless Keyboard Pro",
            "slug": "wireless-keyboard-pro",
            "description": "Slim wireless keyboard with numeric keypad",
            "body": "Slim profile, quiet keys, battery life up to 18 months.",
            "rowStatus": "ACTIVE",
            "attributes": [
                {
                    "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                    "value": "White"
                }
            ],
            "images": [
                {
                    "id": "88a1b2c3-0103-4d2e-9f3a-5b6c7d8e9f01",
                    "imagePath": "/products/wireless-keyboard-pro/1.png"
                },
                {
                    "id": "99b2c3d4-0104-4e3f-8a4b-6c7d8e9fa012",
                    "imagePath": "/products/wireless-keyboard/2.png",
                    "rowStatus": "DELETED"
                }
            ],
            "options": [
                {
                    "id": "aac3d4e5-0107-4f4a-9b5c-7d8e9fa0b123",
                    "name": "สี",
                    "values": [
                        {
                            "id": "bbd4e5f6-0113-4a5b-8c6d-8e9fa0b1c234",
                            "value": "ดำ",
                            "images": [
                                {
                                    "id": "ddf6a7b8-0115-4c7d-8e8f-a0b1c2d3e456",
                                    "imagePath": "/products/wireless-keyboard-pro/black-1.png"
                                }
                            ]
                        },
                        {
                            "id": "cce5f6a7-0114-4b6c-9d7e-9fa0b1c2d345",
                            "value": "ขาว"
                        },
                        {
                            "value": "เทา",
                            "images": [
                                {
                                    "imagePath": "/products/wireless-keyboard-pro/grey-1.png"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "a3c4d5e6-f7a8-4b9c-8d0e-2f3a4b5c6d7e",
            "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
            "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
            "name": "USB Cable",
            "slug": "usb-cable",
            "description": "USB-C charging cable 1 meter",
            "body": "Braided cable, supports fast charging.",
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field         | Description                                       | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ------------- | ------------------------------------------------- | ------- |
| 1   | products       | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.products | Result of each product, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                     | Description                                             | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------- | ------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.products[].index     | Index of the product in the request, Starting from 0    | 0                                    |
| 2   | productId      | String: UUID | MANDATORY | Sequence Diagram | data.products[].productId | Inserted, Updated, Deleted or Archived Product Id       | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.products[].action    | Action of the product (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Product Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "products": [
            {
                "index": 0,
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "action": "INSERT"
            },
            {
                "index": 1,
                "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "productId": "a3c4d5e6-f7a8-4b9c-8d0e-2f3a4b5c6d7e",
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
        "bizMessage": "products[0]: Type Id, Category Id, Brand Id, Name, Description and Body are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
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
        "bizMessage": "Products must contain 1 to 100 items.",
        "requestId": "req-400b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:50.456Z",
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
        "bizMessage": "products[2]: Id is duplicated with products[1].",
        "requestId": "req-400c1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:55.789Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Slug

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[1]: Slug must contain only a-z, 0-9 and hyphen, and must not be longer than 128 characters.",
        "requestId": "req-400d1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Attribute

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0]: Attribute Id and Value are required fields, Attribute Id must not be duplicated.",
        "requestId": "req-400e1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:02.456Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Category Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[1]: Attributes are required when category is changed.",
        "requestId": "req-400f1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:03.789Z",
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
        "bizMessage": "products[0].images[0]: Image Path is a required field, Image Id must not be duplicated.",
        "requestId": "req-400g1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:04.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Option

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0].options[0]: Name is required and Values must contain at least 1 value.",
        "requestId": "req-400h1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:05.456Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Option Duplicate

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0].options[1]: Name is duplicated with products[0].options[0].",
        "requestId": "req-400i1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:05.789Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Option Status

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0].options[0]: Row status must be ACTIVE or DELETED.",
        "requestId": "req-400l1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:06.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Value Duplicate

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0].options[0].values[1]: Value is duplicated with products[0].options[0].values[0].",
        "requestId": "req-400m1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:06.456Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Level

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[0]: Options must not contain more than 3 levels.",
        "requestId": "req-400j1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:06.789Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request SKU Limit

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "products[1]: SKU count exceeds the maximum of 500.",
        "requestId": "req-400k1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:07.123Z",
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

#### Fail - Not Found

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "products[1]: Product not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:05.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Reference

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "products[0]: Product type, category or brand not found.",
        "requestId": "req-404b1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:12.654Z",
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
        "bizMessage": "products[1].images[0]: Product image not found.",
        "requestId": "req-404d1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:20.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Attribute

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "products[0]: Product category attribute not found.",
        "requestId": "req-404c1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:18.987Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Option

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "products[0].options[0]: Product option not found.",
        "requestId": "req-404e1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.321Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Option Value

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "products[0].options[0].values[0]: Product option value not found.",
        "requestId": "req-404f1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:24.321Z",
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
        "bizMessage": "You do not have permission to manage products.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict SKU In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "products[1]: Product options cannot be changed because SKUs are used.",
        "requestId": "req-409a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:10.123Z",
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
        "bizMessage": "products[1]: The product is in a campaign that has not ended (Black Friday 2026) and cannot be deleted.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
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

### Table: [product.m_product_type](../../../schema/product/m_product_type.md)

#### QUERY - Check product types

```SQL
SELECT
    pt.id as type_id
FROM product.m_product_type pt
WHERE pt.id IN ('<sequence.products.typeIds>')
AND pt.row_status = 'ACTIVE'
```

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Check product categories

```SQL
SELECT
    pc.id as category_id
FROM product.m_product_category pc
WHERE pc.id IN ('<sequence.products.categoryIds>')
AND pc.row_status = 'ACTIVE'
```

### Table: [product.m_product_brand](../../../schema/product/m_product_brand.md)

#### QUERY - Check product brands

```SQL
SELECT
    pb.id as brand_id
FROM product.m_product_brand pb
WHERE pb.id IN ('<sequence.products.brandIds>')
AND pb.row_status = 'ACTIVE'
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Check existing products

```SQL
SELECT
    p.id as product_id,
    p.category_id
FROM product.m_product p
WHERE p.id IN ('<sequence.products.ids>')
```

#### INSERT - Create product

```SQL
INSERT INTO product.m_product (
    created_by,
    row_status,
    type_id,
    category_id,
    brand_id,
    name,
    slug,
    description,
    body
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.products.rowStatus>',
    '<sequence.products.typeId>',
    '<sequence.products.categoryId>',
    '<sequence.products.brandId>',
    '<sequence.products.name>',
    '<sequence.products.slug>',
    '<sequence.products.description>',
    '<sequence.products.body>'
)
RETURNING id as product_id
```

#### UPDATE - Update or delete product

```SQL
UPDATE product.m_product
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.rowStatus>',
    type_id = '<sequence.products.typeId>',
    category_id = '<sequence.products.categoryId>',
    brand_id = '<sequence.products.brandId>',
    name = '<sequence.products.name>',
    slug = '<sequence.products.slug>', -- only when slug is specified
    description = '<sequence.products.description>',
    body = '<sequence.products.body>'
WHERE id = '<sequence.products.id>'
RETURNING id as product_id
```

### Table: [product.m_product_category_attribute](../../../schema/product/m_product_category_attribute.md)

#### QUERY - Check product category attributes

```SQL
SELECT
    pca.id as attribute_id
FROM product.m_product_category_attribute pca
WHERE pca.id IN ('<sequence.products.attributes.attributeIds>')
AND pca.category_id = '<sequence.products.categoryId>'
AND pca.row_status = 'ACTIVE'
```

### Table: [product.m_product_attribute](../../../schema/product/m_product_attribute.md)

#### QUERY - Get existing product attributes

```SQL
SELECT
    pa.id as product_attribute_id,
    pa.attribute_id
FROM product.m_product_attribute pa
WHERE pa.product_id = '<sequence.products.id>'
AND pa.row_status <> 'DELETED'
```

#### INSERT - Create product attribute

```SQL
INSERT INTO product.m_product_attribute (
    created_by,
    product_id,
    attribute_id,
    value
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.productId>',
    '<sequence.products.attributes.attributeId>',
    '<sequence.products.attributes.value>'
)
RETURNING id as product_attribute_id
```

#### UPDATE - Update product attribute

```SQL
UPDATE product.m_product_attribute
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    value = '<sequence.products.attributes.value>'
WHERE id = '<sequence.productAttributeId>'
RETURNING id as product_attribute_id
```

#### UPDATE - Delete product attributes that are not in the list

```SQL
UPDATE product.m_product_attribute
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE product_id = '<sequence.productId>'
AND attribute_id NOT IN ('<sequence.products.attributes.attributeIds>')
AND row_status <> 'DELETED'
```

### Table: [product.m_product_option](../../../schema/product/m_product_option.md)

#### QUERY - Get existing product options

```SQL
SELECT
    po.id as option_id,
    po.name,
    po.level_no,
    po.row_status
FROM product.m_product_option po
WHERE po.product_id = '<sequence.products.id>'
AND po.row_status <> 'DELETED'
ORDER BY po.level_no
```

#### UPDATE - Move product option levels aside

```SQL
UPDATE product.m_product_option
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    level_no = level_no + 1000 -- temporary level, avoids the unique (product_id, level_no) conflict while renumbering
WHERE product_id = '<sequence.productId>'
AND row_status <> 'DELETED'
```

#### UPDATE - Set temporary names for renamed product options

```SQL
UPDATE product.m_product_option
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    name = '~' || id -- temporary name, avoids the unique (product_id, name) conflict, the final name is set by the update below
WHERE product_id = '<sequence.productId>'
AND id IN ('<sequence.products.options.renamedIds>') -- listed options that are renamed to a name currently held by another listed option (swap or chain of renames)
AND row_status <> 'DELETED'
```

#### UPDATE - Update or delete product option

```SQL
UPDATE product.m_product_option
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.options.rowStatus>', -- ACTIVE or DELETED only
    name = '<sequence.products.options.name>',
    level_no = CASE WHEN '<sequence.products.options.rowStatus>' = 'DELETED' THEN level_no ELSE '<sequence.products.options.levelNo>' END -- renumbered from 1 in the order of options, a DELETED option keeps its current level_no, DELETED options are outside the unique index
WHERE id = '<sequence.products.options.id>'
AND product_id = '<sequence.productId>'
AND row_status <> 'DELETED' -- a DELETED option is never reopened
RETURNING id as option_id
```

#### UPDATE - Delete product options that are not in the list

```SQL
UPDATE product.m_product_option
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE product_id = '<sequence.productId>'
AND id NOT IN ('<sequence.products.options.ids>') -- all options when options is an empty array
AND row_status <> 'DELETED'
```

#### INSERT - Create product option

```SQL
INSERT INTO product.m_product_option (
    created_by,
    row_status,
    product_id,
    name,
    level_no
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.products.options.rowStatus>',
    '<sequence.productId>',
    '<sequence.products.options.name>',
    '<sequence.products.options.levelNo>' -- position in options ignoring DELETED options
)
RETURNING id as option_id
```

### Table: [product.m_product_option_value](../../../schema/product/m_product_option_value.md)

#### QUERY - Get existing product option values

```SQL
SELECT
    pov.id as option_value_id,
    pov.option_id,
    pov.value,
    pov.sort_order,
    pov.row_status
FROM product.m_product_option_value pov
INNER JOIN product.m_product_option po ON po.id = pov.option_id
WHERE po.product_id = '<sequence.products.id>'
AND pov.row_status <> 'DELETED'
```

#### UPDATE - Delete product option values of deleted options

```SQL
UPDATE product.m_product_option_value
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE option_id IN (
    SELECT po.id
    FROM product.m_product_option po
    WHERE po.product_id = '<sequence.productId>'
    AND po.row_status = 'DELETED' -- options deleted by rowStatus and options that are not in the list
)
AND row_status <> 'DELETED'
```

#### UPDATE - Set temporary names for renamed product option values

```SQL
UPDATE product.m_product_option_value
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    value = '~' || id -- temporary value, avoids the unique (option_id, value) conflict, the final value is set by the update below
WHERE option_id = '<sequence.optionId>'
AND id IN ('<sequence.products.options.values.renamedIds>') -- listed values that are renamed to a value currently held by another listed value (swap or chain of renames)
AND row_status <> 'DELETED'
```

#### UPDATE - Update or delete product option value

```SQL
UPDATE product.m_product_option_value
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.options.values.rowStatus>',
    value = '<sequence.products.options.values.value>',
    sort_order = '<sequence.products.options.values.sortOrder>' -- position in values, counted from 1
WHERE id = '<sequence.products.options.values.id>'
AND option_id = '<sequence.optionId>'
AND row_status <> 'DELETED' -- a DELETED value is never reopened
RETURNING id as option_value_id
```

#### UPDATE - Delete product option values that are not in the list

```SQL
UPDATE product.m_product_option_value
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE option_id = '<sequence.optionId>'
AND id NOT IN ('<sequence.products.options.values.ids>')
AND row_status <> 'DELETED'
```

#### INSERT - Create product option value

```SQL
INSERT INTO product.m_product_option_value (
    created_by,
    row_status,
    option_id,
    value,
    sort_order
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.products.options.values.rowStatus>',
    '<sequence.optionId>',
    '<sequence.products.options.values.value>',
    '<sequence.products.options.values.sortOrder>' -- position in values, counted from 1
)
RETURNING id as option_value_id
```

### Table: [product.m_product_image](../../../schema/product/m_product_image.md)

#### QUERY - Check existing product images

```SQL
SELECT
    pi.id as image_id
FROM product.m_product_image pi
WHERE pi.id IN ('<sequence.products.images.ids>')
AND pi.product_id = '<sequence.products.id>'
AND pi.option_value_id IS NULL
```

#### QUERY - Check existing product option value images

```SQL
SELECT
    pi.id as image_id
FROM product.m_product_image pi
WHERE pi.id IN ('<sequence.products.options.values.images.ids>')
AND pi.option_value_id = '<sequence.optionValueId>'
```

#### INSERT - Create product image

```SQL
INSERT INTO product.m_product_image (
    created_by,
    row_status,
    product_id,
    image_path,
    option_value_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.products.images.rowStatus>',
    '<sequence.productId>',
    '<sequence.products.images.imagePath>',
    NULL -- product level image
)
RETURNING id as image_id
```

#### INSERT - Create product option value image

```SQL
INSERT INTO product.m_product_image (
    created_by,
    row_status,
    product_id,
    image_path,
    option_value_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.products.options.values.images.rowStatus>',
    '<sequence.productId>',
    '<sequence.products.options.values.images.imagePath>',
    '<sequence.optionValueId>'
)
RETURNING id as image_id
```

#### UPDATE - Update or delete product image

```SQL
UPDATE product.m_product_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.images.rowStatus>',
    image_path = '<sequence.products.images.imagePath>'
WHERE id = '<sequence.products.images.id>'
AND product_id = '<sequence.productId>'
AND option_value_id IS NULL -- product level images only
RETURNING id as image_id
```

#### UPDATE - Update or delete product option value image

```SQL
UPDATE product.m_product_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.options.values.images.rowStatus>',
    image_path = '<sequence.products.options.values.images.imagePath>'
WHERE id = '<sequence.products.options.values.images.id>'
AND product_id = '<sequence.productId>'
AND option_value_id = '<sequence.optionValueId>'
RETURNING id as image_id
```

#### UPDATE - Delete product images of deleted option values

```SQL
UPDATE product.m_product_image
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE option_value_id IN (
    SELECT pov.id
    FROM product.m_product_option_value pov
    INNER JOIN product.m_product_option po ON po.id = pov.option_id
    WHERE po.product_id = '<sequence.productId>'
    AND pov.row_status = 'DELETED' -- values deleted by rowStatus, values that are not in the list and values of deleted options
)
AND row_status <> 'DELETED'
```

### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)

#### QUERY - Check product SKUs in use

```SQL
SELECT
    s.id as sku_id
FROM product.m_product_sku s
WHERE s.product_id = '<sequence.productId>'
AND s.row_status <> 'DELETED'
AND (
    EXISTS (SELECT 1 FROM shop.t_shop_product_sku tsps WHERE tsps.sku_id = s.id)
    OR EXISTS (SELECT 1 FROM cart.t_cart c WHERE c.sku_id = s.id)
    OR EXISTS (SELECT 1 FROM sales.t_order_item oi WHERE oi.sku_id = s.id)
)
```

#### QUERY - Get existing product SKUs

```SQL
SELECT
    s.id as sku_id,
    s.combination_key,
    s.row_status
FROM product.m_product_sku s
WHERE s.product_id = '<sequence.productId>'
AND s.row_status <> 'DELETED' -- used to generate only the missing combinations
```

#### UPDATE - Close all product SKUs when levels are added, removed or reordered

```SQL
UPDATE product.m_product_sku
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED' -- only when the levels of the product change and no SKU is in use, otherwise respond 409
WHERE product_id = '<sequence.productId>'
AND row_status <> 'DELETED'
```

#### UPDATE - Close product SKUs of deleted option values

```SQL
UPDATE product.m_product_sku s
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = 'DELETED'
WHERE s.product_id = '<sequence.productId>'
AND s.row_status <> 'DELETED'
AND EXISTS ( -- run after the values are updated or deleted
    SELECT 1
    FROM product.m_product_sku_option_value sov
    INNER JOIN product.m_product_option_value pov ON pov.id = sov.option_value_id
    WHERE sov.sku_id = s.id
    AND pov.row_status = 'DELETED' -- values deleted by rowStatus, values that are not in the list and values of deleted options
)
```

#### UPDATE - Close product SKUs of closed option values

```SQL
UPDATE product.m_product_sku s
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.products.options.values.rowStatus>' -- INACTIVE, LOCKED or ARCHIVED closes the SKUs, ACTIVE reopens them
WHERE s.product_id = '<sequence.productId>'
AND s.row_status <> 'DELETED' -- a DELETED SKU is never reopened
AND s.id IN (
    SELECT sov.sku_id
    FROM product.m_product_sku_option_value sov
    WHERE sov.option_value_id = '<sequence.optionValueId>'
)
AND (
    '<sequence.products.options.values.rowStatus>' <> 'ACTIVE'
    OR NOT EXISTS ( -- reopen only when every value of the SKU is ACTIVE, run after the option value is updated
        SELECT 1
        FROM product.m_product_sku_option_value sov2
        INNER JOIN product.m_product_option_value pov2 ON pov2.id = sov2.option_value_id
        WHERE sov2.sku_id = s.id
        AND pov2.row_status <> 'ACTIVE'
    )
)
```

#### UPDATE - Rename product SKUs of renamed option values

```SQL
UPDATE product.m_product_sku s
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    name = LEFT(sn.sku_name, 128), -- value names joined by ' / ' in level order, truncated to 128 characters
    description = LEFT(sn.sku_name, 256) -- the same text truncated to 256 characters
FROM (
    SELECT
        sov.sku_id,
        STRING_AGG(pov.value, ' / ' ORDER BY po.level_no) AS sku_name
    FROM product.m_product_sku_option_value sov
    INNER JOIN product.m_product_option_value pov ON pov.id = sov.option_value_id
    INNER JOIN product.m_product_option po ON po.id = pov.option_id
    WHERE sov.sku_id IN ( -- run after the option values are updated
        SELECT sov2.sku_id
        FROM product.m_product_sku_option_value sov2
        WHERE sov2.option_value_id IN ('<sequence.products.options.values.renamedValueIds>') -- values whose value is renamed
    )
    GROUP BY sov.sku_id
) sn
WHERE s.id = sn.sku_id
AND s.product_id = '<sequence.productId>'
AND s.row_status <> 'DELETED'
```

#### UPDATE - Rename default product SKU

```SQL
UPDATE product.m_product_sku
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    name = '<sequence.products.name>', -- only when the product name changes
    description = '<sequence.products.description>'
WHERE product_id = '<sequence.productId>'
AND combination_key = '' -- the default SKU
AND row_status <> 'DELETED'
```

#### INSERT - Create default product SKU

```SQL
INSERT INTO product.m_product_sku (
    created_by,
    row_status,
    product_id,
    name,
    description,
    combination_key
)
VALUES (
    '<sequence.createdBy>',
    'ACTIVE',
    '<sequence.productId>',
    '<sequence.products.name>',
    '<sequence.products.description>',
    '' -- only when the product has no level, the default SKU has no option values
)
RETURNING id as sku_id
```

#### INSERT - Create product SKU

```SQL
INSERT INTO product.m_product_sku (
    created_by,
    row_status,
    product_id,
    name,
    description,
    combination_key
)
VALUES (
    '<sequence.createdBy>',
    'ACTIVE',
    '<sequence.productId>',
    '<sequence.products.skus.name>', -- value names of the combination joined by ' / ' in level order, truncated to 128 characters
    '<sequence.products.skus.description>', -- the same text truncated to 256 characters
    '<sequence.products.skus.combinationKey>' -- value ids of the combination joined by '-' in level order, UUIDs have a fixed length so the key stays unique
)
RETURNING id as sku_id
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### INSERT - Create product SKU option value

```SQL
INSERT INTO product.m_product_sku_option_value (
    created_by,
    row_status,
    sku_id,
    option_value_id
)
VALUES (
    '<sequence.createdBy>',
    'ACTIVE',
    '<sequence.skuId>',
    '<sequence.products.skus.optionValueIds>' -- one row for each value of the combination
)
RETURNING id as sku_option_value_id
```

### Table: [campaign.t_campaign_product](../../../schema/campaign/t_campaign_product.md)

#### QUERY - Check product campaigns in use

```SQL
SELECT
    cp.id as campaign_product_id,
    c.name
FROM campaign.t_campaign_product cp
INNER JOIN campaign.m_campaign c
    ON c.id = cp.campaign_id
WHERE cp.product_id = '<sequence.id>'
AND cp.row_status <> 'DELETED'
AND c.row_status <> 'DELETED'
AND c.end_at > NOW() AT TIME ZONE 'UTC' -- a campaign that ended or was deleted does not block, answer 409 (E10006) when a row is found
LIMIT 1
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
