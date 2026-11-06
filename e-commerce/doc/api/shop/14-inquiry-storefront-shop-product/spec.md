# [GET]: v1/storefront/shop/product

| Title       | Description                                                                                                                                                                                                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Storefront Shop Product API                                                                                                                                                                                                                                                                   |
| Method      | GET                                                                                                                                                                                                                                                                                                   |
| Endpoint    | v{version}/storefront/shop/product                                                                                                                                                                                                                                                                    |
| Version     | 1                                                                                                                                                                                                                                                                                                     |
| Description | Inquiry the products of a shop for the page of the shop, with the first image, the price range and the stock status of each product and the shop itself (name, description, shop type and images), with paging, search, category filter, stock filter and sort, Public API, no access token is needed |

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

|     | Parameter Name | Data Type | M/O       | Description       | Example                                  |
| --- | -------------- | --------- | --------- | ----------------- | ---------------------------------------- |
| 1   | timestamp      | DateTime  | MANDATORY | Request timestamp | 2026-11-06T09:00:00.123Z                 |
| 2   | requestId      | String    | OPTIONAL  | API Request Id    | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

### Query Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                  | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | shopId         | String: UUID | MANDATORY | Shop Id                                                                                                      | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | categoryId     | String: UUID | OPTIONAL  | Product Category Id, The products of the category and of all its sub categories                              | d3e4f5a6-b7c8-4d9e-8f0a-1b2c3d4e5f6a |
| 3   | search         | String       | OPTIONAL  | Search by product name or product description                                                                | shirt                                |
| 4   | inStock        | Boolean      | OPTIONAL  | true: only the products that are in stock, Not specified: every product, also the ones that are out of stock | true                                 |
| 5   | sort           | String       | OPTIONAL  | Order of the list (NEWEST, PRICE_ASC, PRICE_DESC, NAME_ASC), Defaults to NEWEST                              | NEWEST                               |
| 6   | pageIndex      | Numeric      | OPTIONAL  | Page index starting from 1, Defaults to 1                                                                    | 1                                    |
| 7   | pageSize       | Numeric      | OPTIONAL  | Number of items per page (max 100), Defaults to 10                                                           | 10                                   |

### Shop Product List Rules

The rules of this section, including the rule that a shop that is not ACTIVE has no page, were approved by the product owner.

- This API is public: it needs no access token. It never returns the cost price, the margins, the margin rates of the shop, the quantity of a lot or the users of the shop.
- The shop must be ACTIVE, otherwise 404 (E10004). A shop that is INACTIVE, LOCKED, ARCHIVED or DELETED has no page, its products cannot be seen (approved by the product owner). A shop that is ACTIVE and has no product to show answers 200 with `items` empty.
- A product is listed when it is ACTIVE (`product.m_product`), listed by the shop (`shop.t_shop_product` ACTIVE) and has at least one SKU that is ACTIVE for the shop and for the product. This is the same condition as the product page ([shop/04](../04-inquiry-storefront-product/spec.md)), so every product of the list has a page.
- The price and the stock come from the lot that is on sale of each SKU, as on the product page: a SKU is in stock when its lot on sale (`is_on_sale`, ACTIVE) has a quantity greater than 0. `priceFrom` and `priceTo` are the lowest and the highest selling price of the SKUs that are in stock, `stockStatus` is IN_STOCK when at least one SKU is in stock. A product with no SKU in stock is still listed with `stockStatus` OUT_OF_STOCK and `priceFrom` and `priceTo` null, and `inStock` true hides it.
- `sort`: NEWEST (default) lists the products by the time the shop listed them (`shop.t_shop_product.created_at`), newest first. PRICE_ASC and PRICE_DESC order by `priceFrom` and the products that are out of stock come last in both. NAME_ASC orders by the product name. Every sort ends with `productId` ascending as the tie-break, so the pages never repeat or skip a product.
- `categoryId` selects the products of the category and of all its sub categories (a recursive query on `product.m_product_category`), a category that does not exist gives an empty list. `search` matches the product name or the product description (ILIKE). `totalItems` counts the products after the filters.
- `imagePath` is the first image of the product among the images of the product level that are ACTIVE, ordered by creation time and then `id`. The images of the option values are not used.
- The shop block has the name, the description, the shop type name and the images of the shop that are ACTIVE, in the order type, seq, creation time and id (the shop type name is returned also when the shop type is not ACTIVE). It has no margin and no member.
- The status of a shop product is not changed by any API (the shop product is created by the shop product SKU API). A shop stops showing a product by closing all the SKUs of the product with that API.
- The list is a picture of the stock at the time it is read, it does not reserve anything.

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/storefront/shop/product?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&sort=NEWEST&pageIndex=1&pageSize=10 HTTP/1.1
Host: www.domain.com
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/storefront/shop/product?shopId=5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d&sort=NEWEST&pageIndex=1&pageSize=10' \
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

|     | Parameter Name | Data Type                           | M/O       | Source           | Field           | Description                                          | Example |
| --- | -------------- | ----------------------------------- | --------- | ---------------- | --------------- | ---------------------------------------------------- | ------- |
| 1   | shop           | [Object of Shop](#shop-object)      | MANDATORY | Sequence Diagram | data.shop       | The shop of the list                                 |         |
| 2   | items          | [Array of Product](#product-object) | MANDATORY | Sequence Diagram | data.items      | Products of the shop, Empty array when there is none |         |
| 3   | pageIndex      | Numeric                             | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                                   | 1       |
| 4   | pageSize       | Numeric                             | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                             | 10      |
| 5   | totalItems     | Numeric                             | MANDATORY | Sequence Diagram | data.totalItems | Total number of products after the filters           | 4       |
| 6   | totalPages     | Numeric                             | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                                | 1       |

#### Shop Object

|     | Parameter Name | Data Type                                 | M/O       | Source           | Field                 | Description                                                                                               | Example                                   |
| --- | -------------- | ----------------------------------------- | --------- | ---------------- | --------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | shopId         | String: UUID                              | MANDATORY | Sequence Diagram | data.shop.shopId      | Shop Id                                                                                                   | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d      |
| 2   | name           | String                                    | MANDATORY | Sequence Diagram | data.shop.name        | Shop Name                                                                                                 | Aof Fashion                               |
| 3   | description    | String                                    | MANDATORY | Sequence Diagram | data.shop.description | Shop Description                                                                                          | Clothes and accessories for everyday wear |
| 4   | typeName       | String                                    | MANDATORY | Sequence Diagram | data.shop.typeName    | Shop Type Name                                                                                            | Fashion Store                             |
| 5   | images         | [Array of Shop Image](#shop-image-object) | MANDATORY | Sequence Diagram | data.shop.images      | Images of the shop that are ACTIVE (logo, banners, wallpaper), Ordered by type, seq, creation time and id |                                           |

#### Shop Image Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                        | Description                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------------------- | ------------------------------------ | ------------------------------------ |
| 1   | imageId        | String: UUID | MANDATORY | Sequence Diagram | data.shop.images[].imageId   | Shop Image Id                        | 6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e |
| 2   | type           | String       | MANDATORY | Sequence Diagram | data.shop.images[].type      | Image type (LOGO, BANNER, WALLPAPER) | LOGO                                 |
| 3   | imagePath      | String       | MANDATORY | Sequence Diagram | data.shop.images[].imagePath | Image Path                           | /shops/aof-fashion/logo.png          |

#### Product Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                    | Description                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | productId      | String: UUID | MANDATORY | Sequence Diagram | data.items[].productId   | Product Id                                                                                            | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.items[].name        | Product Name                                                                                          | Cotton Shirt                         |
| 3   | slug           | String       | MANDATORY | Sequence Diagram | data.items[].slug        | Product Slug, Used in the web URL /{productId}/{slug}                                                 | cotton-shirt                         |
| 4   | imagePath      | String       | OPTIONAL  | Sequence Diagram | data.items[].imagePath   | First image of the product (a product level image that is ACTIVE), Null when the product has no image | /products/shirt/main.png             |
| 5   | priceFrom      | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].priceFrom   | Lowest selling price of the SKUs that are in stock, Null when no SKU is in stock                      | 199.00                               |
| 6   | priceTo        | Numeric      | OPTIONAL  | Sequence Diagram | data.items[].priceTo     | Highest selling price of the SKUs that are in stock, Null when no SKU is in stock                     | 219.00                               |
| 7   | stockStatus    | String       | MANDATORY | Sequence Diagram | data.items[].stockStatus | IN_STOCK when at least one SKU is in stock, otherwise OUT_OF_STOCK                                    | IN_STOCK                             |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Shop Product Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shop": {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "name": "Aof Fashion",
            "description": "Clothes and accessories for everyday wear",
            "typeName": "Fashion Store",
            "images": [
                {
                    "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "BANNER",
                    "imagePath": "/shops/aof-fashion/banner-1.png"
                },
                {
                    "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "imagePath": "/shops/aof-fashion/logo.png"
                }
            ]
        },
        "items": [
            {
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "name": "Cotton Shirt",
                "slug": "cotton-shirt",
                "imagePath": "/products/shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 219.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                "name": "Canvas Tote",
                "slug": "canvas-tote",
                "imagePath": null,
                "priceFrom": null,
                "priceTo": null,
                "stockStatus": "OUT_OF_STOCK"
            },
            {
                "productId": "c7d6e5f4-a3b2-4c1d-9e0f-8a7b6c5d4e3f",
                "name": "Wool Scarf",
                "slug": "wool-scarf",
                "imagePath": "/products/wool-scarf/main.png",
                "priceFrom": 350.00,
                "priceTo": 350.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "a9b8c7d6-e5f4-4a3b-8c2d-1e0f9a8b7c6d",
                "name": "Linen Shirt",
                "slug": "linen-shirt",
                "imagePath": "/products/linen-shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 249.00,
                "stockStatus": "IN_STOCK"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 4,
        "totalPages": 1
    }
}
```

#### Success - Price Ascending

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Shop Product Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:08:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shop": {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "name": "Aof Fashion",
            "description": "Clothes and accessories for everyday wear",
            "typeName": "Fashion Store",
            "images": [
                {
                    "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "BANNER",
                    "imagePath": "/shops/aof-fashion/banner-1.png"
                },
                {
                    "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "imagePath": "/shops/aof-fashion/logo.png"
                }
            ]
        },
        "items": [
            {
                "productId": "a9b8c7d6-e5f4-4a3b-8c2d-1e0f9a8b7c6d",
                "name": "Linen Shirt",
                "slug": "linen-shirt",
                "imagePath": "/products/linen-shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 249.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "name": "Cotton Shirt",
                "slug": "cotton-shirt",
                "imagePath": "/products/shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 219.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "c7d6e5f4-a3b2-4c1d-9e0f-8a7b6c5d4e3f",
                "name": "Wool Scarf",
                "slug": "wool-scarf",
                "imagePath": "/products/wool-scarf/main.png",
                "priceFrom": 350.00,
                "priceTo": 350.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                "name": "Canvas Tote",
                "slug": "canvas-tote",
                "imagePath": null,
                "priceFrom": null,
                "priceTo": null,
                "stockStatus": "OUT_OF_STOCK"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 4,
        "totalPages": 1
    }
}
```

#### Success - In Stock Only

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Storefront Shop Product Success",
        "requestId": "req-8a1b2c3d-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:08:30.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shop": {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "name": "Aof Fashion",
            "description": "Clothes and accessories for everyday wear",
            "typeName": "Fashion Store",
            "images": [
                {
                    "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "BANNER",
                    "imagePath": "/shops/aof-fashion/banner-1.png"
                },
                {
                    "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "imagePath": "/shops/aof-fashion/logo.png"
                }
            ]
        },
        "items": [
            {
                "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                "name": "Cotton Shirt",
                "slug": "cotton-shirt",
                "imagePath": "/products/shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 219.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "c7d6e5f4-a3b2-4c1d-9e0f-8a7b6c5d4e3f",
                "name": "Wool Scarf",
                "slug": "wool-scarf",
                "imagePath": "/products/wool-scarf/main.png",
                "priceFrom": 350.00,
                "priceTo": 350.00,
                "stockStatus": "IN_STOCK"
            },
            {
                "productId": "a9b8c7d6-e5f4-4a3b-8c2d-1e0f9a8b7c6d",
                "name": "Linen Shirt",
                "slug": "linen-shirt",
                "imagePath": "/products/linen-shirt/main.png",
                "priceFrom": 199.00,
                "priceTo": 249.00,
                "stockStatus": "IN_STOCK"
            }
        ],
        "pageIndex": 1,
        "pageSize": 10,
        "totalItems": 3,
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
        "bizMessage": "Inquiry Storefront Shop Product Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:09:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "shop": {
            "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
            "name": "Aof Fashion",
            "description": "Clothes and accessories for everyday wear",
            "typeName": "Fashion Store",
            "images": [
                {
                    "imageId": "6b7c8d9e-0002-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "BANNER",
                    "imagePath": "/shops/aof-fashion/banner-1.png"
                },
                {
                    "imageId": "6b7c8d9e-0001-4b2c-8d3e-4f5a6b7c8d9e",
                    "type": "LOGO",
                    "imagePath": "/shops/aof-fashion/logo.png"
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
        "bizMessage": "Shop Id is a required field.",
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

#### Fail - Bad Request Sort

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Sort must be one of NEWEST, PRICE_ASC, PRICE_DESC, NAME_ASC and In Stock must be true or false.",
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
        "bizMessage": "Shop not found.",
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

### Table: [shop.m_shop](../../../schema/shop/m_shop.md)

#### QUERY - Get shop

```SQL
SELECT
    s.id as shop_id,
    s.type_id,
    s.name,
    s.description
FROM shop.m_shop s
WHERE s.id = '<sequence.shopId>'
AND s.row_status = 'ACTIVE' -- a shop that is not ACTIVE has no page
```

### Table: [shop.m_shop_type](../../../schema/shop/m_shop_type.md)

#### QUERY - Get shop type name

```SQL
SELECT
    st.name as type_name
FROM shop.m_shop_type st
WHERE st.id = '<sequence.typeId>'
```

### Table: [shop.m_shop_image](../../../schema/shop/m_shop_image.md)

#### QUERY - Get shop images

```SQL
SELECT
    si.id as image_id,
    si.type,
    si.image_path
FROM shop.m_shop_image si
WHERE si.shop_id = '<sequence.shopId>'
AND si.row_status = 'ACTIVE'
ORDER BY si.type, si.seq, si.created_at, si.id
```

### Table: [product.m_product_category](../../../schema/product/m_product_category.md)

#### QUERY - Get the category and its sub categories

```SQL
WITH RECURSIVE categories AS (
    SELECT pc.id
    FROM product.m_product_category pc
    WHERE pc.id = '<sequence.categoryId>' -- only when categoryId is specified
    AND pc.row_status <> 'DELETED'
    UNION ALL
    SELECT pc.id
    FROM product.m_product_category pc
    INNER JOIN categories c
        ON pc.parent_id = c.id
    WHERE pc.row_status <> 'DELETED'
)
SELECT
    c.id as category_id
FROM categories c
```

### Table: [shop.t_shop_product](../../../schema/shop/t_shop_product.md)

#### QUERY - Get products of the shop

```SQL
WITH visible AS (
    SELECT
        sp.id as shop_product_id,
        sp.product_id,
        sp.created_at as listed_at,
        MIN(l.selling_price) as price_from,
        MAX(l.selling_price) as price_to
    FROM shop.t_shop_product sp
    INNER JOIN shop.t_shop_product_sku ssk
        ON ssk.shop_product_id = sp.id
        AND ssk.row_status = 'ACTIVE'
    INNER JOIN product.m_product_sku ps
        ON ps.id = ssk.sku_id
        AND ps.row_status = 'ACTIVE'
    LEFT JOIN shop.t_shop_product_sku_lot l
        ON l.shop_product_sku_id = ssk.id
        AND l.is_on_sale = TRUE
        AND l.row_status = 'ACTIVE'
        AND l.quantity > 0
    WHERE sp.shop_id = '<sequence.shopId>'
    AND sp.row_status = 'ACTIVE'
    GROUP BY sp.id, sp.product_id, sp.created_at
)
SELECT
    p.id as product_id,
    p.name,
    p.slug,
    v.price_from,
    v.price_to,
    CASE WHEN v.price_from IS NULL THEN 'OUT_OF_STOCK' ELSE 'IN_STOCK' END as stock_status
FROM visible v
INNER JOIN product.m_product p
    ON p.id = v.product_id
WHERE p.row_status = 'ACTIVE'
AND p.category_id IN ('<sequence.categoryIds>') -- only when categoryId is specified
AND (p.name ILIKE '%<sequence.search>%' OR p.description ILIKE '%<sequence.search>%') -- only when search is specified
AND v.price_from IS NOT NULL -- only when inStock is true
ORDER BY v.listed_at DESC, p.id -- sort NEWEST (default)
-- ORDER BY (v.price_from IS NULL), v.price_from, p.id -- sort PRICE_ASC, the products out of stock last
-- ORDER BY (v.price_from IS NULL), v.price_from DESC, p.id -- sort PRICE_DESC, the products out of stock last
-- ORDER BY p.name, p.id -- sort NAME_ASC
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
WITH visible AS (
    SELECT
        sp.id as shop_product_id,
        sp.product_id,
        MIN(l.selling_price) as price_from
    FROM shop.t_shop_product sp
    INNER JOIN shop.t_shop_product_sku ssk
        ON ssk.shop_product_id = sp.id
        AND ssk.row_status = 'ACTIVE'
    INNER JOIN product.m_product_sku ps
        ON ps.id = ssk.sku_id
        AND ps.row_status = 'ACTIVE'
    LEFT JOIN shop.t_shop_product_sku_lot l
        ON l.shop_product_sku_id = ssk.id
        AND l.is_on_sale = TRUE
        AND l.row_status = 'ACTIVE'
        AND l.quantity > 0
    WHERE sp.shop_id = '<sequence.shopId>'
    AND sp.row_status = 'ACTIVE'
    GROUP BY sp.id, sp.product_id, sp.created_at
)
SELECT
    COUNT(p.id) as total_items
FROM visible v
INNER JOIN product.m_product p
    ON p.id = v.product_id
WHERE p.row_status = 'ACTIVE'
AND p.category_id IN ('<sequence.categoryIds>') -- only when categoryId is specified
AND (p.name ILIKE '%<sequence.search>%' OR p.description ILIKE '%<sequence.search>%') -- only when search is specified
AND v.price_from IS NOT NULL -- only when inStock is true
```

### Table: [product.m_product_image](../../../schema/product/m_product_image.md)

#### QUERY - Get the first image of each product

```SQL
SELECT DISTINCT ON (pi.product_id)
    pi.product_id,
    pi.image_path
FROM product.m_product_image pi
WHERE pi.product_id IN ('<sequence.productIds>')
AND pi.option_value_id IS NULL
AND pi.row_status = 'ACTIVE'
ORDER BY pi.product_id, pi.created_at, pi.id
```
