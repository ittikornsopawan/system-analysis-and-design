# [POST]: v1/consent/type/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Consent Type Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Endpoint    | v{version}/consent/type/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Insert, update or delete multiple consent types at the same time, only a platform administrator can call it, Each consent type is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All consent types are processed in one transaction in the request order, If any consent type fails then no consent type is changed |

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

|     | Parameter Name | Data Type                                     | M/O       | Description                                                      | Example |
| --- | -------------- | --------------------------------------------- | --------- | ---------------------------------------------------------------- | ------- |
| 1   | consentTypes   | [Array of Consent Type](#consent-type-object) | MANDATORY | Consent types to insert, update or delete (min 1, max 100 items) |         |

#### Consent Type Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                                                                             | Example                                               |
| --- | -------------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | id             | String: UUID | OPTIONAL  | Consent Type Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED consent type counts as not found, Must not be duplicated in the request                                                                                       | b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e                  |
| 2   | name           | String       | MANDATORY | Consent Type Name (max 128 characters), Unique among consent types that are not DELETED                                                                                                                                                                                 | Terms and Conditions                                  |
| 3   | description    | String       | OPTIONAL  | Consent Type Description (max 1000 characters), Not specified keeps the current description on update, null clears it                                                                                                                                                   | Terms that every customer accepts to use the platform |
| 4   | isRequired     | Boolean      | OPTIONAL  | Reference data only, the consent decides whether it must be accepted, Defaults to FALSE on insert, Not specified keeps the current value on update                                                                                                                      | true                                                  |
| 5   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the consent type is not used by any consent that is not DELETED | ACTIVE                                                |

### Consent Type Rules (same as the single upsert, applied per consent type)

- Every consent type follows the rules of [the single upsert](../06-upsert-consent-type/spec.md#consent-type-rules): unique name among consent types that are not DELETED, required `name`, DELETED is final, delete and archive are rejected while a consent that is not DELETED uses the consent type.
- The consent types are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no consent type is changed.
- `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). The name of a DELETED item is not compared.
- Swapping the names of two consent types in one request is rejected with 409 (E10003) at the first item, because that name is still held by the other consent type when the item is checked. Rename them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- Permission: the same as the single upsert, only a platform administrator can call this API, any other caller gets 403 (E10009). The check is made once for the request, after the existence checks of all items and before the duplicate name and in-use checks, so the 403 message has no item position. Approved by the product owner (answered through the lead SA, 2026-11-06).
- The response is HTTP 200 for every successful batch, including a batch that deletes.

#### Example Body Parameters

```JSON
{
    "consentTypes": [
        {
            "name": "Terms and Conditions",
            "description": "Terms that every customer accepts to use the platform",
            "isRequired": true,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Marketing",
            "description": "Permission to send promotions and news",
            "isRequired": false,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c5d6e7f8-a9b0-4c1d-8e2f-4a5b6c7d8e9f",
            "name": "Cookies",
            "description": "Permission to store cookies in the browser",
            "isRequired": false,
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/consent/type/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "consentTypes": [
        {
            "name": "Terms and Conditions",
            "description": "Terms that every customer accepts to use the platform",
            "isRequired": true,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Marketing",
            "description": "Permission to send promotions and news",
            "isRequired": false,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c5d6e7f8-a9b0-4c1d-8e2f-4a5b6c7d8e9f",
            "name": "Cookies",
            "description": "Permission to store cookies in the browser",
            "isRequired": false,
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/consent/type/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "consentTypes": [
        {
            "name": "Terms and Conditions",
            "description": "Terms that every customer accepts to use the platform",
            "isRequired": true,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
            "name": "Marketing",
            "description": "Permission to send promotions and news",
            "isRequired": false,
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c5d6e7f8-a9b0-4c1d-8e2f-4a5b6c7d8e9f",
            "name": "Cookies",
            "description": "Permission to store cookies in the browser",
            "isRequired": false,
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field             | Description                                            | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ----------------- | ------------------------------------------------------ | ------- |
| 1   | consentTypes   | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.consentTypes | Result of each consent type, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                             | Description                                                  | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | --------------------------------- | ------------------------------------------------------------ | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.consentTypes[].index         | Index of the consent type in the request, Starting from 0    | 0                                    |
| 2   | consentTypeId  | String: UUID | MANDATORY | Sequence Diagram | data.consentTypes[].consentTypeId | Inserted, Updated, Deleted or Archived Consent Type Id       | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.consentTypes[].action        | Action of the consent type (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Consent Type Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consentTypes": [
            {
                "index": 0,
                "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "consentTypeId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "consentTypeId": "c5d6e7f8-a9b0-4c1d-8e2f-4a5b6c7d8e9f",
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
        "bizMessage": "consentTypes[0]: Name is a required field.",
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
        "bizMessage": "Consent types must contain 1 to 100 items.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:47.123Z",
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
        "bizMessage": "consentTypes[2]: Id is duplicated with consentTypes[1].",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:54.123Z",
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
        "bizMessage": "consentTypes[2]: Name is duplicated with consentTypes[0].",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:41:01.123Z",
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
        "bizMessage": "consentTypes[1]: Row status must not be DELETED when inserting a consent type.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:22.123Z",
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
        "bizMessage": "consentTypes[1]: Consent type not found.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:15.123Z",
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
        "bizMessage": "You do not have permission to change consent types.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "consentTypes[0]: Consent type name already exists.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:45:29.123Z",
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
        "bizMessage": "consentTypes[2]: Consent type is used by consents.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:40:36.123Z",
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

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Check existing consent type

```SQL
SELECT
    ct.id as consent_type_id
FROM consent.m_consent_type ct
WHERE ct.id = '<sequence.consentTypes.id>'
AND ct.row_status <> 'DELETED' -- the id of a DELETED consent type counts as not found
```

#### QUERY - Check duplicate name

```SQL
SELECT
    ct.id as consent_type_id
FROM consent.m_consent_type ct
WHERE ct.name = '<sequence.consentTypes.name>'
AND ct.row_status <> 'DELETED'
AND ct.id <> '<sequence.consentTypes.id>' -- only when id is specified
```

#### INSERT - Create consent type

```SQL
INSERT INTO consent.m_consent_type (
    created_by,
    row_status,
    name,
    description,
    is_required
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.consentTypes.rowStatus>',
    '<sequence.consentTypes.name>',
    '<sequence.consentTypes.description>',
    '<sequence.consentTypes.isRequired>'
)
RETURNING id as consent_type_id
```

#### UPDATE - Update or delete consent type

```SQL
UPDATE consent.m_consent_type
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.consentTypes.rowStatus>',
    name = '<sequence.consentTypes.name>',
    description = '<sequence.consentTypes.description>', -- only when description is specified (null clears it)
    is_required = '<sequence.consentTypes.isRequired>' -- only when isRequired is specified
WHERE id = '<sequence.consentTypes.id>'
RETURNING id as consent_type_id
```

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Check consent in use

```SQL
SELECT
    c.id as consent_id
FROM consent.t_consent c
WHERE c.consent_type_id = '<sequence.consentTypes.id>' -- only when rowStatus is DELETED or ARCHIVED
AND c.row_status <> 'DELETED'
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
