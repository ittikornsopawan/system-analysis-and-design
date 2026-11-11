---
name: Role Batch Upsert API Specification
description: Defines whole-request validation, verified JWT authorization, sorted target locks, ordered atomic role mutations and indexed result mapping.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/role/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Role Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Endpoint    | v{version}/author/role/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Description | Insert, update or delete multiple roles at the same time, only a platform administrator can call it, Each role is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All roles are processed in one transaction in the request order, If any role fails then no role is changed |

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

|     | Parameter Name | Data Type                     | M/O       | Description                                              | Example |
| --- | -------------- | ----------------------------- | --------- | -------------------------------------------------------- | ------- |
| 1   | roles          | [Array of Role](#role-object) | MANDATORY | Roles to insert, update or delete (min 1, max 100 items) |         |

#### Role Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                             | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Role Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED role counts as not found, Must not be duplicated in the request                       | b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e |
| 2   | name           | String       | MANDATORY | Role Name, Role code (max 64 characters): capital letters, digits and `_`, starting with a letter, Unique among roles that are not DELETED, The role `PLATFORM_ADMIN` cannot be changed | CATALOG_MANAGER                      |
| 3   | description    | String       | MANDATORY | Role Description (max 256 characters)                                                                                                                                                   | Manages the product catalogue        |
| 4   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting                         | ACTIVE                               |

### Role Rules (same as the single upsert, applied per role)

- Every role follows the rules of [the single upsert](../01-upsert-role/spec.md#role-rules): name is the role code: capital letters, DELETED is final, delete and archive are rejected while a user (`author.t_user_role`) or a permission (`author.t_role_permission`) that is not DELETED still uses it.
- The roles are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no role is changed. `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001). The response is HTTP 200 for every successful batch, including a batch that deletes. The 403 message has no item position (the permission is the caller's, not the item's).
- **`PLATFORM_ADMIN` is the system role.** It cannot be renamed, changed, deleted, archived, locked or set INACTIVE through this API: any request that names it by `id` is rejected with 409 (E10006) `System role cannot be changed.` Giving another role the name `PLATFORM_ADMIN` is a duplicate name (409, E10003). The role is created by the seed, see `e-commerce/db/seed/author.seed.sql`.
- Permission: only a platform administrator from the verified JWT roles claim can call this API; require exact case-sensitive PLATFORM_ADMIN. Valid non-admin claims return one 403 E10009 after all target existence checks and before any conflict or write, with no item position. Never reload live caller grants from author.t_user_role/author.m_role. Approved by the product owner (Q2/Q4/Q10/Q13, 2026-11-07), superseding the earlier live-assignment guard.

### Batch Execution and Credential Rules

- Governing behavior: [owner-confirmed API review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q2/Q4/Q7/Q10/Q13/Q15, and the global whole-batch 400 -> 404 -> 403 -> 409/write convention. This detailed revision remains in-review; no backend/schema implementation is included.
- Validate the whole request before SQL: exactly one JSON object with only roles, no query keys, correct JSON content type and mandatory UTC timestamp; roles is an array of 1..100 non-null objects with only id/name/description/rowStatus and no repeated JSON keys. Process item validation in input order; required name/description are non-null nonblank strings (max 64/256), name matches ^[A-Z][A-Z0-9_]{0,63}$, and values are not trimmed/case-normalized. id is optional only by omission; supplied id must be a non-null UUID. rowStatus defaults to ACTIVE only when omitted, otherwise ACTIVE/INACTIVE/DELETED/LOCKED/ARCHIVED; insert-DELETED is 400. Validate required fields even for delete/archive. Generate requestId if omitted.
- Compare parsed canonical UUIDs when rejecting duplicate ids (400), and reject exact duplicate names among non-DELETED input items (400); deleted input items do not reserve a proposed name. Input errors identify roles[i] where item-specific; count/envelope/header errors are request-level. No partial processing before validation is complete.
- Verify JWT signature/issuer/audience/expiry/UUID sub and structured roles before BEGIN. roles must be an array (including []), each object has UUID roleId and non-empty string name, and roleIds are unique; missing/malformed claims are generic 401 E10002, not an empty-role fallback. Derive callerUserId only from verified sub, accessTokenHash as SHA-256 of the exact JWT, createdBy/updatedBy as caller UUID string. Never use request flags or a separate isPlatformAdmin claim to grant permission.
- Begin one READ COMMITTED transaction, lock caller user first, capture fresh server UTC now after the lock and recheck JWT exp, then read joined current credential/user. Require matching hash/caller, ACTIVE token/user and strict expired_at > now. Missing caller or revoked/inactive/expired/mismatched credentials is generic 401 before target reads. Logout/reset use the same user-first lock. Withdrawal of a grant alone does not invalidate an otherwise-current old JWT role snapshot; refresh loads current grants.
- Construct targetRoleIds as a typed UUID[] of all supplied ids (empty array for all inserts). Lock every matching non-DELETED target role in ascending id order with one SELECT FOR UPDATE, independent of request order. Map locked rows by id, then report the first missing/DELETED target in original request order as roles[i]: Role not found. (404 E10004), before caller permission or any conflict/write. The row-lock query rechecks lifecycle after waiting; no resurrection. Request-order mutation and sorted lock order are separate concerns. Existing roles cannot appear twice because validation rejects duplicate ids.
- After all target ids exist, authorize once using exact case-sensitive PLATFORM_ADMIN from verified JWT roles. Empty roles or other valid roles is one 403 E10009 with no item index; skip all conflict/write work. Do not query the caller's live assignments or reload claims. Target system-role and binding reads below protect business invariants only.
- Then iterate roles[i] in original input order. For an existing target check its stored PLATFORM_ADMIN name (409 E10006) before duplicate name. Check duplicate names with a null-safe optional target exclusion, across all non-DELETED statuses; omitted insert id binds typed SQL NULL. For an existing target requested DELETED/ARCHIVED, either non-DELETED user or permission binding is 409 E10006, including inactive/locked/archived bindings. INACTIVE/LOCKED leave bindings unchanged. Insert-ARCHIVED is INSERT and needs no binding check.
- Each item's conflict reads see preceding item writes in the same transaction. Deleting a role at index 0 can release its old name for an insert at index 1; reversing those items returns duplicate 409 at index 0 and applies neither. Renaming A to a name still held by B returns 409 even if a later item would release it; this API does not apply a final-state rename plan. Preserve the existing request-order rule. Every item-specific 404/409 message begins roles[i]; a unique-index collision uses the current writing item's index.
- Bind every SQL value. INSERT explicitly sets created_at from fresh server now and must return exactly one role_id; zero/malformed result is internal 500. UPDATE guards target id, non-DELETED status and stored name <> PLATFORM_ADMIN; zero returns roles[i]: Role not found. (404 E10004), no result or earlier mutation is committed. Exactly one returned update id must equal that input id. Preserve creation audit on update; never trust a client-generated inserted id or audit fields.
- Append exactly index/roleId/action per item, using RETURNING. index is its original zero-based position. action is INSERT when id omitted (including insert-ARCHIVED), otherwise DELETE for DELETED, ARCHIVE for ARCHIVED, UPDATE for ACTIVE/INACTIVE/LOCKED. All item outcomes, including DELETE, remain in data.roles. Require exactly one result per input item in the same order with no duplicate returned roleIds. Finish all mapping before one COMMIT after the loop, then HTTP 200 S10000 Batch Upsert Role Success; batch never sends per-item 201/204 or partial success.
- uq_m_role_name is the final concurrent duplicate guard. SQLSTATE 23505 from that constraint rolls back all items and returns 409 E10003 roles[i]: Role name already exists.; other SQL/result/mapping failures roll back and return generic 500 without bizCode. Timeout before COMMIT rolls back and returns 408 E90001. These request-level failures have no invented item position. No success or partial result escapes a failed transaction; no retry is promised after an unknown commit result.
- Shared lifecycle invariant: reference/assignment writers must lock and recheck the target role before creating/reopening a binding, with target users first and role ids ascending. Their matching migrations remain separate API PRs; this batch contract and its SQL fixtures do not certify unmigrated writers. A soft-deleted parent flag alone is not enforced by its foreign key.
- Execution order: validate all items (400) -> verify JWT (401) -> begin transaction (READ COMMITTED) -> caller lock -> fresh current credential gate (401) -> lock target ids ascending -> all target existence checks in request order (404) -> one claims permission (403, E10009) -> per-item stored system/duplicate/in-use conflicts (409) and guarded writes in input order -> complete indexed mapping -> COMMIT -> one 200. Every post-BEGIN error rolls back the whole batch.

#### Scenario correspondence with sequence.wsd

| Scenario                                                           | Branch/outcome                                  | Effects                          |
| ------------------------------------------------------------------ | ----------------------------------------------- | -------------------------------- |
| Invalid array/items/duplicate ids or names / invalid JWT claims    | 400 E10001 / 401 E10002 before SQL              | No writes                        |
| Missing caller, token revocation or expiry during caller-lock wait | 401 E10002 before target reads                  | Rollback                         |
| Later input target missing while an earlier item would conflict    | All target existence first, 404 E10004 roles[i] | No item writes                   |
| Valid current JWT without exact PLATFORM_ADMIN                     | Single 403 E10009, no position                  | No conflicts/writes              |
| Stored system role / duplicate name / any non-DELETED binding      | 409 E10006 / E10003 / E10006 roles[i]           | All earlier writes rolled back   |
| Delete then reuse the old name / reverse order                     | 200 DELETE+INSERT / 409 at earlier insert       | Request-order visibility, atomic |
| Mixed insert/update/archive/delete, including all-delete           | One 200 with ordered index/roleId/action        | One commit after all items       |
| Guarded UPDATE returns zero / wrong result id                      | 404 E10004 roles[i] / generic 500               | Whole batch rollback             |
| Concurrent same-name insert / timeout / unexpected failure         | Indexed 409 E10003 / 408 E90001 / generic 500   | No partial success               |
| Opposite input target orders                                       | Lock ids ascending, mutate input order          | Shared lock protocol             |

#### Example Body Parameters

```JSON
{
    "roles": [
        {
            "name": "CATALOG_MANAGER",
            "description": "Manages the product catalogue",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "name": "SHOP_SUPPORT",
            "description": "Helps shops with their questions",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e7f",
            "name": "AUDITOR",
            "description": "Reads the platform data",
            "rowStatus": "DELETED"
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/role/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "roles": [
        {
            "name": "CATALOG_MANAGER",
            "description": "Manages the product catalogue",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "name": "SHOP_SUPPORT",
            "description": "Helps shops with their questions",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e7f",
            "name": "AUDITOR",
            "description": "Reads the platform data",
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/role/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "roles": [
        {
            "name": "CATALOG_MANAGER",
            "description": "Manages the product catalogue",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "name": "SHOP_SUPPORT",
            "description": "Helps shops with their questions",
            "rowStatus": "ACTIVE"
        },
        {
            "id": "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e7f",
            "name": "AUDITOR",
            "description": "Reads the platform data",
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-06T09:00:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                         | M/O       | Source           | Field      | Description                                    | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------- | ---------------------------------------------- | ------- |
| 1   | roles          | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.roles | Result of each role, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field               | Description                                          | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------- | ---------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.roles[].index  | Index of the role in the request, Starting from 0    | 0                                    |
| 2   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.roles[].roleId | Inserted, Updated, Deleted or Archived Role Id       | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.roles[].action | Action of the role (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Role Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "roles": [
            {
                "index": 0,
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "action": "INSERT"
            },
            {
                "index": 1,
                "roleId": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "roleId": "c3d4e5f6-a7b8-4c9d-8e1f-2a3b4c5d6e7f",
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
        "bizMessage": "roles[0]: Name and Description are required fields.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:40:40.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Bad Request Name

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "roles[1]: Role name must be capital letters, digits and _, starting with a letter, at most 64 characters.",
        "requestId": "req-410a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:41:47.123Z",
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
        "bizMessage": "roles[1]: Row status must not be DELETED when inserting a role.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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
        "bizMessage": "Roles must contain 1 to 100 items.",
        "requestId": "req-430a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:43:01.123Z",
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
        "bizMessage": "roles[2]: Id is duplicated with roles[1].",
        "requestId": "req-440a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:44:08.123Z",
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
        "bizMessage": "roles[2]: Name is duplicated with roles[0].",
        "requestId": "req-450a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:45:15.123Z",
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

#### Fail - Forbidden

```JSON
{
    "status": {
        "code": 403,
        "message": "Forbidden",
        "bizCode": "E10009",
        "bizMessage": "You do not have permission to manage roles.",
        "requestId": "req-460a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:46:22.123Z",
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
        "bizMessage": "roles[1]: Role not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
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
        "bizMessage": "roles[0]: Role name already exists.",
        "requestId": "req-490a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:49:43.123Z",
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
        "bizMessage": "roles[2]: Role is assigned to users or has permissions.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict System Role

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "roles[1]: System role cannot be changed.",
        "requestId": "req-510a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:01:57.123Z",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-role-batch-review",
        "timestamp": "2026-11-08T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

All SQL executes within one READ COMMITTED transaction. Caller identity is distinct from target role ids. Optional per-item id uses typed SQL NULL; targetRoleIds is a bound typed UUID[] (empty allowed). Locks precede item writes; only the final commit persists any item.

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

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Lock existing roles

```SQL
SELECT
    r.id as role_id,
    r.name
FROM author.m_role r
WHERE r.id = ANY ('<sequence.targetRoleIds>'::UUID[])
AND r.row_status <> 'DELETED' -- the id of a DELETED role counts as not found
ORDER BY r.id
FOR UPDATE
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check system role

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.id = '<sequence.roles.id>'
AND r.name = 'PLATFORM_ADMIN' -- the request is rejected (409) when a row is found, only when id is specified
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### QUERY - Check duplicate name

```SQL
SELECT
    r.id as role_id
FROM author.m_role r
WHERE r.name = '<sequence.roles.name>'
AND r.row_status <> 'DELETED'
AND ('<sequence.roles.id>' IS NULL OR r.id <> '<sequence.roles.id>') -- omitted insert id is typed SQL NULL
```

### Table: [author.t_user_role](../../../schema/author/t_user_role.md)

#### QUERY - Check user in use

```SQL
SELECT
    ur.id as user_role_id
FROM author.t_user_role ur
WHERE ur.role_id = '<sequence.roles.id>' -- only when rowStatus is DELETED or ARCHIVED
AND ur.row_status <> 'DELETED'
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.role_id = '<sequence.roles.id>' -- only when rowStatus is DELETED or ARCHIVED
AND rp.row_status <> 'DELETED'
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### INSERT - Create role

```SQL
INSERT INTO author.m_role (
    created_by,
    created_at,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.roles.rowStatus>',
    '<sequence.roles.name>',
    '<sequence.roles.description>'
)
RETURNING id as role_id
```

### Table: [author.m_role](../../../schema/author/m_role.md)

#### UPDATE - Update or delete role

```SQL
UPDATE author.m_role
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.roles.rowStatus>',
    name = '<sequence.roles.name>',
    description = '<sequence.roles.description>'
WHERE id = '<sequence.roles.id>'
AND row_status <> 'DELETED'
AND name <> 'PLATFORM_ADMIN'
RETURNING id as role_id
```
