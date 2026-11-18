---
name: "Upsert Parameter API"
description: "Insert, update, delete or archive one parameter (reference data such as a country, province, district, subdistrict or postal code), only for a platform administrator authorized from the verified JWT roles claim after the caller lock and the current credential check. Read it when you implement, review or test POST v1/parameter/upsert."
status: approved
approved_by: Josh (SA Lead, delegated by Ittikorn 2026-11-17)
approved_at: 2026-11-18T08:23:39+07:00
---

# [POST]: v1/parameter/upsert

| Title       | Description                                                                                                                                                                                                                                                                                                                                               |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Parameter API                                                                                                                                                                                                                                                                                                                                      |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                      |
| Endpoint    | v{version}/parameter/upsert                                                                                                                                                                                                                                                                                                                               |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                         |
| Description | Insert, update or delete a parameter (a key with localized value, title and display under an optional parent parameter), Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200), only a platform administrator can call it |

## Domain

| Environment    | Url                                 |
| -------------- | ----------------------------------- |
| DEV            | https://www.domain.com/api-dev      |
| QA             | https://www.domain.com/api-qa       |
| UAT            | https://www.domain.com/api-uat      |
| PRE-PRODUCTION | https://www.domain.com/api-pre-prod |
| PRODUCTION     | https://www.domain.com/api          |

- A parameter is one row of reference data in a hierarchy through `parentId`, for example country > province > district > subdistrict > postal code. A parameter without `parentId` is a root.
- The rules on the parent, the cycle, the replaced fields, the localized texts and the key were decided by Josh, SA Lead, delegated by the owner, 2026-11-18 (Q1 to Q5 of the parameter API review).
- Every request replaces the whole parameter: `key` and `value` are required in every request, including a delete and an archive. `parentId`, `title`, `display`, `metadata` and `expiredAt` are optional and an omitted value is written as null, so an update that omits `parentId` makes the parameter a root and an update that omits `expiredAt` removes the expiry. `effectiveAt` is optional: an omitted value is the current time on insert and keeps the stored value on update.
- `key` has 1 to 128 characters and no leading or trailing space. It is unique among parameters that are not DELETED. The comparison is exact (upper and lower case are different keys) and a key held by an INACTIVE, LOCKED or ARCHIVED parameter is still taken (409, E10003). The key of a DELETED parameter can be used again. The key can change on update, because other tables refer to a parameter by its id. When two requests write the same key at the same time, the unique index `uq_m_parameter_key` rejects the second write and it also answers 409 (E10003).
- `value`, `title` and `display` are localized texts: a JSON object with at least one key, every key is a lowercase ISO 639-1 language code (two letters, for example `en`, `th`) and every value is a non-empty string of at most 512 characters. No language is mandatory. `metadata` is any JSON object (not an array or a scalar) of at most 4 KB (4096 bytes) when serialized. Anything else is 400 (E10001).
- `expiredAt` must be later than `effectiveAt` (400, E10001). On an update without `effectiveAt` the stored `effective_at` is compared, after the existence check.
- The parent must exist and be ACTIVE on every write that has a `parentId`, also when the parent is not changed, otherwise 404 (E10005). Only the row status of the parent is checked, not its `effectiveAt` and `expiredAt`. The parent is read with `FOR SHARE`, so a delete or an archive of the parent that runs at the same time (which locks the parent with `FOR UPDATE` and then checks its children) waits for this request or makes it fail with 404.
- `parentId` must not be the parameter itself or one of its descendants (400, E10001), checked inside the transaction by walking up the ancestors of the new parent. An insert cannot make a cycle because the new parameter has no children.
- DELETED is final: a DELETED parameter is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the parameter again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a parameter.
- A parameter cannot be deleted or archived while it has a child parameter that is not DELETED, 409 (E10006). INACTIVE and LOCKED are allowed even when it has children, the children are not changed, but no write can use it as a parent while it is not ACTIVE.
- Governing decisions: owner-confirmed API review Q2, Q4, Q10 and Q13 (JWT payload of 2026-11-13).
- Permission: only a platform administrator can call this API: the verified JWT `roles` claim (an array of role names, an empty array is valid) must contain the exact case-sensitive role `PLATFORM_ADMIN`, otherwise 403 (E10009), after the existence checks and before the cycle, duplicate, in-use and other conflict checks and before anything is written. Never query `author.m_role` or `author.t_user_role`: a change of the role assignments does not change a token that was already issued. Reading is public (parameter inquiry).
- The transaction locks the caller user first and checks the current credential, a missing user or credential is 401 (E10002). The order of the checks and the locks is in the sequence diagram.
- Order of checks: validate the request (400) -> existence of the parameter and of the parent (404) -> permission (403) -> effective window and cycle (400) -> duplicate key and children (409) -> write, in one transaction.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

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

|     | Parameter Name | Data Type         | M/O       | Description                                                                                                                                                                                                                                                      | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID      | OPTIONAL  | Parameter Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED parameter counts as not found                                                                                                                             | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |
| 2   | parentId       | String: UUID      | OPTIONAL  | Parent Parameter Id, The parent must exist and be ACTIVE, Must not be the parameter itself or one of its descendants, Omitted or null makes the parameter a root                                                                                                 | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | key            | String            | MANDATORY | Parameter Key (1 to 128 characters, no leading or trailing space), Unique among parameters that are not DELETED, Exact comparison                                                                                                                                | TH-10                                |
| 4   | value          | Object            | MANDATORY | Localized value, A JSON object of lowercase ISO 639-1 language codes and non-empty strings (max 512 characters each), At least one language                                                                                                                      |                                      |
| 5   | title          | Object            | OPTIONAL  | Localized title, Same format as value, Omitted or null is written as null                                                                                                                                                                                        |                                      |
| 6   | display        | Object            | OPTIONAL  | Localized display text, Same format as value, Omitted or null is written as null                                                                                                                                                                                 |                                      |
| 7   | metadata       | Object            | OPTIONAL  | Any JSON object (max 4096 bytes when serialized), Omitted or null is written as null                                                                                                                                                                             |                                      |
| 8   | effectiveAt    | String: TIMESTAMP | OPTIONAL  | Start of the effective period (UTC), Defaults to the current time on insert, Keeps the stored value on update when omitted                                                                                                                                       | 2026-11-18T00:00:00.000Z             |
| 9   | expiredAt      | String: TIMESTAMP | OPTIONAL  | End of the effective period (UTC), Must be later than effectiveAt, Omitted or null means the parameter never expires                                                                                                                                             | 2030-12-31T23:59:59.000Z             |
| 10  | rowStatus      | String            | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete or archive is allowed only when the parameter has no child parameter that is not DELETED | ACTIVE                               |

#### Example Body Parameters

##### Insert

```JSON
{
    "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "key": "TH-10",
    "value": {
        "en": "Bangkok",
        "th": "กรุงเทพมหานคร"
    },
    "title": {
        "en": "Province",
        "th": "จังหวัด"
    },
    "display": {
        "en": "Bangkok",
        "th": "กรุงเทพฯ"
    },
    "metadata": {
        "isoCode": "TH-10"
    },
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "key": "TH-10",
    "value": {
        "en": "Bangkok Metropolis",
        "th": "กรุงเทพมหานคร"
    },
    "title": {
        "en": "Province",
        "th": "จังหวัด"
    },
    "display": {
        "en": "Bangkok",
        "th": "กรุงเทพฯ"
    },
    "metadata": {
        "isoCode": "TH-10"
    },
    "effectiveAt": "2026-11-18T00:00:00.000Z",
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
    "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "key": "TH-10",
    "value": {
        "en": "Bangkok Metropolis",
        "th": "กรุงเทพมหานคร"
    },
    "rowStatus": "DELETED"
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/parameter/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-18T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "key": "TH-10",
    "value": {
        "en": "Bangkok",
        "th": "กรุงเทพมหานคร"
    },
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/parameter/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-18T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "parentId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
    "key": "TH-10",
    "value": {
        "en": "Bangkok",
        "th": "กรุงเทพมหานคร"
    },
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field            | Description                                                                      | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ---------------- | -------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | parameterId    | String: UUID | MANDATORY | Sequence Diagram | data.parameterId | Inserted, Updated or Archived Parameter Id, Not returned when deleted (HTTP 204) | 2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Parameter Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-18T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "parameterId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e"
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
        "bizMessage": "Update Parameter Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-18T09:05:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "parameterId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e"
    }
}
```

#### Success - Delete

HTTP 204, no response body

```HTTP
HTTP/1.1 204 No Content
```

#### Success - Archive

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Archive Parameter Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-18T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "parameterId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e"
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
        "bizMessage": "Key and Value are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Localized Text

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Value must be an object of lowercase language codes and non-empty texts.",
        "requestId": "req-401a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:10.123Z",
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
        "bizMessage": "Row status must not be DELETED when inserting a parameter.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:20.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Effective Period

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Expired at must be later than effective at.",
        "requestId": "req-411a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:30.123Z",
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
        "bizMessage": "Parent must not be the parameter itself or one of its descendants.",
        "requestId": "req-412a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-18T09:01:40.123Z",
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
        "bizMessage": "Parameter not found.",
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
        "bizMessage": "Parent parameter not found.",
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
        "bizMessage": "Parameter key already exists.",
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
        "bizMessage": "Parameter has child parameters.",
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

---

## Database Relations

One READ COMMITTED transaction. The caller identity (`callerUserId`, the `sub` of the verified JWT) is distinct from the parameter; the fresh UTC time is bound. The caller user is locked first, then the current credential is checked, then the parameter is locked (`FOR UPDATE`) and the parent is read with `FOR SHARE` before the permission decision, the conflict checks and the write. `effectiveAt` in the SQL is the request value, or the current time on insert, or the stored `effective_at` on update.

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
WHERE p.id = '<sequence.id>'
AND p.row_status <> 'DELETED' -- the id of a DELETED parameter counts as not found
FOR UPDATE
```

#### QUERY - Check parent parameter

```SQL
SELECT
    pp.id as parent_id
FROM public.m_parameter pp
WHERE pp.id = '<sequence.parentId>'
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
    WHERE a.id = '<sequence.parentId>'
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
WHERE an.id = '<sequence.id>' -- only when id and parentId are specified
```

#### QUERY - Check duplicate key

```SQL
SELECT
    p.id as parameter_id
FROM public.m_parameter p
WHERE p.key = '<sequence.key>'
AND p.row_status <> 'DELETED'
AND p.id <> '<sequence.id>' -- only when id is specified
```

#### QUERY - Check child parameter

```SQL
SELECT
    cp.id as child_id
FROM public.m_parameter cp
WHERE cp.parent_id = '<sequence.id>' -- only when rowStatus is DELETED or ARCHIVED
AND cp.row_status <> 'DELETED'
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
    '<sequence.rowStatus>',
    '<sequence.effectiveAt>',
    '<sequence.expiredAt>',
    '<sequence.parentId>',
    '<sequence.key>',
    '<sequence.value>',
    '<sequence.title>',
    '<sequence.display>',
    '<sequence.metadata>'
)
RETURNING id as parameter_id
```

#### UPDATE - Update or delete parameter

```SQL
UPDATE public.m_parameter
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = NOW() AT TIME ZONE 'UTC',
    row_status = '<sequence.rowStatus>',
    effective_at = '<sequence.effectiveAt>',
    expired_at = '<sequence.expiredAt>',
    parent_id = '<sequence.parentId>',
    key = '<sequence.key>',
    value = '<sequence.value>',
    title = '<sequence.title>',
    display = '<sequence.display>',
    metadata = '<sequence.metadata>'
WHERE id = '<sequence.id>'
RETURNING id as parameter_id
```
