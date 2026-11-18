---
name: "Upsert Parameter Batch API"
description: "Insert, update, delete or archive several parameters in one transaction, with the parent, cycle and children rules checked on the final state, only for a platform administrator authorized from the verified JWT roles claim after the caller lock and the current credential check. Read it when you implement, review or test POST v1/parameter/upsert/batch."
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-18T07:49:47+07:00
---

# [POST]: v1/parameter/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Parameter Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Endpoint    | v{version}/parameter/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Description | Insert, update or delete multiple parameters at the same time, Each parameter is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All parameters are processed in one transaction in the request order, If any parameter fails then no parameter is changed, only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- Every parameter follows the rules of the single upsert (parameter/01): the whole parameter is replaced, `key` and `value` are required, `key` is unique among parameters that are not DELETED, the localized texts and `metadata` have the same format, `expiredAt` is later than `effectiveAt`, DELETED is final, the parent must exist and be ACTIVE, a parent cannot be its own descendant, and delete and archive are rejected while a child parameter that is not DELETED exists.
- The rules of this batch, including the final-state checks below, were decided by Josh, SA Lead, delegated by the owner, 2026-11-18 (parameter API review).
- The parameters are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no parameter is changed.
- The parent, cycle and children rules depend on the final state, so they are checked once after all items are written: every item with a `parentId` must have a parent that exists and is ACTIVE (404, E10005), every updated item with a `parentId` must not be under itself (400, E10001), and every item that is DELETED or ARCHIVED must have no child parameter that is not DELETED (409, E10006). So one batch can delete a parent together with all its children, or activate a parent and move a child under it, in any item order. The message starts with the position of the item that fails.
- `id` must not be duplicated in the request, and `key` must not be duplicated among the items that are not DELETED (400, E10001). The key of a DELETED item is not compared.
- Swapping the keys of two parameters in one request is rejected with 409 (E10003) at the first item, because that key is still held by the other parameter when the item is checked. Change them in two requests.
- An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001).
- Governing decisions: owner-confirmed API review Q2, Q4, Q10 and Q13 (JWT payload of 2026-11-13).
- Permission: the same as the single upsert, only a platform administrator can call this API: the verified JWT `roles` claim (an array of role names, an empty array is valid) must contain the exact case-sensitive role `PLATFORM_ADMIN`, otherwise 403 (E10009). The check is made once for the request, after the existence checks of all items and before the duplicate, in-use and other conflict checks, so the 403 message has no item position. Never query `author.m_role` or `author.t_user_role`: a change of the role assignments does not change a token that was already issued.
- The transaction locks the caller user first and checks the current credential, a missing user or credential is 401 (E10002). The order of the checks and the locks is in the sequence diagram.
- Order of checks: validate the whole request (400, in item order) -> existence of every item with an id (404) -> permission (403) -> per item in the request order: effective period (400), duplicate key (409), write -> final state: parent (404), cycle (400), children (409), in one transaction.
- The response is HTTP 200 for every successful batch, including a batch that deletes.

---

## Request Parameters

### Header Parameters

|     | Parameter Name | Data Type | M/O       | Description                  | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request  | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp            | 2026-11-18T09:00:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id               | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type                               | M/O       | Description                                                   | Example |
| --- | -------------- | --------------------------------------- | --------- | ------------------------------------------------------------- | ------- |
| 1   | parameters     | [Array of Parameter](#parameter-object) | MANDATORY | Parameters to insert, update or delete (min 1, max 100 items) |         |

#### Parameter Object

|     | Parameter Name | Data Type         | M/O       | Description                                                                                                                                                                                                                                                                                  | Example                              |
| --- | -------------- | ----------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID      | OPTIONAL  | Parameter Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED parameter counts as not found, Must not be duplicated in the request                                                                                                                  | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 2   | parentId       | String: UUID      | OPTIONAL  | Parent Parameter Id, The parent must exist and be ACTIVE after all items are applied, Must not be the parameter itself or one of its descendants, Omitted or null makes the parameter a root                                                                                                 | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | key            | String            | MANDATORY | Parameter Key (1 to 128 characters, no leading or trailing space), Unique among parameters that are not DELETED, Exact comparison, Must not be duplicated among the items that are not DELETED                                                                                               | TH-10                                |
| 4   | value          | Object            | MANDATORY | Localized value, A JSON object of lowercase ISO 639-1 language codes and non-empty strings (max 512 characters each), At least one language                                                                                                                                                  |                                      |
| 5   | title          | Object            | OPTIONAL  | Localized title, Same format as value, Omitted or null is written as null                                                                                                                                                                                                                    |                                      |
| 6   | display        | Object            | OPTIONAL  | Localized display text, Same format as value, Omitted or null is written as null                                                                                                                                                                                                             |                                      |
| 7   | metadata       | Object            | OPTIONAL  | Any JSON object (max 4096 bytes when serialized), Omitted or null is written as null                                                                                                                                                                                                         |                                      |
| 8   | effectiveAt    | String: TIMESTAMP | OPTIONAL  | Start of the effective period (UTC), Defaults to the current time on insert, Keeps the stored value on update when omitted                                                                                                                                                                   | 2026-11-18T00:00:00.000Z             |
| 9   | expiredAt      | String: TIMESTAMP | OPTIONAL  | End of the effective period (UTC), Must be later than effectiveAt, Omitted or null means the parameter never expires                                                                                                                                                                         | 2030-12-31T23:59:59.000Z             |
| 10  | rowStatus      | String            | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the parameter has no child parameter that is not DELETED after all items are applied | ACTIVE                               |

#### Example Body Parameters

```JSON
{
    "parameters": [
        {
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-10",
            "value": {
                "en": "Bangkok",
                "th": "กรุงเทพมหานคร"
            },
            "rowStatus": "ACTIVE"
        },
        {
            "id": "3c4d5e6f-7a8b-4c9d-8e0f-2a3b4c5d6e7f",
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-11",
            "value": {
                "en": "Samut Prakan",
                "th": "สมุทรปราการ"
            },
            "rowStatus": "ACTIVE"
        },
        {
            "id": "4d5e6f7a-8b9c-4d0e-9f1a-3b4c5d6e7f8a",
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-99",
            "value": {
                "en": "Old Province"
            },
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/parameter/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-18T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "parameters": [
        {
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-10",
            "value": {
                "en": "Bangkok",
                "th": "กรุงเทพมหานคร"
            },
            "rowStatus": "ACTIVE"
        },
        {
            "id": "4d5e6f7a-8b9c-4d0e-9f1a-3b4c5d6e7f8a",
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-99",
            "value": {
                "en": "Old Province"
            },
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/parameter/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-18T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "parameters": [
        {
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-10",
            "value": {
                "en": "Bangkok",
                "th": "กรุงเทพมหานคร"
            },
            "rowStatus": "ACTIVE"
        },
        {
            "id": "4d5e6f7a-8b9c-4d0e-9f1a-3b4c5d6e7f8a",
            "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "key": "TH-99",
            "value": {
                "en": "Old Province"
            },
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field           | Description                                         | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | --------------- | --------------------------------------------------- | ------- |
| 1   | parameters     | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.parameters | Result of each parameter, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                         | Description                                               | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------------------------- | --------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.parameters[].index       | Index of the parameter in the request, Starting from 0    | 0                                    |
| 2   | parameterId    | String: UUID | MANDATORY | Sequence Diagram | data.parameters[].parameterId | Inserted, Updated, Deleted or Archived Parameter Id       | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.parameters[].action      | Action of the parameter (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Parameter Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-18T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "parameters": [
            {
                "index": 0,
                "parameterId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
                "action": "INSERT"
            },
            {
                "index": 1,
                "parameterId": "3c4d5e6f-7a8b-4c9d-8e0f-2a3b4c5d6e7f",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "parameterId": "4d5e6f7a-8b9c-4d0e-9f1a-3b4c5d6e7f8a",
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
        "bizMessage": "parameters[0]: Key and Value are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:00.123Z",
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
        "bizMessage": "Parameters must contain 1 to 100 items.",
        "requestId": "req-401a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:10.123Z",
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
        "bizMessage": "parameters[2]: Id is duplicated with parameters[1].",
        "requestId": "req-402a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:20.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Duplicate Key

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "parameters[2]: Key is duplicated with parameters[0].",
        "requestId": "req-403a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:30.123Z",
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
        "bizMessage": "parameters[0]: Row status must not be DELETED when inserting a parameter.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Cycle

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "parameters[1]: Parent must not be the parameter itself or one of its descendants.",
        "requestId": "req-412a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:50.123Z",
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
        "timestamp": "2026-11-18T09:02:00.123Z",
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
        "bizMessage": "parameters[1]: Parameter not found.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:02:10.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Parent

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "parameters[0]: Parent parameter not found.",
        "requestId": "req-421a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:02:20.123Z",
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
        "bizMessage": "You do not have permission to manage parameters.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:02:30.123Z",
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
        "bizMessage": "parameters[0]: Parameter key already exists.",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:02:40.123Z",
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
        "bizMessage": "parameters[2]: Parameter has child parameters.",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:02:50.123Z",
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
        "timestamp": "2026-11-18T09:03:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:03:10.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. The caller identity (`callerUserId`, the `sub` of the verified JWT) is distinct from the parameters; the fresh UTC time is bound. The caller user is locked first, then the current credential is checked, then the parameters of the items with an id are locked one by one in ascending id order (`FOR UPDATE`) before the permission decision, the conflict checks and the writes. The parents are read with `FOR SHARE` in the final-state checks after all items are written. `effectiveAt` in the SQL is the item value, or the current time on insert, or the stored `effective_at` on update.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the caller user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.callerUserId>'
FOR UPDATE
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check current credential and user

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
JOIN authen.m_user u ON u.id = at.user_id
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.callerUserId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND u.row_status = 'ACTIVE'
```

### Table: [public.m_parameter](../../../schema/public/m_parameter.md)

#### QUERY - Check existing parameter

```SQL
SELECT
    p.id as parameter_id,
    p.effective_at
FROM public.m_parameter p
WHERE p.id = '<sequence.parameters.id>'
AND p.row_status <> 'DELETED' -- the id of a DELETED parameter counts as not found
FOR UPDATE
```

#### QUERY - Check duplicate key

```SQL
SELECT
    p.id as parameter_id
FROM public.m_parameter p
WHERE p.key = '<sequence.parameters.key>'
AND p.row_status <> 'DELETED'
AND p.id <> '<sequence.parameters.id>' -- only when id is specified
```

#### INSERT - Create parameter

```SQL
INSERT INTO public.m_parameter (
    created_by,
    row_status,
    effective_at,
    expired_at,
    parent_id,
    key,
    value,
    title,
    display,
    metadata
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.parameters.rowStatus>',
    '<sequence.parameters.effectiveAt>',
    '<sequence.parameters.expiredAt>',
    '<sequence.parameters.parentId>',
    '<sequence.parameters.key>',
    '<sequence.parameters.value>',
    '<sequence.parameters.title>',
    '<sequence.parameters.display>',
    '<sequence.parameters.metadata>'
)
RETURNING id as parameter_id
```

#### UPDATE - Update or delete parameter

```SQL
UPDATE public.m_parameter
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.parameters.rowStatus>',
    effective_at = '<sequence.parameters.effectiveAt>',
    expired_at = '<sequence.parameters.expiredAt>',
    parent_id = '<sequence.parameters.parentId>',
    key = '<sequence.parameters.key>',
    value = '<sequence.parameters.value>',
    title = '<sequence.parameters.title>',
    display = '<sequence.parameters.display>',
    metadata = '<sequence.parameters.metadata>'
WHERE id = '<sequence.parameters.id>'
RETURNING id as parameter_id
```

#### QUERY - Check parent parameter

```SQL
SELECT
    pp.id as parent_id
FROM public.m_parameter pp
WHERE pp.id = '<sequence.parameters.parentId>'
AND pp.row_status = 'ACTIVE'
FOR SHARE
```

#### QUERY - Check parent cycle

```SQL
WITH RECURSIVE ancestor AS (
    SELECT
        a.id,
        a.parent_id
    FROM public.m_parameter a
    WHERE a.id = '<sequence.parameters.parentId>'
    UNION
    SELECT
        n.id,
        n.parent_id
    FROM public.m_parameter n
    JOIN ancestor c ON n.id = c.parent_id
)
SELECT
    an.id as ancestor_id
FROM ancestor an
WHERE an.id = '<sequence.parameters.id>' -- only when id and parentId are specified
```

#### QUERY - Check child parameter

```SQL
SELECT
    cp.id as child_id
FROM public.m_parameter cp
WHERE cp.parent_id = '<sequence.parameters.id>' -- only when rowStatus is DELETED or ARCHIVED
AND cp.row_status <> 'DELETED'
```
