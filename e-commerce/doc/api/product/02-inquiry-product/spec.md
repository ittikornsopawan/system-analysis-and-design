# [GET]: v1/product

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Product API                                                                                                                                                                                                                                                                                                                                                                       |
| Method      | GET                                                                                                                                                                                                                                                                                                                                                                                       |
| Endpoint    | v{version}/product                                                                                                                                                                                                                                                                                                                                                                        |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                         |
| Description | Inquiry the list of products with paging, search and category filter, Inquiry by id returns a list with one item, Deleted products are excluded, Options and SKUs are returned with the product, Image shown for a selection is the image of the lowest level selected value that has an image, otherwise the product level images (a rule for the client, the API does not calculate it) |

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

|     | Parameter Name | Data Type    | M/O      | Description                                        | Example                              |
| --- | -------------- | ------------ | -------- | -------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | Product Id, Response is a list with one item       | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 2   | categoryId     | String: UUID | OPTIONAL | Product Category Id, Filter products by category   | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e |
| 3   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1          | 1                                    |
| 4   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10 | 10                                   |
| 5   | search         | String       | OPTIONAL | Search by product name or product description      | mouse                                |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/product?id=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&categoryId=b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e&pageIndex=1&pageSize=10&search=mouse HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/product?id=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c&categoryId=b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e&pageIndex=1&pageSize=10&search=mouse' \
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

|     | Parameter Name | Data Type                           | M/O       | Source           | Field           | Description                          | Example |
| --- | -------------- | ----------------------------------- | --------- | ---------------- | --------------- | ------------------------------------ | ------- |
| 1   | items          | [Array of Product](#product-object) | MANDATORY | Sequence Diagram | data.items      | Products, Empty array when not found |         |
| 2   | pageIndex      | Numeric                             | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                   | 1       |
| 3   | pageSize       | Numeric                             | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page             | 10      |
| 4   | totalItems     | Numeric                             | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                | 2       |
| 5   | totalPages     | Numeric                             | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                | 1       |

#### Product Object

|     | Parameter Name | Data Type                               | M/O       | Source           | Field                     | Description                                                                                                                              | Example                                                       |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1   | productId      | String: UUID                            | MANDATORY | Sequence Diagram | data.items[].productId    | Product Id                                                                                                                               | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c                          |
| 2   | typeId         | String: UUID                            | MANDATORY | Sequence Diagram | data.items[].typeId       | Product Type Id                                                                                                                          | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d                          |
| 3   | typeName       | String                                  | MANDATORY | Sequence Diagram | data.items[].typeName     | Product Type Name                                                                                                                        | Electronics                                                   |
| 4   | categoryId     | String: UUID                            | MANDATORY | Sequence Diagram | data.items[].categoryId   | Product Category Id                                                                                                                      | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e                          |
| 5   | categoryName   | String                                  | MANDATORY | Sequence Diagram | data.items[].categoryName | Product Category Name                                                                                                                    | Computer Accessories                                          |
| 6   | brandId        | String: UUID                            | MANDATORY | Sequence Diagram | data.items[].brandId      | Product Brand Id                                                                                                                         | c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f                          |
| 7   | brandName      | String                                  | MANDATORY | Sequence Diagram | data.items[].brandName    | Product Brand Name                                                                                                                       | Acme                                                          |
| 8   | name           | String                                  | MANDATORY | Sequence Diagram | data.items[].name         | Product Name                                                                                                                             | Wireless Mouse                                                |
| 9   | slug           | String                                  | MANDATORY | Sequence Diagram | data.items[].slug         | Product Slug, Used in the web URL /{id}/{slug}                                                                                           | wireless-mouse                                                |
| 10  | description    | String                                  | MANDATORY | Sequence Diagram | data.items[].description  | Product Description                                                                                                                      | Ergonomic wireless mouse with 2.4GHz receiver                 |
| 11  | body           | String                                  | MANDATORY | Sequence Diagram | data.items[].body         | Product Detail                                                                                                                           | Ergonomic design, silent click, battery life up to 12 months. |
| 12  | rowStatus      | String                                  | MANDATORY | Sequence Diagram | data.items[].rowStatus    | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                                                                                          | ACTIVE                                                        |
| 13  | attributes     | [Array of Attribute](#attribute-object) | MANDATORY | Sequence Diagram | data.items[].attributes   | Product attributes, Empty array when the product has no attribute                                                                        |                                                               |
| 14  | images         | [Array of Image](#image-object)         | MANDATORY | Sequence Diagram | data.items[].images       | Product level images, Empty array when the product has no product level image (images of option values are in options[].values[].images) |                                                               |
| 15  | options        | [Array of Option](#option-object)       | MANDATORY | Sequence Diagram | data.items[].options      | Product options ordered by level (ACTIVE options only), Empty array when the product has no level                                        |                                                               |
| 16  | skus           | [Array of SKU](#sku-object)             | MANDATORY | Sequence Diagram | data.items[].skus         | Product SKUs (DELETED SKUs are excluded), A product without level has 1 default SKU                                                      |                                                               |

#### Attribute Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                   | Description                     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------------- | ------------------------------- | ------------------------------------ |
| 1   | attributeId    | String: UUID | MANDATORY | Sequence Diagram | data.items[].attributes[].attributeId   | Product Category Attribute Id   | 11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d |
| 2   | attributeName  | String       | MANDATORY | Sequence Diagram | data.items[].attributes[].attributeName | Product Category Attribute Name | Color                                |
| 3   | value          | String       | MANDATORY | Sequence Diagram | data.items[].attributes[].value         | Attribute Value                 | Black                                |

#### Image Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                           | Description      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------------- | ---------------- | ------------------------------------ |
| 1   | imageId        | String: UUID | MANDATORY | Sequence Diagram | data.items[].images[].imageId   | Product Image Id | 33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f |
| 2   | imagePath      | String       | MANDATORY | Sequence Diagram | data.items[].images[].imagePath | Image Path       | /products/wireless-mouse/1.png       |

#### Option Object

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field                           | Description                                                      | Example                              |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | ------------------------------- | ---------------------------------------------------------------- | ------------------------------------ |
| 1   | optionId       | String: UUID                                  | MANDATORY | Sequence Diagram | data.items[].options[].optionId | Product Option Id                                                | c0a1b2c3-0001-4a01-8b01-000000000001 |
| 2   | name           | String                                        | MANDATORY | Sequence Diagram | data.items[].options[].name     | Option Name, The name of the level                               | ลาย                                  |
| 3   | levelNo        | Numeric                                       | MANDATORY | Sequence Diagram | data.items[].options[].levelNo  | Level number starting from 1, Options are ordered by level       | 1                                    |
| 4   | values         | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.items[].options[].values   | Option values ordered by sortOrder (DELETED values are excluded) |                                      |

#### Option Value Object

|     | Parameter Name | Data Type                                                 | M/O       | Source           | Field                                     | Description                                                         | Example                              |
| --- | -------------- | --------------------------------------------------------- | --------- | ---------------- | ----------------------------------------- | ------------------------------------------------------------------- | ------------------------------------ |
| 1   | valueId        | String: UUID                                              | MANDATORY | Sequence Diagram | data.items[].options[].values[].valueId   | Product Option Value Id                                             | d0e1f2a3-0001-4a01-8b01-000000000001 |
| 2   | value          | String                                                    | MANDATORY | Sequence Diagram | data.items[].options[].values[].value     | Option Value                                                        | A                                    |
| 3   | sortOrder      | Numeric                                                   | MANDATORY | Sequence Diagram | data.items[].options[].values[].sortOrder | Display order of the value in the option                            | 1                                    |
| 4   | rowStatus      | String                                                    | MANDATORY | Sequence Diagram | data.items[].options[].values[].rowStatus | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                     | ACTIVE                               |
| 5   | images         | [Array of Option Value Image](#option-value-image-object) | MANDATORY | Sequence Diagram | data.items[].options[].values[].images    | Images of the option value, Empty array when the value has no image |                                      |

#### Option Value Image Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                                              | Description      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------------------------------------- | ---------------- | ------------------------------------ |
| 1   | imageId        | String: UUID | MANDATORY | Sequence Diagram | data.items[].options[].values[].images[].imageId   | Product Image Id | f7a8b9c0-0001-4a01-8b01-000000000001 |
| 2   | imagePath      | String       | MANDATORY | Sequence Diagram | data.items[].options[].values[].images[].imagePath | Image Path       | /products/wireless-mouse/red-1.png   |

#### SKU Object

|     | Parameter Name | Data Type             | M/O       | Source           | Field                              | Description                                                                                             | Example                                                                                                        |
| --- | -------------- | --------------------- | --------- | ---------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 1   | skuId          | String: UUID          | MANDATORY | Sequence Diagram | data.items[].skus[].skuId          | Product SKU Id                                                                                          | e5f6a7b8-0001-4a01-8b01-000000000001                                                                           |
| 2   | name           | String                | MANDATORY | Sequence Diagram | data.items[].skus[].name           | SKU Name, The value names joined by " / " in level order                                                | A / S / แดง                                                                                                    |
| 3   | combinationKey | String                | MANDATORY | Sequence Diagram | data.items[].skus[].combinationKey | The option value ids joined by "-" in level order, Empty for the default SKU of a product without level | d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0006-4a06-8b06-000000000006 |
| 4   | optionValueIds | Array of String: UUID | MANDATORY | Sequence Diagram | data.items[].skus[].optionValueIds | Option value ids of the SKU in level order, Empty array for the default SKU                             |                                                                                                                |
| 5   | rowStatus      | String                | MANDATORY | Sequence Diagram | data.items[].skus[].rowStatus      | Row status (ACTIVE, INACTIVE, LOCKED, ARCHIVED)                                                         | ACTIVE                                                                                                         |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Product Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "typeName": "Electronics",
                "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "categoryName": "Computer Accessories",
                "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "brandName": "Acme",
                "name": "Wireless Mouse",
                "slug": "wireless-mouse",
                "description": "Ergonomic wireless mouse with 2.4GHz receiver",
                "body": "Ergonomic design, silent click, battery life up to 12 months.",
                "rowStatus": "ACTIVE",
                "attributes": [
                    {
                        "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                        "attributeName": "Color",
                        "value": "Black"
                    },
                    {
                        "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                        "attributeName": "Connectivity",
                        "value": "2.4GHz Wireless"
                    }
                ],
                "images": [
                    {
                        "imageId": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
                        "imagePath": "/products/wireless-mouse/1.png"
                    },
                    {
                        "imageId": "44d5e6f7-0004-4d3e-9f4a-5b6c7d8e9fa0",
                        "imagePath": "/products/wireless-mouse/2.png"
                    }
                ],
                "options": [
                    {
                        "optionId": "c0a1b2c3-0001-4a01-8b01-000000000001",
                        "name": "ลาย",
                        "levelNo": 1,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0001-4a01-8b01-000000000001",
                                "value": "A",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0002-4a02-8b02-000000000002",
                                "value": "B",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": []
                            }
                        ]
                    },
                    {
                        "optionId": "c0a1b2c3-0002-4a02-8b02-000000000002",
                        "name": "ไซส์",
                        "levelNo": 2,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0003-4a03-8b03-000000000003",
                                "value": "S",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0004-4a04-8b04-000000000004",
                                "value": "M",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0005-4a05-8b05-000000000005",
                                "value": "L",
                                "sortOrder": 3,
                                "rowStatus": "ACTIVE",
                                "images": []
                            }
                        ]
                    },
                    {
                        "optionId": "c0a1b2c3-0003-4a03-8b03-000000000003",
                        "name": "สี",
                        "levelNo": 3,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0006-4a06-8b06-000000000006",
                                "value": "แดง",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": [
                                    {
                                        "imageId": "f7a8b9c0-0001-4a01-8b01-000000000001",
                                        "imagePath": "/products/wireless-mouse/red-1.png"
                                    },
                                    {
                                        "imageId": "f7a8b9c0-0002-4a02-8b02-000000000002",
                                        "imagePath": "/products/wireless-mouse/red-2.png"
                                    }
                                ]
                            },
                            {
                                "valueId": "d0e1f2a3-0007-4a07-8b07-000000000007",
                                "value": "ดำ",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": [
                                    {
                                        "imageId": "f7a8b9c0-0003-4a03-8b03-000000000003",
                                        "imagePath": "/products/wireless-mouse/black-1.png"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "skus": [
                    {
                        "skuId": "e5f6a7b8-0001-4a01-8b01-000000000001",
                        "name": "A / S / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0002-4a02-8b02-000000000002",
                        "name": "A / S / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0003-4a03-8b03-000000000003",
                        "name": "A / M / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0004-4a04-8b04-000000000004",
                        "name": "A / M / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0005-4a05-8b05-000000000005",
                        "name": "A / L / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0006-4a06-8b06-000000000006",
                        "name": "A / L / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0007-4a07-8b07-000000000007",
                        "name": "B / S / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0008-4a08-8b08-000000000008",
                        "name": "B / S / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0009-4a09-8b09-000000000009",
                        "name": "B / M / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000a-4a0a-8b0a-00000000000a",
                        "name": "B / M / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000b-4a0b-8b0b-00000000000b",
                        "name": "B / L / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000c-4a0c-8b0c-00000000000c",
                        "name": "B / L / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    }
                ]
            },
            {
                "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "typeName": "Electronics",
                "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "categoryName": "Computer Accessories",
                "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "brandName": "Acme",
                "name": "Wireless Keyboard",
                "slug": "wireless-keyboard",
                "description": "Slim wireless keyboard with numeric keypad",
                "body": "Slim profile, quiet keys, battery life up to 18 months.",
                "rowStatus": "INACTIVE",
                "attributes": [
                    {
                        "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                        "attributeName": "Color",
                        "value": "White"
                    }
                ],
                "images": [
                    {
                        "imageId": "77a8b9c0-0007-4a6b-8c7d-8e9fa0b1c2d3",
                        "imagePath": "/products/wireless-keyboard/1.png"
                    }
                ],
                "options": [],
                "skus": [
                    {
                        "skuId": "e5f6a7b8-0080-4a80-8b80-000000000080",
                        "name": "Wireless Keyboard",
                        "combinationKey": "",
                        "optionValueIds": [],
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
        "bizMessage": "Inquiry Product Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-05T12:48:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "typeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "typeName": "Electronics",
                "categoryId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "categoryName": "Computer Accessories",
                "brandId": "c9d0e1f2-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                "brandName": "Acme",
                "name": "Wireless Mouse",
                "slug": "wireless-mouse",
                "description": "Ergonomic wireless mouse with 2.4GHz receiver",
                "body": "Ergonomic design, silent click, battery life up to 12 months.",
                "rowStatus": "ACTIVE",
                "attributes": [
                    {
                        "attributeId": "11a2b3c4-0001-4a0b-8c1d-2e3f4a5b6c7d",
                        "attributeName": "Color",
                        "value": "Black"
                    },
                    {
                        "attributeId": "22b3c4d5-0002-4b1c-9d2e-3f4a5b6c7d8e",
                        "attributeName": "Connectivity",
                        "value": "2.4GHz Wireless"
                    }
                ],
                "images": [
                    {
                        "imageId": "33c4d5e6-0003-4c2d-8e3f-4a5b6c7d8e9f",
                        "imagePath": "/products/wireless-mouse/1.png"
                    },
                    {
                        "imageId": "44d5e6f7-0004-4d3e-9f4a-5b6c7d8e9fa0",
                        "imagePath": "/products/wireless-mouse/2.png"
                    }
                ],
                "options": [
                    {
                        "optionId": "c0a1b2c3-0001-4a01-8b01-000000000001",
                        "name": "ลาย",
                        "levelNo": 1,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0001-4a01-8b01-000000000001",
                                "value": "A",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0002-4a02-8b02-000000000002",
                                "value": "B",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": []
                            }
                        ]
                    },
                    {
                        "optionId": "c0a1b2c3-0002-4a02-8b02-000000000002",
                        "name": "ไซส์",
                        "levelNo": 2,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0003-4a03-8b03-000000000003",
                                "value": "S",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0004-4a04-8b04-000000000004",
                                "value": "M",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": []
                            },
                            {
                                "valueId": "d0e1f2a3-0005-4a05-8b05-000000000005",
                                "value": "L",
                                "sortOrder": 3,
                                "rowStatus": "ACTIVE",
                                "images": []
                            }
                        ]
                    },
                    {
                        "optionId": "c0a1b2c3-0003-4a03-8b03-000000000003",
                        "name": "สี",
                        "levelNo": 3,
                        "values": [
                            {
                                "valueId": "d0e1f2a3-0006-4a06-8b06-000000000006",
                                "value": "แดง",
                                "sortOrder": 1,
                                "rowStatus": "ACTIVE",
                                "images": [
                                    {
                                        "imageId": "f7a8b9c0-0001-4a01-8b01-000000000001",
                                        "imagePath": "/products/wireless-mouse/red-1.png"
                                    },
                                    {
                                        "imageId": "f7a8b9c0-0002-4a02-8b02-000000000002",
                                        "imagePath": "/products/wireless-mouse/red-2.png"
                                    }
                                ]
                            },
                            {
                                "valueId": "d0e1f2a3-0007-4a07-8b07-000000000007",
                                "value": "ดำ",
                                "sortOrder": 2,
                                "rowStatus": "ACTIVE",
                                "images": [
                                    {
                                        "imageId": "f7a8b9c0-0003-4a03-8b03-000000000003",
                                        "imagePath": "/products/wireless-mouse/black-1.png"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "skus": [
                    {
                        "skuId": "e5f6a7b8-0001-4a01-8b01-000000000001",
                        "name": "A / S / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0002-4a02-8b02-000000000002",
                        "name": "A / S / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0003-4a03-8b03-000000000003",
                        "name": "A / M / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0004-4a04-8b04-000000000004",
                        "name": "A / M / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0005-4a05-8b05-000000000005",
                        "name": "A / L / แดง",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0006-4a06-8b06-000000000006",
                        "name": "A / L / ดำ",
                        "combinationKey": "d0e1f2a3-0001-4a01-8b01-000000000001-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0001-4a01-8b01-000000000001",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0007-4a07-8b07-000000000007",
                        "name": "B / S / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0008-4a08-8b08-000000000008",
                        "name": "B / S / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0003-4a03-8b03-000000000003-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0003-4a03-8b03-000000000003",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-0009-4a09-8b09-000000000009",
                        "name": "B / M / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000a-4a0a-8b0a-00000000000a",
                        "name": "B / M / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0004-4a04-8b04-000000000004-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0004-4a04-8b04-000000000004",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000b-4a0b-8b0b-00000000000b",
                        "name": "B / L / แดง",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0006-4a06-8b06-000000000006",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0006-4a06-8b06-000000000006"
                        ],
                        "rowStatus": "ACTIVE"
                    },
                    {
                        "skuId": "e5f6a7b8-000c-4a0c-8b0c-00000000000c",
                        "name": "B / L / ดำ",
                        "combinationKey": "d0e1f2a3-0002-4a02-8b02-000000000002-d0e1f2a3-0005-4a05-8b05-000000000005-d0e1f2a3-0007-4a07-8b07-000000000007",
                        "optionValueIds": [
                            "d0e1f2a3-0002-4a02-8b02-000000000002",
                            "d0e1f2a3-0005-4a05-8b05-000000000005",
                            "d0e1f2a3-0007-4a07-8b07-000000000007"
                        ],
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
        "bizMessage": "Inquiry Product Success",
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
        "timestamp": "2026-11-05T12:43:45.123Z",
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

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Get products

```SQL
SELECT
    p.id as product_id,
    p.type_id,
    p.category_id,
    p.brand_id,
    p.name,
    p.slug,
    p.description,
    p.body,
    p.row_status
FROM product.m_product p
WHERE p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.category_id = '<sequence.categoryId>' -- only when categoryId is specified
AND (p.name ILIKE '%<sequence.search>%' OR p.description ILIKE '%<sequence.search>%') -- only when search is specified
ORDER BY p.created_at DESC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(p.id) as total_items
FROM product.m_product p
WHERE p.row_status <> 'DELETED'
AND p.id = '<sequence.id>' -- only when id is specified
AND p.category_id = '<sequence.categoryId>' -- only when categoryId is specified
AND (p.name ILIKE '%<sequence.search>%' OR p.description ILIKE '%<sequence.search>%') -- only when search is specified
```

### Table: [product.m_product_type](../../../schema/product/m_product_type.md)

#### QUERY - Get product type

```SQL
SELECT
    pt.id as type_id,
    pt.name as type_name
FROM product.m_product_type pt
WHERE pt.id IN ('<sequence.typeIds>')
```

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Get product category

```SQL
SELECT
    pc.id as category_id,
    pc.name as category_name
FROM product.m_product_category pc
WHERE pc.id IN ('<sequence.categoryIds>')
```

### Table: [product.m_product_brand](../../../schema/product/m_product_brand.md)

#### QUERY - Get product brand

```SQL
SELECT
    pb.id as brand_id,
    pb.name as brand_name
FROM product.m_product_brand pb
WHERE pb.id IN ('<sequence.brandIds>')
```

### Table: [product.m_product_attribute](../../../schema/product/m_product_attribute.md)

#### QUERY - Get product attributes

```SQL
SELECT
    pa.product_id,
    pa.attribute_id,
    pa.value
FROM product.m_product_attribute pa
WHERE pa.product_id IN ('<sequence.productIds>')
AND pa.row_status = 'ACTIVE'
ORDER BY pa.created_at
```

### Table: [product.m_product_category_attribute](../../../schema/product/m_product_category_attribute.md)

#### QUERY - Get product category attribute

```SQL
SELECT
    pca.id as attribute_id,
    pca.name as attribute_name
FROM product.m_product_category_attribute pca
WHERE pca.id IN ('<sequence.attributeIds>')
```

### Table: [product.m_product_image](../../../schema/product/m_product_image.md)

#### QUERY - Get product images

```SQL
SELECT
    pi.id as image_id,
    pi.product_id,
    pi.image_path
FROM product.m_product_image pi
WHERE pi.product_id IN ('<sequence.productIds>')
AND pi.option_value_id IS NULL
AND pi.row_status = 'ACTIVE'
ORDER BY pi.created_at
```

#### QUERY - Get product option value images

```SQL
SELECT
    pi.id as image_id,
    pi.option_value_id,
    pi.image_path
FROM product.m_product_image pi
WHERE pi.option_value_id IN ('<sequence.valueIds>')
AND pi.row_status = 'ACTIVE'
ORDER BY pi.created_at
```

### Table: [product.m_product_option](../../../schema/product/m_product_option.md)

#### QUERY - Get product options

```SQL
SELECT
    po.id as option_id,
    po.product_id,
    po.name,
    po.level_no
FROM product.m_product_option po
WHERE po.product_id IN ('<sequence.productIds>')
AND po.row_status = 'ACTIVE'
ORDER BY po.level_no
```

### Table: [product.m_product_option_value](../../../schema/product/m_product_option_value.md)

#### QUERY - Get product option values

```SQL
SELECT
    pov.id as value_id,
    pov.option_id,
    pov.value,
    pov.sort_order,
    pov.row_status
FROM product.m_product_option_value pov
WHERE pov.option_id IN ('<sequence.optionIds>')
AND pov.row_status <> 'DELETED'
ORDER BY pov.sort_order
```

### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)

#### QUERY - Get product SKUs

```SQL
SELECT
    ps.id as sku_id,
    ps.product_id,
    ps.name,
    ps.combination_key,
    ps.row_status
FROM product.m_product_sku ps
WHERE ps.product_id IN ('<sequence.productIds>')
AND ps.row_status <> 'DELETED'
ORDER BY ps.created_at, ps.combination_key
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### QUERY - Get product SKU option values

```SQL
SELECT
    psov.sku_id,
    psov.option_value_id
FROM product.m_product_sku_option_value psov
JOIN product.m_product_option_value pov ON pov.id = psov.option_value_id
JOIN product.m_product_option po ON po.id = pov.option_id
WHERE psov.sku_id IN ('<sequence.skuIds>')
AND psov.row_status <> 'DELETED'
ORDER BY psov.sku_id, po.level_no
```
