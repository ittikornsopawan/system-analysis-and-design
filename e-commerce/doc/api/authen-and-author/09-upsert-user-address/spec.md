# [POST]: v1/user/address/upsert

| Title       | Description                                                                                                                                                                                                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert User Address API                                                                                                                                                                                                                                                                        |
| Method      | POST                                                                                                                                                                                                                                                                                           |
| Endpoint    | v{version}/user/address/upsert                                                                                                                                                                                                                                                                 |
| Version     | 1                                                                                                                                                                                                                                                                                              |
| Description | Insert, update or delete a delivery address of the logged-in user, Insert when id is not specified (HTTP 201), Update when id is specified (HTTP 200), Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), A user has one default address, At most 10 addresses per user |

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
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-06T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                              | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | User Address Id, Insert when not specified, Update or Delete when specified, The id of a DELETED address or of another user counts as not found                                          | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 2   | title          | String       | MANDATORY | Address title (max 128 characters)                                                                                                                                                       | Home                                 |
| 3   | isDefault      | Boolean      | OPTIONAL  | Default address, TRUE makes this the default and the earlier default stops being one, FALSE or not specified keeps the current value (the first ACTIVE address of a user is the default) | true                                 |
| 4   | address        | String       | MANDATORY | Address, Plain text over TLS, The system encrypts it                                                                                                                                     | 123 Sukhumvit Road                   |
| 5   | city           | String       | MANDATORY | City, Plain text over TLS                                                                                                                                                                | Watthana                             |
| 6   | state          | String       | MANDATORY | State, Plain text over TLS                                                                                                                                                               | Bangkok                              |
| 7   | postalCode     | String       | MANDATORY | Postal code, Plain text over TLS                                                                                                                                                         | 10110                                |
| 8   | country        | String       | MANDATORY | Country, Plain text over TLS                                                                                                                                                             | Thailand                             |
| 9   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED, DELETED is not allowed when inserting, There is no archive                                              | ACTIVE                               |

### User Address Rules

- The address belongs to the caller: `userId` comes from the access token. An address of another user, and an address that is DELETED, counts as not found (404, E10004).
- There is no batch (the rows belong to the customer) and no archive. Delete is a soft delete (`rowStatus` DELETED), the row is never removed because `sales.t_order.address_id` points at it. DELETED is final. INACTIVE is reversible, an update with `rowStatus` ACTIVE opens the address again. Only an ACTIVE address can be used at checkout (`sales/01-inquiry-checkout`, `sales/02-create-order`). `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts an address.
- Sensitive fields (`address`, `city`, `state`, `postalCode`, `country`) are sent as plain text over TLS and encrypted by the system before they are stored, with the same deterministic encryption as `01-register`. `title` stays plain text.
- **Default address:** a user has at most one default address (partial unique index `uq_t_user_address_user_id_default`). The first ACTIVE address of a user becomes the default whatever `isDefault` says. A request with `isDefault` TRUE makes the address the default and the earlier default is cleared in the same transaction. `isDefault` FALSE, or not sending it, keeps the current value of an existing address, so a default is only replaced by choosing another default.
- Deleting or deactivating the default address clears its default flag and makes the ACTIVE address that was changed last the default (when there is one). `isDefault` TRUE together with `rowStatus` INACTIVE or DELETED is rejected with 400 (E10001).
- A user can have at most 10 addresses that are not DELETED (configurable). An insert over the limit is 400 (E10001).
- Lock order: lock the `authen.m_user` row of the caller first (`FOR UPDATE`), then read and write the addresses.
- Execution order: validate the request (400) -> lock the user row -> existence and owner check (404) -> address limit (400, insert only) -> clear the old default when this address becomes the default -> write -> promote another default when the default was deleted or deactivated.
- HTTP status: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body).

#### Example Body Parameters

##### Insert

```JSON
{
    "title": "Home",
    "isDefault": true,
    "address": "123 Sukhumvit Road",
    "city": "Watthana",
    "state": "Bangkok",
    "postalCode": "10110",
    "country": "Thailand",
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "title": "Home (condo)",
    "isDefault": true,
    "address": "123 Sukhumvit Road",
    "city": "Watthana",
    "state": "Bangkok",
    "postalCode": "10110",
    "country": "Thailand",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "title": "Home (condo)",
    "isDefault": true,
    "address": "123 Sukhumvit Road",
    "city": "Watthana",
    "state": "Bangkok",
    "postalCode": "10110",
    "country": "Thailand",
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/user/address/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "title": "Home",
    "isDefault": true,
    "address": "123 Sukhumvit Road",
    "city": "Watthana",
    "state": "Bangkok",
    "postalCode": "10110",
    "country": "Thailand",
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/user/address/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "title": "Home",
    "isDefault": true,
    "address": "123 Sukhumvit Road",
    "city": "Watthana",
    "state": "Bangkok",
    "postalCode": "10110",
    "country": "Thailand",
    "rowStatus": "ACTIVE"
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field              | Description                                                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------ | -------------------------------------------------------------------- | ------------------------------------ |
| 1   | userAddressId  | String: UUID | MANDATORY | Sequence Diagram | data.userAddressId | Inserted or Updated Address Id, Not returned when deleted (HTTP 204) | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert User Address Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userAddressId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
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
        "bizMessage": "Update User Address Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userAddressId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Title, Address, City, State, Postal Code and Country are required fields.",
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
        "bizMessage": "Row status must not be DELETED when inserting a user address.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Limit

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "A user can have at most 10 addresses.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Default

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "A default address must be ACTIVE.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "User address not found.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- every authen API locks the user row first
```

### Table: [authen.t_user_address](../../../schema/authen/t_user_address.md)

#### QUERY - Check existing address

```SQL
SELECT
    ua.id as user_address_id,
    ua.is_default
FROM authen.t_user_address ua
WHERE ua.id = '<sequence.id>'
AND ua.user_id = '<sequence.userId>'
AND ua.row_status <> 'DELETED' -- an address of another user or a DELETED address counts as not found
```

#### QUERY - Count addresses

```SQL
SELECT
    COUNT(ua.id) as addresses
FROM authen.t_user_address ua
WHERE ua.user_id = '<sequence.userId>'
AND ua.row_status <> 'DELETED' -- only when inserting
```

#### QUERY - Check an ACTIVE address exists

```SQL
SELECT
    ua.id as user_address_id
FROM authen.t_user_address ua
WHERE ua.user_id = '<sequence.userId>'
AND ua.row_status = 'ACTIVE'
AND ua.id <> '<sequence.id>' -- only when id is specified
```

#### UPDATE - Clear the old default

```SQL
UPDATE authen.t_user_address
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    is_default = FALSE
WHERE user_id = '<sequence.userId>'
AND is_default
AND row_status <> 'DELETED'
AND id <> '<sequence.id>' -- only when id is specified
```

#### INSERT - Create user address

```SQL
INSERT INTO authen.t_user_address (
    created_by,
    row_status,
    user_id,
    title,
    is_default,
    address,
    city,
    state,
    postal_code,
    country
)
VALUES (
    '<sequence.userId>',
    '<sequence.rowStatus>',
    '<sequence.userId>',
    '<sequence.title>',
    '<sequence.isDefault>', -- TRUE when it is the first ACTIVE address of the user
    '<sequence.addressBytes>',
    '<sequence.cityBytes>',
    '<sequence.stateBytes>',
    '<sequence.postalCodeBytes>',
    '<sequence.countryBytes>'
)
RETURNING id as user_address_id
```

#### UPDATE - Update or delete user address

```SQL
UPDATE authen.t_user_address
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    title = '<sequence.title>',
    is_default = '<sequence.isDefault>', -- FALSE when rowStatus is INACTIVE or DELETED
    address = '<sequence.addressBytes>',
    city = '<sequence.cityBytes>',
    state = '<sequence.stateBytes>',
    postal_code = '<sequence.postalCodeBytes>',
    country = '<sequence.countryBytes>'
WHERE id = '<sequence.id>'
AND user_id = '<sequence.userId>'
RETURNING id as user_address_id
```

#### UPDATE - Promote another default address

```SQL
UPDATE authen.t_user_address
SET
    updated_by = '<sequence.userId>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    is_default = TRUE
WHERE id = (
    SELECT ua.id
    FROM authen.t_user_address ua
    WHERE ua.user_id = '<sequence.userId>'
    AND ua.row_status = 'ACTIVE'
    ORDER BY COALESCE(ua.updated_at, ua.created_at) DESC, ua.id
    LIMIT 1
) -- only when the default address was deleted or deactivated
```
