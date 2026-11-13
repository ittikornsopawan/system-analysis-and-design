# [GET]: v1/cart

| Title       | Description                                                                                                                                                                                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Cart API                                                                                                                                                                                                                    |
| Method      | GET                                                                                                                                                                                                                                 |
| Endpoint    | v{version}/cart                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                   |
| Description | Inquiry the cart of the logged-in customer grouped by shop, every line with the current selling price of the lot that is on sale, the stock status of the line and the totals, The cart has at most 100 lines so there is no paging |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- AVAILABLE: the SKU is on sale and the quantity is not larger than the remaining quantity of the lot that is on sale (`quantity <= maxOrderQuantity`). Only these lines count in the subtotals and the summary.
- QUANTITY_EXCEEDS_STOCK: the SKU is on sale but `quantity > maxOrderQuantity`. `sellingPrice` is returned, `lineTotal` is null, the customer must lower the quantity.
- OUT_OF_STOCK: the SKU has no lot on sale or the lot on sale has quantity 0. `sellingPrice` is null and `maxOrderQuantity` is 0.
- UNAVAILABLE: the shop, the product, the shop product, the shop product SKU or the product SKU is no longer ACTIVE. `sellingPrice` is null and `maxOrderQuantity` is 0. The line stays in the cart so the customer can remove it.
- The price is always the current price of the lot on sale. The cart keeps no price, so a change of the price or of the lot is visible the next time the cart is read.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------ | ------------------------------------ |
| 1   | shopId         | String: UUID | OPTIONAL | Shop Id, Return only the lines of the shop | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/cart HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/cart' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
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

|     | Parameter Name | Data Type                            | M/O       | Source           | Field        | Description                                                                                | Example |
| --- | -------------- | ------------------------------------ | --------- | ---------------- | ------------ | ------------------------------------------------------------------------------------------ | ------- |
| 1   | shops          | [Array of Shop](#shop-object)        | MANDATORY | Sequence Diagram | data.shops   | Shops that have lines in the cart ordered by shop name, Empty array when the cart is empty |         |
| 2   | summary        | [Object of Summary](#summary-object) | MANDATORY | Sequence Diagram | data.summary | Totals of the cart                                                                         |         |

#### Shop Object

|     | Parameter Name | Data Type                               | M/O       | Source           | Field                 | Description                                         | Example                              |
| --- | -------------- | --------------------------------------- | --------- | ---------------- | --------------------- | --------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID                            | MANDATORY | Sequence Diagram | data.shops[].shopId   | Shop Id                                             | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | shopName       | String                                  | MANDATORY | Sequence Diagram | data.shops[].shopName | Shop Name                                           | Acme Store                           |
| 3   | items          | [Array of Cart Item](#cart-item-object) | MANDATORY | Sequence Diagram | data.shops[].items    | Lines of the shop in the order they were added      |                                      |
| 4   | subtotal       | Numeric                                 | MANDATORY | Sequence Diagram | data.shops[].subtotal | Sum of lineTotal of the AVAILABLE lines of the shop | 398.00                               |

#### Cart Item Object

|     | Parameter Name   | Data Type                                     | M/O       | Source           | Field                                 | Description                                                                                                              | Example                              |
| --- | ---------------- | --------------------------------------------- | --------- | ---------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | cartId           | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].cartId           | Cart line Id                                                                                                             | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |
| 2   | productId        | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].productId        | Product Id                                                                                                               | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | productName      | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].productName      | Product Name                                                                                                             | Cotton Shirt                         |
| 4   | productSlug      | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].productSlug      | Product Slug, Used in the web URL /{productId}/{slug}                                                                    | cotton-shirt                         |
| 5   | skuId            | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].skuId            | Product SKU Id                                                                                                           | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 6   | shopProductSkuId | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].shopProductSkuId | Shop Product SKU Id                                                                                                      | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 7   | skuName          | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].skuName          | SKU Name                                                                                                                 | A / S                                |
| 8   | optionValues     | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues     | Chosen value of every level in level order, Empty for the default SKU                                                    |                                      |
| 9   | imagePath        | String                                        | OPTIONAL  | Sequence Diagram | data.shops[].items[].imagePath        | Image of the lowest level chosen value that has an image, otherwise the first product image, Null when there is no image | /products/shirt/a.png                |
| 10  | quantity         | Numeric                                       | MANDATORY | Sequence Diagram | data.shops[].items[].quantity         | Quantity in the cart                                                                                                     | 2                                    |
| 11  | sellingPrice     | Numeric                                       | OPTIONAL  | Sequence Diagram | data.shops[].items[].sellingPrice     | Selling price of the lot that is on sale now, Null when the SKU is not on sale                                           | 199.00                               |
| 12  | lineTotal        | Numeric                                       | OPTIONAL  | Sequence Diagram | data.shops[].items[].lineTotal        | sellingPrice x quantity, Null unless availability is AVAILABLE                                                           | 398.00                               |
| 13  | availability     | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].availability     | AVAILABLE, QUANTITY_EXCEEDS_STOCK, OUT_OF_STOCK or UNAVAILABLE                                                           | AVAILABLE                            |
| 14  | maxOrderQuantity | Numeric                                       | MANDATORY | Sequence Diagram | data.shops[].items[].maxOrderQuantity | Remaining quantity of the lot that is on sale, 0 when the SKU is out of stock or not on sale                             | 80                                   |

#### Option Value Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                          | Description  | Example |
| --- | -------------- | --------- | --------- | ---------------- | ---------------------------------------------- | ------------ | ------- |
| 1   | optionName     | String    | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues[].optionName | Level name   | Pattern |
| 2   | value          | String    | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues[].value      | Chosen value | A       |

#### Summary Object

|     | Parameter Name     | Data Type | M/O       | Source           | Field                           | Description                                                                                                                   | Example |
| --- | ------------------ | --------- | --------- | ---------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------- |
| 1   | lineCount          | Numeric   | MANDATORY | Sequence Diagram | data.summary.lineCount          | Number of lines in the cart                                                                                                   | 4       |
| 2   | availableLineCount | Numeric   | MANDATORY | Sequence Diagram | data.summary.availableLineCount | Number of AVAILABLE lines                                                                                                     | 2       |
| 3   | totalQuantity      | Numeric   | MANDATORY | Sequence Diagram | data.summary.totalQuantity      | Sum of quantity of the AVAILABLE lines                                                                                        | 3       |
| 4   | subtotal           | Numeric   | MANDATORY | Sequence Diagram | data.summary.subtotal           | Sum of lineTotal of the AVAILABLE lines of every shop, Discount, tax and shipping are not included (they belong to the order) | 918.00  |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Cart Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shops": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Acme Store",
                "items": [
                    {
                        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "productSlug": "cotton-shirt",
                        "skuId": "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e",
                        "shopProductSkuId": "9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f",
                        "skuName": "A / S",
                        "optionValues": [
                            {
                                "optionName": "Pattern",
                                "value": "A"
                            },
                            {
                                "optionName": "Size",
                                "value": "S"
                            }
                        ],
                        "imagePath": "/products/shirt/a.png",
                        "quantity": 2,
                        "sellingPrice": 199.0,
                        "lineTotal": 398.0,
                        "availability": "AVAILABLE",
                        "maxOrderQuantity": 80
                    },
                    {
                        "cartId": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "productSlug": "wireless-mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
                        "skuName": "Wireless Mouse",
                        "optionValues": [],
                        "imagePath": "/products/wireless-mouse/1.png",
                        "quantity": 10,
                        "sellingPrice": 219.0,
                        "lineTotal": null,
                        "availability": "QUANTITY_EXCEEDS_STOCK",
                        "maxOrderQuantity": 5
                    }
                ],
                "subtotal": 398.0
            },
            {
                "shopId": "6b2c3d4e-5f60-4b7c-9d8e-0f1a2b3c4d5e",
                "shopName": "Beta Shop",
                "items": [
                    {
                        "cartId": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
                        "productSlug": "cotton-shirt",
                        "skuId": "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a",
                        "shopProductSkuId": "be2f3a4b-5c6d-4e7f-8a8b-9c0d1e2f3a4b",
                        "skuName": "B / M",
                        "optionValues": [
                            {
                                "optionName": "Pattern",
                                "value": "B"
                            },
                            {
                                "optionName": "Size",
                                "value": "M"
                            }
                        ],
                        "imagePath": "/products/shirt/main.png",
                        "quantity": 1,
                        "sellingPrice": 520.0,
                        "lineTotal": 520.0,
                        "availability": "AVAILABLE",
                        "maxOrderQuantity": 12
                    },
                    {
                        "cartId": "c4d3e5f6-0718-4293-9da4-e5f607182930",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Keyboard",
                        "productSlug": "wireless-keyboard",
                        "skuId": "ae1f2a3b-4c5d-4e6f-8a7b-8c9d0e1f2a3b",
                        "shopProductSkuId": "bf2a3b4c-5d6e-4f70-9b8c-9d0e1f2a3b4c",
                        "skuName": "Wireless Keyboard",
                        "optionValues": [],
                        "imagePath": null,
                        "quantity": 1,
                        "sellingPrice": null,
                        "lineTotal": null,
                        "availability": "UNAVAILABLE",
                        "maxOrderQuantity": 0
                    }
                ],
                "subtotal": 520.0
            }
        ],
        "summary": {
            "lineCount": 4,
            "availableLineCount": 2,
            "totalQuantity": 3,
            "subtotal": 918.0
        }
    }
}
```

#### Success - Empty Cart

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Cart Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shops": [],
        "summary": {
            "lineCount": 0,
            "availableLineCount": 0,
            "totalQuantity": 0,
            "subtotal": 0.0
        }
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
        "bizMessage": "Shop Id must be a valid UUID.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "requestId": "req-70a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:07:49.123Z",
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

### Table: [cart.t_cart](../../../schema/cart/t_cart.md)

#### QUERY - Get the lines of the user

```SQL
SELECT
    c.id as cart_id,
    c.shop_id,
    c.product_id,
    c.sku_id,
    c.quantity
FROM cart.t_cart c
WHERE c.user_id = '<sequence.userId>'
AND c.row_status = 'ACTIVE'
AND c.shop_id = '<sequence.shopId>' -- only when shopId is specified
ORDER BY c.created_at
```

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Get shops

```SQL
SELECT
    s.id as shop_id,
    s.name as shop_name,
    s.row_status
FROM shop.m_shop s
WHERE s.id IN ('<sequence.shopIds>')
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Get the shop product SKUs of the lines

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    sp.shop_id,
    sp.product_id,
    ssk.sku_id,
    ssk.row_status as sku_row_status,
    sp.row_status as shop_product_row_status
FROM shop.t_shop_product_sku ssk
INNER JOIN shop.t_shop_product sp
    ON sp.id = ssk.shop_product_id
WHERE (sp.shop_id, sp.product_id, ssk.sku_id) IN (<sequence.lineKeys>)
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

### Table: [product.m_product](../../../schema/product/m_product.md)

#### QUERY - Get products

```SQL
SELECT
    p.id as product_id,
    p.name,
    p.slug,
    p.row_status
FROM product.m_product p
WHERE p.id IN ('<sequence.productIds>')
```

### Table: [product.m_product_sku](../../../schema/product/m_product_sku.md)

#### QUERY - Get product SKUs

```SQL
SELECT
    ps.id as sku_id,
    ps.name,
    ps.row_status
FROM product.m_product_sku ps
WHERE ps.id IN ('<sequence.skuIds>')
```

### Table: [product.m_product_sku_option_value](../../../schema/product/m_product_sku_option_value.md)

#### QUERY - Get the chosen option values of the SKUs

```SQL
SELECT
    psov.sku_id,
    po.name as option_name,
    pov.id as option_value_id,
    pov.value
FROM product.m_product_sku_option_value psov
INNER JOIN product.m_product_option_value pov
    ON pov.id = psov.option_value_id
INNER JOIN product.m_product_option po
    ON po.id = pov.option_id
WHERE psov.sku_id IN ('<sequence.skuIds>')
AND psov.row_status <> 'DELETED'
ORDER BY psov.sku_id, po.level_no
```

### Table: [product.m_product_image](../../../schema/product/m_product_image.md)

#### QUERY - Get the images of the lines

```SQL
SELECT
    pi.product_id,
    pi.option_value_id,
    pi.image_path
FROM product.m_product_image pi
WHERE (pi.product_id IN ('<sequence.productIds>') AND pi.option_value_id IS NULL
    OR pi.option_value_id IN ('<sequence.optionValueIds>'))
AND pi.row_status = 'ACTIVE'
ORDER BY pi.created_at
```
