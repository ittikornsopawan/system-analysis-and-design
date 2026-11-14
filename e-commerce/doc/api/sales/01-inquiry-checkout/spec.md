---
name: "Inquiry Checkout API"
description: "Preview the orders that the logged-in customer would create from the cart, grouped by shop with the current selling price of the lot that is on sale, the totals of each order and the lines that cannot be ordered. Read it when you implement, review or test GET v1/checkout."
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/checkout

| Title       | Description                                                                                                                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Checkout API                                                                                                                                                                                                                                                         |
| Method      | GET                                                                                                                                                                                                                                                                          |
| Endpoint    | v{version}/checkout                                                                                                                                                                                                                                                          |
| Version     | 1                                                                                                                                                                                                                                                                            |
| Description | Preview the orders that the logged-in customer would create from the cart, grouped by shop with the current selling price of the lot that is on sale, the totals of each order and the lines that cannot be ordered, Nothing is written, The preview does not hold the stock |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Only the logged-in customer previews a checkout. The user comes from the access token and the request never carries a user id. `addressId` must be an ACTIVE address of the user, otherwise 404 (E10005). `cartIds` are lines of the cart of the user, a line of another user or a deleted line is not found (404, E10004), `cartIds` must not be duplicated (400, E10001) and has at most 100 ids. When `cartIds` is not specified every ACTIVE line of the cart is used, an empty selection is rejected with 400 (E10001).
- A line can be ordered only when it is AVAILABLE as the cart defines it: the shop, the product, the shop product, the shop product SKU and the product SKU are ACTIVE, one lot is on sale and the quantity of the line is not larger than the remaining quantity of that lot. One line that is not AVAILABLE rejects the whole request with 409 (E10007), nothing is created, the message names the line (`cartId`) and the reason (QUANTITY_EXCEEDS_STOCK, OUT_OF_STOCK or UNAVAILABLE).
- One order is created for each shop of the selected lines, so a cart with lines of two shops makes two orders. All orders are created in one transaction, either every order is created or none.
- The price of an item is the selling price of the lot that is on sale at the moment of the request and the item keeps that lot (`lot_id`), the price never changes afterwards. The profit of an item is the margin of that lot multiplied by the quantity (`gross_profit`, `shop_profit`, `platform_profit`).
- `totalTax` and `totalShipping` are 0.00 for now (the tax is not defined and the shipping fee is set by the payment API when the customer starts to pay).
- `totalDiscount` is the sum of the campaign discounts of the items of the shop and is 0.00 when no campaign applies, `totalAmount = totalPrice - totalDiscount + totalTax + totalShipping`, the database enforces this formula (`ck_t_order_total_amount_sum`). The `price` and the `total_price` of an item never change, the discount is kept in `discount` of the item.
- Discount rules: a campaign applies to an item only when the campaign is ACTIVE, `start_at <= now < end_at` (UTC), the shop of the item is in a live `campaign.t_campaign_shop` row (or the campaign has no live shop row, it is for every shop), the product of the item is in a live `campaign.t_campaign_product` row by `product_id` or by `product_category_id` equal to the category of the product, that category only (or the campaign has no live product row), and the campaign has a live discount and a live budget.
- One campaign for each item: when several campaigns apply, the one with the largest discount for that item wins, a tie goes to the smaller campaign `id`, discounts are never stacked and there is no fallback to another campaign when the budget of the winner is short. `PERCENTAGE`: `ROUND(price x quantity x discount_value / 100, 2)` (half up, for each item). `FIXED_AMOUNT`: `discount_value x quantity` (baht per unit). The discount of an item is never more than `(selling_price - cost_price) x quantity` of its lot, so an item is never sold below its cost, the part above that is dropped.
- The preview only reads the budget: when the remaining amount of a campaign is less than the discounts the campaign gives to one shop order, every cart line of that order that uses the campaign is returned in `problems` with the reason `DISCOUNT_BUDGET_EXHAUSTED` (`maxOrderQuantity` is the remaining quantity of the lot, the stock itself is fine) and `canCheckout` is false. Nothing is reserved here.
- This follows the campaign design (C2 to C9, approved by the product owner on 2026-11-06).
- The response lists the lines that can be ordered in `shops` (AVAILABLE lines only) and the lines that cannot in `problems`. `canCheckout` is true only when `problems` is empty and `shops` is not empty, it is the same test that the create order API applies. The stock can still change between the preview and the order, the order API checks again.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type             | M/O       | Description                                                                                                  | Example                              |
| --- | -------------- | --------------------- | --------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | addressId      | String: UUID          | MANDATORY | Shipping address of the customer, Must be an ACTIVE address of the user                                      | a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90 |
| 2   | cartIds        | Array of String: UUID | OPTIONAL  | Cart line Ids to check out (max 100, repeat the parameter), Every ACTIVE line of the cart when not specified | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/checkout?addressId=a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90&cartIds=c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607&cartIds=c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718&cartIds=c3c2d4e5-f607-4182-8c93-d4e5f6071829 HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/checkout?addressId=a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90&cartIds=c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607&cartIds=c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718&cartIds=c3c2d4e5-f607-4182-8c93-d4e5f6071829' \
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

|     | Parameter Name | Data Type                            | M/O       | Source           | Field            | Description                                                           | Example |
| --- | -------------- | ------------------------------------ | --------- | ---------------- | ---------------- | --------------------------------------------------------------------- | ------- |
| 1   | address        | [Object of Address](#address-object) | MANDATORY | Sequence Diagram | data.address     | Shipping address that was checked                                     |         |
| 2   | shops          | [Array of Shop](#shop-object)        | MANDATORY | Sequence Diagram | data.shops       | One entry for each order that would be created, ordered by shop name  |         |
| 3   | summary        | [Object of Summary](#summary-object) | MANDATORY | Sequence Diagram | data.summary     | Totals of all the orders                                              |         |
| 4   | problems       | [Array of Problem](#problem-object)  | MANDATORY | Sequence Diagram | data.problems    | Selected lines that cannot be ordered, Empty array when there is none |         |
| 5   | canCheckout    | Boolean                              | MANDATORY | Sequence Diagram | data.canCheckout | TRUE when the orders can be created now                               | true    |

#### Address Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                  | Description     | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------------- | --------------- | ------------------------------------ |
| 1   | addressId      | String: UUID | MANDATORY | Sequence Diagram | data.address.addressId | User Address Id | a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90 |
| 2   | title          | String       | MANDATORY | Sequence Diagram | data.address.title     | Address title   | Home                                 |

#### Shop Object

|     | Parameter Name | Data Type                     | M/O       | Source           | Field                      | Description                                             | Example                              |
| --- | -------------- | ----------------------------- | --------- | ---------------- | -------------------------- | ------------------------------------------------------- | ------------------------------------ |
| 1   | shopId         | String: UUID                  | MANDATORY | Sequence Diagram | data.shops[].shopId        | Shop Id                                                 | 5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d |
| 2   | shopName       | String                        | MANDATORY | Sequence Diagram | data.shops[].shopName      | Shop Name                                               | Acme Store                           |
| 3   | items          | [Array of Item](#item-object) | MANDATORY | Sequence Diagram | data.shops[].items         | Lines of the shop that can be ordered                   |                                      |
| 4   | totalPrice     | Numeric                       | MANDATORY | Sequence Diagram | data.shops[].totalPrice    | Sum of lineTotal of the items                           | 617.00                               |
| 5   | totalDiscount  | Numeric                       | MANDATORY | Sequence Diagram | data.shops[].totalDiscount | Discount of the campaign, 0.00 when no campaign applies | 0.00                                 |
| 6   | totalTax       | Numeric                       | MANDATORY | Sequence Diagram | data.shops[].totalTax      | Tax, 0.00 for now                                       | 0.00                                 |
| 7   | totalShipping  | Numeric                       | MANDATORY | Sequence Diagram | data.shops[].totalShipping | Shipping fee, 0.00 until the payment starts             | 0.00                                 |
| 8   | totalAmount    | Numeric                       | MANDATORY | Sequence Diagram | data.shops[].totalAmount   | totalPrice - totalDiscount + totalTax + totalShipping   | 617.00                               |

#### Item Object

|     | Parameter Name   | Data Type                                     | M/O       | Source           | Field                                 | Description                                                           | Example                              |
| --- | ---------------- | --------------------------------------------- | --------- | ---------------- | ------------------------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| 1   | cartId           | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].cartId           | Cart line Id                                                          | c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607 |
| 2   | productId        | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].productId        | Product Id                                                            | e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c |
| 3   | productName      | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].productName      | Product Name                                                          | Cotton Shirt                         |
| 4   | skuId            | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].skuId            | Product SKU Id                                                        | 7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e |
| 5   | shopProductSkuId | String: UUID                                  | MANDATORY | Sequence Diagram | data.shops[].items[].shopProductSkuId | Shop Product SKU Id                                                   | 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f |
| 6   | skuName          | String                                        | MANDATORY | Sequence Diagram | data.shops[].items[].skuName          | SKU Name                                                              | A / S                                |
| 7   | optionValues     | [Array of Option Value](#option-value-object) | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues     | Chosen value of every level in level order, Empty for the default SKU |                                      |
| 8   | imagePath        | String                                        | OPTIONAL  | Sequence Diagram | data.shops[].items[].imagePath        | Image of the SKU (same rule as the cart), Null when there is no image | /products/shirt/a.png                |
| 9   | quantity         | Numeric                                       | MANDATORY | Sequence Diagram | data.shops[].items[].quantity         | Quantity in the cart                                                  | 2                                    |
| 10  | sellingPrice     | Numeric                                       | MANDATORY | Sequence Diagram | data.shops[].items[].sellingPrice     | Selling price of the lot that is on sale now                          | 199.00                               |
| 11  | lineTotal        | Numeric                                       | MANDATORY | Sequence Diagram | data.shops[].items[].lineTotal        | sellingPrice x quantity                                               | 398.00                               |

#### Option Value Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                                          | Description  | Example |
| --- | -------------- | --------- | --------- | ---------------- | ---------------------------------------------- | ------------ | ------- |
| 1   | optionName     | String    | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues[].optionName | Level name   | Pattern |
| 2   | value          | String    | MANDATORY | Sequence Diagram | data.shops[].items[].optionValues[].value      | Chosen value | A       |

#### Summary Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                      | Description                            | Example |
| --- | -------------- | --------- | --------- | ---------------- | -------------------------- | -------------------------------------- | ------- |
| 1   | shopCount      | Numeric   | MANDATORY | Sequence Diagram | data.summary.shopCount     | Number of orders that would be created | 2       |
| 2   | itemCount      | Numeric   | MANDATORY | Sequence Diagram | data.summary.itemCount     | Number of items in all the orders      | 3       |
| 3   | totalQuantity  | Numeric   | MANDATORY | Sequence Diagram | data.summary.totalQuantity | Sum of quantity of all the items       | 4       |
| 4   | totalAmount    | Numeric   | MANDATORY | Sequence Diagram | data.summary.totalAmount   | Sum of totalAmount of the orders       | 1137.00 |

#### Problem Object

|     | Parameter Name   | Data Type    | M/O       | Source           | Field                            | Description                                                                                                                                                                                       | Example                              |
| --- | ---------------- | ------------ | --------- | ---------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | cartId           | String: UUID | MANDATORY | Sequence Diagram | data.problems[].cartId           | Cart line Id that cannot be ordered                                                                                                                                                               | c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718 |
| 2   | reason           | String       | MANDATORY | Sequence Diagram | data.problems[].reason           | QUANTITY_EXCEEDS_STOCK, OUT_OF_STOCK or UNAVAILABLE (same meaning as the availability of the cart) or DISCOUNT_BUDGET_EXHAUSTED (the budget of a campaign cannot cover the discount of the order) | QUANTITY_EXCEEDS_STOCK               |
| 3   | quantity         | Numeric      | MANDATORY | Sequence Diagram | data.problems[].quantity         | Quantity in the cart                                                                                                                                                                              | 10                                   |
| 4   | maxOrderQuantity | Numeric      | MANDATORY | Sequence Diagram | data.problems[].maxOrderQuantity | Remaining quantity of the lot that is on sale, 0 when OUT_OF_STOCK or UNAVAILABLE                                                                                                                 | 5                                    |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Checkout Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "address": {
            "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
            "title": "Home"
        },
        "shops": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Acme Store",
                "items": [
                    {
                        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
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
                        "lineTotal": 398.0
                    },
                    {
                        "cartId": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
                        "skuName": "Wireless Mouse",
                        "optionValues": [],
                        "imagePath": "/products/wireless-mouse/1.png",
                        "quantity": 1,
                        "sellingPrice": 219.0,
                        "lineTotal": 219.0
                    }
                ],
                "totalPrice": 617.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 617.0
            },
            {
                "shopId": "6b2c3d4e-5f60-4b7c-9d8e-0f1a2b3c4d5e",
                "shopName": "Beta Shop",
                "items": [
                    {
                        "cartId": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
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
                        "lineTotal": 520.0
                    }
                ],
                "totalPrice": 520.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 520.0
            }
        ],
        "summary": {
            "shopCount": 2,
            "itemCount": 3,
            "totalQuantity": 4,
            "totalAmount": 1137.0
        },
        "problems": [],
        "canCheckout": true
    }
}
```

#### Success - With Campaign

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Checkout Success",
        "requestId": "req-9c8d4e6f-7a0b-4b1c-d3e5-6f7a8b9c0d1e",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "address": {
            "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
            "title": "Home"
        },
        "shops": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Acme Store",
                "items": [
                    {
                        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
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
                        "lineTotal": 398.0
                    },
                    {
                        "cartId": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
                        "productId": "f2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
                        "productName": "Wireless Mouse",
                        "skuId": "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f",
                        "shopProductSkuId": "ad1e2f3a-4b5c-4d6e-9f7a-8b9c0d1e2f3a",
                        "skuName": "Wireless Mouse",
                        "optionValues": [],
                        "imagePath": "/products/wireless-mouse/1.png",
                        "quantity": 1,
                        "sellingPrice": 219.0,
                        "lineTotal": 219.0
                    }
                ],
                "totalPrice": 617.0,
                "totalDiscount": 61.7,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 555.3
            },
            {
                "shopId": "6b2c3d4e-5f60-4b7c-9d8e-0f1a2b3c4d5e",
                "shopName": "Beta Shop",
                "items": [
                    {
                        "cartId": "c3c2d4e5-f607-4182-8c93-d4e5f6071829",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
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
                        "lineTotal": 520.0
                    }
                ],
                "totalPrice": 520.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 520.0
            }
        ],
        "summary": {
            "shopCount": 2,
            "itemCount": 3,
            "totalQuantity": 4,
            "totalAmount": 1075.3
        },
        "problems": [],
        "canCheckout": true
    }
}
```

#### Success - With Problems

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Checkout Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "address": {
            "addressId": "a1d2e3f4-0b1c-4d2e-8f3a-4b5c6d7e8f90",
            "title": "Home"
        },
        "shops": [
            {
                "shopId": "5a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d",
                "shopName": "Acme Store",
                "items": [
                    {
                        "cartId": "c1a0b2c3-d4e5-4f60-8a71-b2c3d4e5f607",
                        "productId": "e1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c",
                        "productName": "Cotton Shirt",
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
                        "lineTotal": 398.0
                    }
                ],
                "totalPrice": 398.0,
                "totalDiscount": 0.0,
                "totalTax": 0.0,
                "totalShipping": 0.0,
                "totalAmount": 398.0
            }
        ],
        "summary": {
            "shopCount": 1,
            "itemCount": 1,
            "totalQuantity": 2,
            "totalAmount": 398.0
        },
        "problems": [
            {
                "cartId": "c2b1c3d4-e5f6-4071-9b82-c3d4e5f60718",
                "reason": "QUANTITY_EXCEEDS_STOCK",
                "quantity": 10,
                "maxOrderQuantity": 5
            }
        ],
        "canCheckout": false
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
        "bizMessage": "Address Id is a required field, Cart Ids must be valid UUIDs without duplicates, The selection must not be empty.",
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

#### Fail - Not Found

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10004",
        "bizMessage": "Cart item not found.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "Address not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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

#### QUERY - Get the cart lines to order

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
AND c.id IN ('<sequence.cartIds>') -- only when cartIds is specified, otherwise every ACTIVE line of the user
ORDER BY c.created_at
```

### Table: [shop.t_shop_product_sku](../../../schema/shop/t_shop_product_sku.md)

#### QUERY - Get the SKU of each line with the lot that is on sale

```SQL
SELECT
    ssk.id as shop_product_sku_id,
    sp.shop_id,
    sp.product_id,
    ssk.sku_id,
    s.name as shop_name,
    p.name as product_name,
    ps.name as sku_name,
    l.id as lot_id,
    l.selling_price,
    l.cost_price,
    l.gross_margin,
    l.share_margin,
    l.platform_margin,
    l.quantity as max_order_quantity
FROM shop.t_shop_product_sku ssk
INNER JOIN shop.t_shop_product sp
    ON sp.id = ssk.shop_product_id
    AND sp.row_status = 'ACTIVE'
INNER JOIN shop.m_shop s
    ON s.id = sp.shop_id
    AND s.row_status = 'ACTIVE'
INNER JOIN product.m_product p
    ON p.id = sp.product_id
    AND p.row_status = 'ACTIVE'
INNER JOIN product.m_product_sku ps
    ON ps.id = ssk.sku_id
    AND ps.row_status = 'ACTIVE'
LEFT JOIN shop.t_shop_product_sku_lot l
    ON l.shop_product_sku_id = ssk.id
    AND l.is_on_sale = TRUE
    AND l.row_status = 'ACTIVE'
WHERE (sp.shop_id, sp.product_id, ssk.sku_id) IN (<sequence.lineKeys>)
AND ssk.row_status = 'ACTIVE'
```

### Table: [authen.t_user_address](../../../schema/authen/t_user_address.md)

#### QUERY - Check the address of the user

```SQL
SELECT
    ua.id as address_id,
    ua.title,
    ua.address,
    ua.city,
    ua.state,
    ua.postal_code,
    ua.country
FROM authen.t_user_address ua
WHERE ua.id = '<sequence.addressId>'
AND ua.user_id = '<sequence.userId>'
AND ua.row_status = 'ACTIVE'
```

### Table: [campaign.m_campaign](../../../schema/campaign/m_campaign.md)

#### QUERY - Get the campaigns that apply to the shop

```SQL
SELECT
    c.id as campaign_id,
    c.name,
    d.discount_type,
    d.discount_value,
    b.id as budget_id,
    b.remaining
FROM campaign.m_campaign c
INNER JOIN campaign.t_campaign_discount d
    ON d.campaign_id = c.id
    AND d.row_status = 'ACTIVE'
INNER JOIN campaign.m_campaign_budget b
    ON b.campaign_id = c.id
    AND b.row_status = 'ACTIVE'
WHERE c.row_status = 'ACTIVE'
AND c.start_at <= NOW() AT TIME ZONE 'UTC'
AND NOW() AT TIME ZONE 'UTC' < c.end_at
AND (EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.shop_id = '<sequence.shopId>'
        AND cs.row_status = 'ACTIVE'
    ) OR NOT EXISTS (
        SELECT 1
        FROM campaign.t_campaign_shop cs
        WHERE cs.campaign_id = c.id
        AND cs.row_status = 'ACTIVE'
    ))
ORDER BY c.id
```

### Table: [campaign.t_campaign_product](../../../schema/campaign/t_campaign_product.md)

#### QUERY - Get the products and categories of the campaigns

```SQL
SELECT
    cp.campaign_id,
    cp.product_id,
    cp.product_category_id,
    p.id as matched_product_id
FROM campaign.t_campaign_product cp
LEFT JOIN product.m_product p
    ON p.id = cp.product_id
    OR p.category_id = cp.product_category_id
WHERE cp.campaign_id IN ('<sequence.campaignIds>')
AND cp.row_status = 'ACTIVE'
AND p.id IN ('<sequence.productIds>') -- a campaign without a live product row is for every product
```
