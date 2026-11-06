# [GET]: v1/user/address

| Title       | Description                                                                                                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry User Address API                                                                                                                                                                 |
| Method      | GET                                                                                                                                                                                      |
| Endpoint    | v{version}/user/address                                                                                                                                                                  |
| Version     | 1                                                                                                                                                                                        |
| Description | Inquiry the delivery addresses of the logged-in user with paging and search, Inquiry by id returns a list with one item, Deleted addresses are excluded, The default address comes first |

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
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Query Parameters

|     | Parameter Name | Data Type    | M/O      | Description                                                                          | Example                              |
| --- | -------------- | ------------ | -------- | ------------------------------------------------------------------------------------ | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL | User Address Id, Response is a list with one item                                    | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 2   | pageIndex      | Numeric      | OPTIONAL | Page index starting from 1, Defaults to 1                                            | 1                                    |
| 3   | pageSize       | Numeric      | OPTIONAL | Number of items per page (max 100), Defaults to 10                                   | 10                                   |
| 4   | search         | String       | OPTIONAL | Search by address title                                                              | home                                 |
| 5   | rowStatus      | String       | OPTIONAL | Row status filter (ACTIVE, INACTIVE), All statuses except DELETED when not specified | ACTIVE                               |

### User Address Inquiry Rules

- The addresses are the ones of the caller: `userId` comes from the access token. The id of another user's address returns an empty list.
- Addresses with `rowStatus` DELETED are never returned. Sensitive fields are decrypted by the system and returned as plain text over TLS.
- Sorted by `is_default` (the default first), then `created_at` descending, then `id`, so that pages never repeat or skip a row.
- `search` matches the title only (the other fields are encrypted).

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/user/address?pageIndex=1&pageSize=10&rowStatus=ACTIVE HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/user/address?pageIndex=1&pageSize=10&rowStatus=ACTIVE' \
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

|     | Parameter Name | Data Type                                     | M/O       | Source           | Field           | Description                                | Example |
| --- | -------------- | --------------------------------------------- | --------- | ---------------- | --------------- | ------------------------------------------ | ------- |
| 1   | items          | [Array of User Address](#user-address-object) | MANDATORY | Sequence Diagram | data.items      | User addresses, Empty array when not found |         |
| 2   | pageIndex      | Numeric                                       | MANDATORY | Sequence Diagram | data.pageIndex  | Current page index                         | 1       |
| 3   | pageSize       | Numeric                                       | MANDATORY | Sequence Diagram | data.pageSize   | Number of items per page                   | 10      |
| 4   | totalItems     | Numeric                                       | MANDATORY | Sequence Diagram | data.totalItems | Total number of items                      | 2       |
| 5   | totalPages     | Numeric                                       | MANDATORY | Sequence Diagram | data.totalPages | Total number of pages                      | 1       |

#### User Address Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                      | Description                   | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | -------------------------- | ----------------------------- | ------------------------------------ |
| 1   | userAddressId  | String: UUID | MANDATORY | Sequence Diagram | data.items[].userAddressId | User Address Id               | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 2   | title          | String       | MANDATORY | Sequence Diagram | data.items[].title         | Address title                 | Home (condo)                         |
| 3   | isDefault      | Boolean      | MANDATORY | Sequence Diagram | data.items[].isDefault     | Default address               | true                                 |
| 4   | address        | String       | MANDATORY | Sequence Diagram | data.items[].address       | Address (plain text)          | 123 Sukhumvit Road                   |
| 5   | city           | String       | MANDATORY | Sequence Diagram | data.items[].city          | City (plain text)             | Watthana                             |
| 6   | state          | String       | MANDATORY | Sequence Diagram | data.items[].state         | State (plain text)            | Bangkok                              |
| 7   | postalCode     | String       | MANDATORY | Sequence Diagram | data.items[].postalCode    | Postal code (plain text)      | 10110                                |
| 8   | country        | String       | MANDATORY | Sequence Diagram | data.items[].country       | Country (plain text)          | Thailand                             |
| 9   | rowStatus      | String       | MANDATORY | Sequence Diagram | data.items[].rowStatus     | Row status (ACTIVE, INACTIVE) | ACTIVE                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Address Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userAddressId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
                "title": "Home (condo)",
                "isDefault": true,
                "address": "123 Sukhumvit Road",
                "city": "Watthana",
                "state": "Bangkok",
                "postalCode": "10110",
                "country": "Thailand",
                "rowStatus": "ACTIVE"
            },
            {
                "userAddressId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
                "title": "Office",
                "isDefault": false,
                "address": "88 Rama IV Road",
                "city": "Khlong Toei",
                "state": "Bangkok",
                "postalCode": "10110",
                "country": "Thailand",
                "rowStatus": "ACTIVE"
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

Request: `GET v1/user/address?id=d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a`

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry User Address Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "items": [
            {
                "userAddressId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
                "title": "Home (condo)",
                "isDefault": true,
                "address": "123 Sukhumvit Road",
                "city": "Watthana",
                "state": "Bangkok",
                "postalCode": "10110",
                "country": "Thailand",
                "rowStatus": "ACTIVE"
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
        "bizMessage": "Inquiry User Address Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:20:00.123Z",
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
        "timestamp": "2026-11-06T09:40:40.123Z",
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
        "bizMessage": "Row status must be one of ACTIVE, INACTIVE.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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

### Table: [authen.t_user_address](../../../schema/authen/t_user_address.md)

#### QUERY - Get user addresses

```SQL
SELECT
    ua.id as user_address_id,
    ua.title,
    ua.is_default,
    ua.address,
    ua.city,
    ua.state,
    ua.postal_code,
    ua.country,
    ua.row_status
FROM authen.t_user_address ua
WHERE ua.user_id = '<sequence.userId>'
AND ua.row_status <> 'DELETED'
AND ua.id = '<sequence.id>' -- only when id is specified
AND ua.title ILIKE '%<sequence.search>%' -- only when search is specified
AND ua.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
ORDER BY ua.is_default DESC, ua.created_at DESC, ua.id
LIMIT <sequence.pageSize> OFFSET (<sequence.pageIndex> - 1) * <sequence.pageSize>
```

#### QUERY - Get total items

```SQL
SELECT
    COUNT(ua.id) as total_items
FROM authen.t_user_address ua
WHERE ua.user_id = '<sequence.userId>'
AND ua.row_status <> 'DELETED'
AND ua.id = '<sequence.id>' -- only when id is specified
AND ua.title ILIKE '%<sequence.search>%' -- only when search is specified
AND ua.row_status = '<sequence.rowStatus>' -- only when rowStatus is specified
```
