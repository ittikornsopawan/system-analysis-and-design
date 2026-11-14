---
name: "Inquiry Storefront Product API"
description: "Inquiry the product page of a product sold by a shop, with levels, option values and their images, every SKU with the selling price of the lot that is on sale and the stock status, the price range and which option values are available. Read it when you implement, review or test GET v1/storefront/product."
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/storefront/product

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Storefront Product API                                                                                                                                                                                                                                                                                                                                                        |
| Method      | GET                                                                                                                                                                                                                                                                                                                                                                                   |
| Endpoint    | v{version}/storefront/product                                                                                                                                                                                                                                                                                                                                                         |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Inquiry the product page of a product sold by a shop, with levels, option values and their images, every SKU with the selling price of the lot that is on sale and the stock status, the price range and which option values are available, Public API, no access token, The web page address is /{productId}/{slug}, the page is found by productId and the slug is only for reading |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only a product that is ACTIVE, sold by a shop that is ACTIVE (`shop.m_shop`), listed by the shop (`shop.t_shop_product` ACTIVE) and has at least one SKU that is ACTIVE for the shop and for the product is returned, otherwise 404 (E10004). A shop that is INACTIVE, LOCKED, ARCHIVED or DELETED has no page, its products cannot be seen or bought (approved by the product owner). The page is found by `productId` and `shopId`, the `slug` is only part of the web address `/{productId}/{slug}`, the web page redirects to the current slug when the slug in the address is different.
- The selling price of a SKU is the selling price of its lot that is on sale (`is_on_sale`), the stock status comes from the remaining quantity of that lot. A SKU with no lot on sale, or whose lot on sale has quantity 0, is OUT_OF_STOCK and has `sellingPrice` null. The API never returns cost price, margins or the quantity of lots that are not on sale.
- When the customer has not selected every level yet the client uses the SKUs whose `optionValueIds` contain the selected values: the price range is the lowest and highest `sellingPrice` of those SKUs that are IN_STOCK, `priceFrom` and `priceTo` are the same range for the whole product.
- Image shown for a selection is the image of the lowest level selected value that has an image, otherwise the product level images.
- A product without level has one default SKU with `combinationKey` empty and `optionValueIds` empty.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description       | Example                                  |
| --- | -------------- | --------- | --------- | ----------------- | ---------------------------------------- |
| 1   | timestamp      | DateTime  | MANDATORY | Request timestamp | 2026-11-06T09:00:00.123Z                 |
| 2   | requestId      | String    | OPTIONAL  | API Request Id    | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Query Parameters

|     | Parameter Name | Data Type    | M/O       | Description | Example                              |
| --- | -------------- | ------------ | --------- | ----------- | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id     | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | productId      | String: UUID | MANDATORY | Product Id  | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/storefront/product?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c HTTP/1.1
Host: www.domain.com
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/storefront/product?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&productId=e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                         | M/O       | Source           | Field            | Description                                                                          | Example                                         |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------- |
| 1   | productId      | String: UUID                      | MANDATORY | Sequence Diagram | data.productId   | Product Id                                                                           | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c            |
| 2   | shopId         | String: UUID                      | MANDATORY | Sequence Diagram | data.shopId      | Shop Id                                                                              | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d            |
| 3   | name           | String                            | MANDATORY | Sequence Diagram | data.name        | Product Name                                                                         | Cotton Shirt                                    |
| 4   | slug           | String                            | MANDATORY | Sequence Diagram | data.slug        | Product Slug, Used in the web URL /{productId}/{slug}                                | cotton-shirt                                    |
| 5   | description    | String                            | MANDATORY | Sequence Diagram | data.description | Product Description                                                                  | Soft cotton shirt in two patterns and two sizes |
| 6   | body           | String                            | MANDATORY | Sequence Diagram | data.body        | Product Detail                                                                       | 100% cotton, machine washable.                  |
| 7   | images         | [Array of Image](#image-object)   | MANDATORY | Sequence Diagram | data.images      | Product level images, Images of option values are in options[].values[].images       |                                                 |
| 8   | options        | [Array of Option](#option-object) | MANDATORY | Sequence Diagram | data.options     | Levels of the product, Empty array when the product has no level                     |                                                 |
| 9   | skus           | [Array of SKU](#sku-object)       | MANDATORY | Sequence Diagram | data.skus        | SKUs that the shop sells, Only SKUs that are ACTIVE for the shop and for the product |                                                 |
| 10  | priceFrom      | Numeric                           | OPTIONAL  | Sequence Diagram | data.priceFrom   | Lowest selling price of the SKUs that are in stock, Null when no SKU is in stock     | 199.00                                          |
| 11  | priceTo        | Numeric                           | OPTIONAL  | Sequence Diagram | data.priceTo     | Highest selling price of the SKUs that are in stock, Null when no SKU is in stock    | 219.00                                          |
| 12  | stockStatus    | String                            | MANDATORY | Sequence Diagram | data.stockStatus | IN_STOCK when at least one SKU is in stock, otherwise OUT_OF_STOCK                   | IN_STOCK                                        |

#### Image Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                   | Description      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------------------- | ---------------- | ------------------------------------ |
| 1   | imageId        | String: UUID | MANDATORY | Sequence Diagram | data.images[].imageId   | Product Image Id | 44440000-aaaa-4bbb-8ccc-dddd00000001 |
| 2   | imagePath      | String       | MANDATORY | Sequence Diagram | data.images[].imagePath | Image Path       | /products/shirt/main.png             |

#### Option Object

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field                   | Description                                 | Example                              |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | ----------------------- | ------------------------------------------- | ------------------------------------ |
| 1   | optionId       | String: UUID                                  | MANDATORY | Sequence Diagram | data.options[].optionId | Product Option Id                           | 33330000-aaaa-4bbb-8ccc-dddd00000001 |
| 2   | name           | String                                        | MANDATORY | Sequence Diagram | data.options[].name     | Level Name                                  | Pattern                              |
| 3   | levelNo        | Numeric                                       | MANDATORY | Sequence Diagram | data.options[].levelNo  | Level number starting from 1                | 1                                    |
| 4   | values         | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.options[].values   | ACTIVE values of the level in display order |                                      |

#### Option Value Object

|     | Parameter Name | Data Type                       | M/O       | Source           | Field                               | Description                                                                                           | Example                              |
| --- | -------------- | ------------------------------- | --------- | ---------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | valueId        | String: UUID                    | MANDATORY | Sequence Diagram | data.options[].values[].valueId     | Product Option Value Id                                                                               | 11110000-aaaa-4bbb-8ccc-dddd00000001 |
| 2   | value          | String                          | MANDATORY | Sequence Diagram | data.options[].values[].value       | Value                                                                                                 | A                                    |
| 3   | sortOrder      | Numeric                         | MANDATORY | Sequence Diagram | data.options[].values[].sortOrder   | Display order starting from 1                                                                         | 1                                    |
| 4   | isAvailable    | Boolean                         | MANDATORY | Sequence Diagram | data.options[].values[].isAvailable | TRUE when at least one SKU that uses the value is in stock, FALSE means the client disables the value | true                                 |
| 5   | images         | [Array of Image](#image-object) | MANDATORY | Sequence Diagram | data.options[].values[].images      | Images of the value                                                                                   |                                      |

#### SKU Object

|     | Parameter Name   | Data Type             | M/O       | Source           | Field                        | Description                                                                                        | Example                                                                   |
| --- | ---------------- | --------------------- | --------- | ---------------- | ---------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | skuId            | String: UUID          | MANDATORY | Sequence Diagram | data.skus[].skuId            | Product SKU Id                                                                                     | 55550001-aaaa-4bbb-8ccc-dddd00000001                                      |
| 2   | shopProductSkuId | String: UUID          | MANDATORY | Sequence Diagram | data.skus[].shopProductSkuId | Shop Product SKU Id, Used when adding the SKU to the cart                                          | 66660001-aaaa-4bbb-8ccc-dddd00000001                                      |
| 3   | name             | String                | MANDATORY | Sequence Diagram | data.skus[].name             | SKU Name                                                                                           | A / S                                                                     |
| 4   | combinationKey   | String                | MANDATORY | Sequence Diagram | data.skus[].combinationKey   | Value ids joined by '-' in level order, Empty for the default SKU of a product without level       | 11110000-aaaa-4bbb-8ccc-dddd00000001-22220000-aaaa-4bbb-8ccc-dddd00000001 |
| 5   | optionValueIds   | Array of String: UUID | MANDATORY | Sequence Diagram | data.skus[].optionValueIds   | Option value ids of the SKU in level order, Empty for the default SKU                              | 11110000-aaaa-4bbb-8ccc-dddd00000001                                      |
| 6   | sellingPrice     | Numeric               | OPTIONAL  | Sequence Diagram | data.skus[].sellingPrice     | Selling price of the lot that is on sale, Null when the SKU has no lot on sale                     | 199.00                                                                    |
| 7   | stockStatus      | String                | MANDATORY | Sequence Diagram | data.skus[].stockStatus      | IN_STOCK when a lot is on sale and its quantity is greater than 0, otherwise OUT_OF_STOCK          | IN_STOCK                                                                  |
| 8   | maxOrderQuantity | Numeric               | MANDATORY | Sequence Diagram | data.skus[].maxOrderQuantity | Largest quantity of one order item, The remaining quantity of the lot on sale, 0 when OUT_OF_STOCK | 80                                                                        |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Product Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
        "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
        "name": "Cotton Shirt",
        "slug": "cotton-shirt",
        "description": "Soft cotton shirt in two patterns and two sizes",
        "body": "100% cotton, machine washable.",
        "images": [
            {
                "imageId": "44440000-aaaa-4bbb-8ccc-dddd00000009",
                "imagePath": "/products/shirt/main.png"
            }
        ],
        "options": [
            {
                "optionId": "33330000-aaaa-4bbb-8ccc-dddd00000001",
                "name": "ลาย",
                "levelNo": 1,
                "values": [
                    {
                        "valueId": "11110000-aaaa-4bbb-8ccc-dddd00000001",
                        "value": "A",
                        "sortOrder": 1,
                        "isAvailable": true,
                        "images": [
                            {
                                "imageId": "44440000-aaaa-4bbb-8ccc-dddd00000001",
                                "imagePath": "/products/shirt/a.png"
                            }
                        ]
                    },
                    {
                        "valueId": "11110000-aaaa-4bbb-8ccc-dddd00000002",
                        "value": "B",
                        "sortOrder": 2,
                        "isAvailable": true,
                        "images": []
                    }
                ]
            },
            {
                "optionId": "33330000-aaaa-4bbb-8ccc-dddd00000002",
                "name": "ไซส์",
                "levelNo": 2,
                "values": [
                    {
                        "valueId": "22220000-aaaa-4bbb-8ccc-dddd00000001",
                        "value": "S",
                        "sortOrder": 1,
                        "isAvailable": true,
                        "images": []
                    },
                    {
                        "valueId": "22220000-aaaa-4bbb-8ccc-dddd00000002",
                        "value": "M",
                        "sortOrder": 2,
                        "isAvailable": true,
                        "images": []
                    }
                ]
            }
        ],
        "skus": [
            {
                "skuId": "55550001-aaaa-4bbb-8ccc-dddd00000001",
                "shopProductSkuId": "66660001-aaaa-4bbb-8ccc-dddd00000001",
                "name": "A / S",
                "combinationKey": "11110000-aaaa-4bbb-8ccc-dddd00000001-22220000-aaaa-4bbb-8ccc-dddd00000001",
                "optionValueIds": [
                    "11110000-aaaa-4bbb-8ccc-dddd00000001",
                    "22220000-aaaa-4bbb-8ccc-dddd00000001"
                ],
                "sellingPrice": 199.0,
                "stockStatus": "IN_STOCK",
                "maxOrderQuantity": 80
            },
            {
                "skuId": "55550002-aaaa-4bbb-8ccc-dddd00000001",
                "shopProductSkuId": "66660002-aaaa-4bbb-8ccc-dddd00000001",
                "name": "A / M",
                "combinationKey": "11110000-aaaa-4bbb-8ccc-dddd00000001-22220000-aaaa-4bbb-8ccc-dddd00000002",
                "optionValueIds": [
                    "11110000-aaaa-4bbb-8ccc-dddd00000001",
                    "22220000-aaaa-4bbb-8ccc-dddd00000002"
                ],
                "sellingPrice": 199.0,
                "stockStatus": "IN_STOCK",
                "maxOrderQuantity": 12
            },
            {
                "skuId": "55550003-aaaa-4bbb-8ccc-dddd00000001",
                "shopProductSkuId": "66660003-aaaa-4bbb-8ccc-dddd00000001",
                "name": "B / S",
                "combinationKey": "11110000-aaaa-4bbb-8ccc-dddd00000002-22220000-aaaa-4bbb-8ccc-dddd00000001",
                "optionValueIds": [
                    "11110000-aaaa-4bbb-8ccc-dddd00000002",
                    "22220000-aaaa-4bbb-8ccc-dddd00000001"
                ],
                "sellingPrice": 219.0,
                "stockStatus": "IN_STOCK",
                "maxOrderQuantity": 5
            },
            {
                "skuId": "55550004-aaaa-4bbb-8ccc-dddd00000001",
                "shopProductSkuId": "66660004-aaaa-4bbb-8ccc-dddd00000001",
                "name": "B / M",
                "combinationKey": "11110000-aaaa-4bbb-8ccc-dddd00000002-22220000-aaaa-4bbb-8ccc-dddd00000002",
                "optionValueIds": [
                    "11110000-aaaa-4bbb-8ccc-dddd00000002",
                    "22220000-aaaa-4bbb-8ccc-dddd00000002"
                ],
                "sellingPrice": null,
                "stockStatus": "OUT_OF_STOCK",
                "maxOrderQuantity": 0
            }
        ],
        "priceFrom": 199.0,
        "priceTo": 219.0,
        "stockStatus": "IN_STOCK"
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
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "requestId": "req-80a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:08:56.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Get shop product

```SQL
SELECT
    sp.id as shop_product_id,
    sp.shop_id,
    sp.product_id
FROM shop.t_shop_product sp
INNER JOIN shop.m_shop s
    ON s.id = sp.shop_id
    AND s.row_status = 'ACTIVE' -- a shop that is not ACTIVE has no page
WHERE sp.shop_id = '<sequence.shopId>'
AND sp.product_id = '<sequence.productId>'
AND sp.row_status = 'ACTIVE'
```

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Get product

```SQL
SELECT
    p.id as product_id,
    p.name,
    p.slug,
    p.description,
    p.body
FROM product.m_product p
WHERE p.id = '<sequence.productId>'
AND p.row_status = 'ACTIVE'
```

### Table: [product.m_product_image](../../../schema/product/m_product_image.md)

#### QUERY - Get product level images

```SQL
SELECT
    pi.id as image_id,
    pi.image_path
FROM product.m_product_image pi
WHERE pi.product_id = '<sequence.productId>'
AND pi.option_value_id IS NULL
AND pi.row_status = 'ACTIVE'
ORDER BY pi.created_at
```

#### QUERY - Get option value images

```SQL
SELECT
    pi.id as image_id,
    pi.option_value_id,
    pi.image_path
FROM product.m_product_image pi
WHERE pi.option_value_id IN ('<sequence.optionValueIds>')
AND pi.row_status = 'ACTIVE'
ORDER BY pi.created_at
```

### Table: [product.m_product_option](../../../schema/product/m_product_option.md)

#### QUERY - Get options

```SQL
SELECT
    po.id as option_id,
    po.name,
    po.level_no
FROM product.m_product_option po
WHERE po.product_id = '<sequence.productId>'
AND po.row_status = 'ACTIVE'
ORDER BY po.level_no
```

### Table: [product.m_product_option_value](../../../schema/product/m_product_option_value.md)

#### QUERY - Get ACTIVE option values

```SQL
SELECT
    pov.id as value_id,
    pov.option_id,
    pov.value,
    pov.sort_order
FROM product.m_product_option_value pov
WHERE pov.option_id IN ('<sequence.optionIds>')
AND pov.row_status = 'ACTIVE'
ORDER BY pov.sort_order
```

### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)

#### QUERY - Get SKUs of the product that the shop sells

```SQL
SELECT
    ps.id as sku_id,
    ssk.id as shop_product_sku_id,
    ps.name,
    ps.combination_key
FROM product.m_product_sku ps
INNER JOIN shop.t_shop_product_sku ssk
    ON ssk.sku_id = ps.id
    AND ssk.shop_product_id = '<sequence.shopProductId>'
    AND ssk.row_status = 'ACTIVE'
WHERE ps.product_id = '<sequence.productId>'
AND ps.row_status = 'ACTIVE'
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### QUERY - Get option values of the SKUs

```SQL
SELECT
    psov.sku_id,
    psov.option_value_id
FROM product.m_product_sku_option_value psov
INNER JOIN product.m_product_option_value pov
    ON pov.id = psov.option_value_id
INNER JOIN product.m_product_option po
    ON po.id = pov.option_id
WHERE psov.sku_id IN ('<sequence.skuIds>')
AND psov.row_status <> 'DELETED'
ORDER BY psov.sku_id, po.level_no
```

### Table: [shop.t_shop_product_sku_lot](../../../schema/shop/t_shop_product_sku_lot.md)

#### QUERY - Get the lot that is on sale of each shop product SKU

```SQL
SELECT
    l.shop_product_sku_id,
    l.selling_price,
    l.quantity
FROM shop.t_shop_product_sku_lot l
WHERE l.shop_product_sku_id IN ('<sequence.shopProductSkuIds>')
AND l.is_on_sale = TRUE
AND l.row_status = 'ACTIVE'
```
