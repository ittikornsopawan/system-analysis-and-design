---
name: Permission Upsert and Scope Link API Specification
description: Defines JWT administration, current credentials, atomic parent and scope-link writes, final scoping invariants and closed-scope cleanup.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/permission/upsert

| Title       | Description                                                                                                                                                                                                                                                             |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Permission API                                                                                                                                                                                                                                                   |
| Method      | POST                                                                                                                                                                                                                                                                    |
| Endpoint    | v{version}/author/permission/upsert                                                                                                                                                                                                                                     |
| Version     | 1                                                                                                                                                                                                                                                                       |
| Description | Insert, update or delete a permission, only a platform administrator can call it, Insert when id is not specified, Update when id is specified, Delete when rowStatus is DELETED (HTTP 204 No Content, no response body), Archive when rowStatus is ARCHIVED (HTTP 200) |

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

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                                                                                                                      | Example                              |
| --- | -------------- | ------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED permission counts as not found                                                                                                                                           | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 2   | name           | String                          | MANDATORY | Permission Name, Permission code (max 64 characters): lower-case letters, digits, `_` and `.`, at least two parts, Unique among permissions that are not DELETED                                                                                                                 | report.read                          |
| 3   | description    | String                          | MANDATORY | Permission Description (max 256 characters)                                                                                                                                                                                                                                      | Reads the platform reports           |
| 4   | scopes         | [Array of Scope](#scope-object) | OPTIONAL  | Scopes of the permission, Each item is inserted when `id` is not specified, updated when `id` is specified, deleted when `rowStatus` is DELETED, Scopes that are not listed are kept                                                                                             |                                      |
| 5   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete/archive requires no role/user usage; Delete also requires zero final non-DELETED scope definitions (Q24) | ACTIVE                               |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                            | Example                              |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Permission Scope Id, Insert when not specified, Update or Delete when specified, Must belong to this permission and must not be duplicated                                                                             | 3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f |
| 2   | scopeId        | String: UUID | MANDATORY | Scope Id, ACTIVE master required for an ACTIVE link (404 E10005), Existing DELETED-link requests may reference a closed master (Q23), Immutable when id is specified, No duplicate scope among non-DELETED input items | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (not allowed when inserting), A scope that a role or user still uses cannot be deleted                                                           | ACTIVE                               |

### Permission Rules

- `name` is unique among permissions that are not DELETED. The comparison is exact and a value held by an INACTIVE, LOCKED or ARCHIVED permission is still taken (409, E10003). The value of a DELETED permission can be used again.
- `name` is the permission code: lower-case letters, digits, `_` and `.`, at least two parts separated by `.`, for example `catalog.manage` (max 64 characters) (400, E10001). Every field that is not optional is required in every request, including a delete and an archive.
- DELETED is final: a DELETED permission is never reopened and its `id` counts as not found (404, E10004). INACTIVE, LOCKED and ARCHIVED are reversible: an update with `rowStatus` ACTIVE opens the permission again. `rowStatus` DELETED is rejected with 400 (E10001) when the request inserts a permission. A permission that is not ACTIVE is excluded from newly resolved login/refresh claims; an existing token keeps its previous claims until expiry (Q4/Q7).
- A permission cannot be deleted or archived while a role (`author.t_role_permission`) or a user (`author.t_user_permission`) that is not DELETED still holds it (409, E10006). INACTIVE and LOCKED are allowed, the rows that use it are not changed.
- `scopes` lists the scopes the permission can have (`author.t_permission_scope`). An item without `id` is added, with `id` is updated, with `rowStatus` DELETED is removed. Scopes that are not listed are kept. Adding or retaining an ACTIVE link requires an ACTIVE scope master (404 E10005); removing an existing link may reference a closed master under owner Q23. A scope cannot be deleted from the permission while a role (`author.t_role_permission_scope`) or a user (`author.t_user_permission`) still uses it (409, E10006). A permission without scopes has no scope dimension.
- Permission: only a platform administrator from verified JWT roles can call this API, with exact case-sensitive PLATFORM_ADMIN. Valid non-admin claims give 403 E10009 after parent existence and before scope/conflict work; do not authorize from live assignment queries or request flags. Approved by the product owner (Q2/Q4/Q10/Q13); this supersedes the prior live-grant guard.
- Execution order: validate the request (400) -> verify JWT (401) -> begin transaction (READ COMMITTED) -> caller lock/fresh current credentials (401) -> locked parent existence check (404) -> permission (403, E10009) -> scope check (404, E10005 for ACTIVE links), owned scope-link existence (404 E10004) and immutable scopeId (400) -> before-definition count -> duplicate check (409, E10003) -> parent/link in-use checks (409 E10006) -> guarded parent and child writes -> final definition count/Q24 deletion guard/Q22 grant guard (409 E10006) -> map -> COMMIT -> response. Every post-BEGIN error rolls back the whole request.
- HTTP status of the single upsert: Insert 201 Created, Update 200 Ok, Delete 204 No Content (no response body), Archive 200 Ok.

### Credential, Scope and Transaction Rules

- Governing decisions: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), including Q22/Q23 approved by the product owner on 2026-11-08. Detailed revision remains in-review; no schema/backend implementation.
- Validate one JSON object with only id/name/description/scopes/rowStatus, no repeated keys or query fields, correct JSON content type and mandatory UTC timestamp. Generate requestId if omitted. Parent id, if supplied, is a non-null UUID; omitted means insert. Required name/description are non-null nonblank strings of at most 64/256 characters; name matches ^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$ without trimming/case-normalization. Parent status defaults to ACTIVE only when omitted, otherwise ACTIVE/INACTIVE/DELETED/LOCKED/ARCHIVED; insert-DELETED is 400.
- scopes omitted or [] means no link change; null is invalid. Every supplied item is an object with only id/scopeId/rowStatus: optional id is a non-null UUID when present, scopeId is a required UUID, and child status is ACTIVE or DELETED, default ACTIVE only when omitted. Reject child insert-DELETED, duplicate parsed child ids, and duplicate scopeIds among non-DELETED input items with 400 before SQL. Required fields remain required on every parent/child delete. No new array-size limit is introduced.
- Verify JWT signature/issuer/audience/expiry/UUID sub and structured roles before BEGIN. roles must be an array including [], every object has UUID roleId/non-empty name, and roleIds are unique; malformed/missing roles is generic 401 E10002, never an empty-role fallback. Derive callerUserId from verified sub and accessTokenHash as SHA-256 of exact JWT. createdBy/updatedBy are the caller UUID string; use fresh server UTC now, never request audit values.
- Begin READ COMMITTED, lock caller user first, capture fresh server UTC now after that lock and recheck JWT exp, then require matching ACTIVE token/hash/caller, strict expired_at > now and ACTIVE user. Missing/revoked/inactive/expired credentials is generic 401 before parent lookup. Logout/reset share the caller lock. Authorization then uses only exact PLATFORM_ADMIN in verified JWT roles; [] or another valid role is 403. Grant changes alone do not invalidate a current old claim; refresh loads latest grants.
- Lock the non-DELETED parent when id is supplied; missing/DELETED is 404 and never reopened. permissionId is that verified existing id, or typed SQL NULL before insert; after parent RETURNING bind the actual returned id for every child write/final query. Keep callerUserId, optional request id and derived permissionId distinct. No client-generated inserted parent id or live caller-grant lookup.
- Lock order: caller user -> existing permission -> ACTIVE referenced scope masters ordered by id -> owned requested permission-scope rows ordered by id -> writes. activeScopeIds contains only scopeIds of requested ACTIVE links; permissionScopeIds contains supplied child ids. Both bind typed UUID[] (empty allowed). Before writing, validate each child in input order: ACTIVE child requires a returned ACTIVE master; DELETED child skips master-active validation (Q23), then a supplied child id must map to the owned non-DELETED row and its stored scopeId must equal the request (400 if changed). Missing/DELETED/other-parent child is 404 E10004. A child id cannot belong to a new parent; it likewise returns 404 after authorization. These checks never disclose another parent's child.
- Q23 owner answer: “ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว”. Deleting an owned existing definition works even when its master is INACTIVE/LOCKED/ARCHIVED/DELETED, subject to immutable scopeId and in-use/Q22 checks. ACTIVE link creation/retention still requires an ACTIVE master. No master status or grant row is changed by this API.
- Scopes that are not listed are kept. Preserve existing precheck semantics: all child reference/duplicate/in-use checks precede any parent/child write. Deleting then readding the same existing scopeId in this array still returns duplicate 409 because the old definition exists at precheck time; remove it in a prior request before adding a replacement. Omitted insert ids bind typed SQL NULL and duplicate exclusions are null-safe. Root name uniqueness spans every non-DELETED parent; scope-pair uniqueness spans every non-DELETED definition.
- Parent DELETED/ARCHIVED is 409 E10006 while any non-DELETED role/direct-user grant holds it, including inactive/locked/archived grants. A DELETED child is 409 E10006 while any non-DELETED role-scope/direct-user row references that definition, irrespective of current effective rights. Do not detach/rewrite grant history. Read these tables for business invariants, never to authorize the caller.
- Capture beforeDefinitionCount as every non-DELETED definition of this permission (not only ACTIVE or ACTIVE-master definitions). After all parent/child writes, query finalDefinitionCount again. Q22 triggers only when beforeDefinitionCount > 0 and finalDefinitionCount = 0. Then freshly query role/direct-user grant usage and reject any non-DELETED grant with 409 E10006 `Permission cannot become unscoped while assigned to roles or users.`; ROLLBACK restores all parent/link/audit writes. Owner answer: “ใช่ ปฏิเสธจนถอน grant เดิมครบ”. A request that merely updates an already-unscoped permission (before count 0) may keep valid unscoped grants. This is a final whole-request invariant, not a transient intermediate count.
- Q24 approved by the product owner on 2026-11-09: owner answer “ต้องถอน links ให้ครบก่อนลบ permission (แนะนำ)”. After all explicit child writes, reuse the final whole-request definition count: rowStatus = DELETED and finalDefinitionCount > 0 is 409 E10006 `Permission cannot be deleted while scope definitions remain.` with complete rollback of parent/child/audit writes. Count every non-DELETED definition, including INACTIVE/LOCKED/ARCHIVED and closed-master links. Omitted/empty scopes keep existing definitions and cannot bypass this rule. The caller may explicitly withdraw every remaining definition and delete the parent in the same request when existing ownership, immutable-id, grant and child-reference checks pass. Already-zero definitions, including DELETED-only history, permit parent deletion. ARCHIVED may retain definitions. Check Q24 after the final count, before Q22 and before any COMMIT/success; no implicit cascade and no deleted-parent cleanup exception are added.
- Shared grant/reference writers must lock and recheck their permission/definition parents before creating/reopening bindings; otherwise a soft-status invariant is not guaranteed by foreign keys. Their migrations remain separate APIs; this contract/SQL test does not certify unmigrated writers. Caller/target users must be locked in ascending id order in those writers before master/link rows.
- Parent/child INSERTs explicitly set created_at from server now and must return exactly one UUID; missing/malformed result is internal 500. Existing parent UPDATE guards id and non-DELETED; child UPDATE guards id, permissionId, immutable scopeId and non-DELETED status. A zero-row update is 404 E10004 with whole-request rollback; a returned existing id must match its requested id. Preserve creation audit on updates. Do not reopen DELETED rows.
- Archive and other reversible parent updates retain unlisted child definitions. Parent deletion requires zero final non-DELETED definitions under Q24; unlisted definitions therefore cause 409 E10006 instead of being stranded. Explicit child actions remain atomic and there is no implicit cascade. A new parent requested ARCHIVED is still an INSERT (201). Child ids are internal results, not added response fields.
- Map exactly data.permissionId from the parent's RETURNING id before COMMIT. Insert is 201 S10000 Insert Permission Success; existing DELETED is 204 with no body/status/data; existing ARCHIVED is 200 S10000 Archive Permission Success; other existing updates are 200 S10000 Update Permission Success. Every child action and final Q24/Q22 check completes before success; no partial response.
- SQLSTATE 23505 from uq_m_permission_name is 409 E10003 `Permission name already exists.`; from uq_t_permission_scope_permission_id_scope_id is 409 E10003 `Scope already exists in the permission.`. Both roll back the entire transaction, including earlier writes. Other SQL/result/mapping errors return generic 500 without bizCode after rollback; timeout before COMMIT is 408 E90001 after rollback. No retry is promised for an unknown commit result.

#### Scenario correspondence with sequence.wsd

| Scenario                                                                | Outcome                               | Effects                                                  |
| ----------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------- |
| Invalid parent/child/duplicate input or malformed JWT                   | 400 E10001 / 401 E10002 before SQL    | None                                                     |
| Missing caller, expiry during caller lock, invalid current token/user   | 401 E10002                            | Rollback before parent read                              |
| Missing/DELETED parent / valid non-admin                                | 404 E10004 / 403 E10009               | No scope/conflict work                                   |
| ACTIVE link master missing/closed / child missing or other-parent       | 404 E10005 / 404 E10004               | Whole request rejected                                   |
| Existing child scopeId changed                                          | 400 E10001                            | No writes                                                |
| Closed master, deleting unused existing link                            | Allowed by Q23                        | Still checks owner/in-use/Q22                            |
| Parent/child duplicate or in-use                                        | 409 E10003 / E10006                   | No partial write                                         |
| Last definition removed while a role/direct grant survives              | 409 E10006 (Q22)                      | Rollback parent, child and audit changes                 |
| Last definition removed without grants / already-unscoped update        | Normal success                        | Final count guard preserves intended dimension           |
| Parent DELETED with any final non-DELETED definition                    | 409 E10006 (Q24)                      | Rollback parent, all explicit child actions and audit    |
| Complete same-request withdrawal then parent DELETED / zero definitions | 204, no body                          | Retain deleted link history, no stranded live definition |
| Parent insert/update/archive/delete with supplied child actions         | 201 / 200 / 200 / 204                 | One transaction, commit only after final guard           |
| Guarded update returns zero / malformed result                          | 404 E10004 / generic 500              | All writes rollback                                      |
| Concurrent unique collision / timeout / unexpected error                | 409 E10003 / 408 E90001 / generic 500 | Whole request rollback                                   |

#### Example Body Parameters

##### Insert

```JSON
{
    "name": "report.read",
    "description": "Reads the platform reports",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
    "rowStatus": "ACTIVE"
}
```

##### Update

```JSON
{
    "id": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "name": "report.export",
    "description": "Reads the platform reports",
    "scopes": [
        {
            "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        },
        {
            "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
            "rowStatus": "ACTIVE"
        }
    ],
    "rowStatus": "ACTIVE"
}
```

##### Delete

```JSON
{
    "id": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
    "name": "report.export",
    "description": "Reads the platform reports",
    "scopes": [
        {
            "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "DELETED"
        },
        {
            "id": "4d5e6f7a-8b9c-4d0e-9f1a-2b3c4d5e6f70",
            "scopeId": "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e",
            "rowStatus": "DELETED"
        }
    ],
    "rowStatus": "DELETED"
}
```

The example withdraws every remaining non-DELETED definition. Any unlisted definition causes 409 E10006 and rolls back the entire request.

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/permission/upsert HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "name": "report.read",
    "description": "Reads the platform reports",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
    "rowStatus": "ACTIVE"
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/permission/upsert' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "name": "report.read",
    "description": "Reads the platform reports",
    "scopes": [
        {
            "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            "rowStatus": "ACTIVE"
        }
    ],
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

|     | Parameter Name | Data Type    | M/O       | Source           | Field             | Description                                                                       | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ----------------- | --------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | permissionId   | String: UUID | MANDATORY | Sequence Diagram | data.permissionId | Inserted, Updated or Archived Permission Id, Not returned when deleted (HTTP 204) | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |

### Example Response Parameters

#### Success - Insert

```JSON
{
    "status": {
        "code": 201,
        "message": "Created",
        "bizCode": "S10000",
        "bizMessage": "Insert Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
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
        "bizMessage": "Update Permission Success",
        "requestId": "req-5c3d9e1f-2a4b-4c6d-8e0f-1a2b3c4d5e6f",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
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
        "bizMessage": "Archive Permission Success",
        "requestId": "req-7e5f1a3b-4c6d-4e8f-8a2b-3c4d5e6f7a8b",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a"
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
        "bizMessage": "Name and Description are required fields.",
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
        "bizMessage": "Permission name must be lower-case letters, digits, _ and ., with at least two parts separated by a dot, at most 64 characters.",
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
        "bizMessage": "Row status must not be DELETED when inserting a permission.",
        "requestId": "req-420a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:42:54.123Z",
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
        "bizMessage": "You do not have permission to manage permissions.",
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
        "bizMessage": "Permission not found.",
        "requestId": "req-470a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:47:29.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Not Found Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizCode": "E10005",
        "bizMessage": "Scope not found.",
        "requestId": "req-480a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:48:36.123Z",
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
        "bizMessage": "Permission name already exists.",
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
        "bizMessage": "Permission is used by roles or users.",
        "requestId": "req-500a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:00:50.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Scope In Use

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Scope is used by roles or users.",
        "requestId": "req-520a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-06T09:02:04.123Z",
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

#### Fail - Bad Request Scope Changed

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizMessage": "Scope Id cannot be changed.",
        "requestId": "req-permission-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10001"
    }
}
```

#### Fail - Not Found Permission Scope

```JSON
{
    "status": {
        "code": 404,
        "message": "Not Found",
        "bizMessage": "Permission scope not found.",
        "requestId": "req-permission-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10004"
    }
}
```

#### Fail - Conflict Scope

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "Scope already exists in the permission.",
        "requestId": "req-permission-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10003"
    }
}
```

#### Fail - Conflict Last Scope

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "Permission cannot become unscoped while assigned to roles or users.",
        "requestId": "req-permission-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10006"
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
        "requestId": "req-permission-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

#### Fail - Conflict Remaining Scopes

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizCode": "E10006",
        "bizMessage": "Permission cannot be deleted while scope definitions remain.",
        "requestId": "req-permission-delete-scopes",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction. All parameters are bound; caller identity, optional request id and derived permissionId are distinct. Arrays are typed UUID[]. Scope checks/duplicate prechecks use the existing candidate id (SQL NULL for a new parent); child writes/final checks use the actual parent RETURNING id. Definition count includes every non-DELETED row, regardless of master status.

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

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Check existing permission

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.id = '<sequence.id>'
AND p.row_status <> 'DELETED' -- the id of a DELETED permission counts as not found
FOR UPDATE
```

### Table: [author.m_scope](../../../schema/author/m_scope.md)

#### QUERY - Check scope

```SQL
SELECT
    s.id as scope_id
FROM author.m_scope s
WHERE s.id = ANY ('<sequence.activeScopeIds>'::UUID[])
AND s.row_status = 'ACTIVE'
ORDER BY s.id
FOR UPDATE
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check existing permission scope

```SQL
SELECT
    ps.id as permission_scope_id,
    ps.scope_id
FROM author.t_permission_scope ps
WHERE ps.id = ANY ('<sequence.permissionScopeIds>'::UUID[])
AND ps.permission_id = '<sequence.permissionId>'
AND ps.row_status <> 'DELETED' -- supplied ids must belong to this permission
ORDER BY ps.id
FOR UPDATE
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Count permission scope definitions

```SQL
SELECT
    COUNT(ps.id) as definition_count
FROM author.t_permission_scope ps
WHERE ps.permission_id = '<sequence.permissionId>'
AND ps.row_status <> 'DELETED'
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### QUERY - Check duplicate name

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.name = '<sequence.name>'
AND p.row_status <> 'DELETED'
AND ('<sequence.id>' IS NULL OR p.id <> '<sequence.id>') -- omitted insert id is typed SQL NULL
```

### Table: [author.t_role_permission](../../../schema/author/t_role_permission.md)

#### QUERY - Check role permission in use

```SQL
SELECT
    rp.id as role_permission_id
FROM author.t_role_permission rp
WHERE rp.permission_id = '<sequence.permissionId>' -- destructive parent check or final Q22 guard
AND rp.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_id = '<sequence.permissionId>' -- destructive parent check or final Q22 guard
AND up.row_status <> 'DELETED'
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### QUERY - Check duplicate permission scope

```SQL
SELECT
    ps.id as permission_scope_id
FROM author.t_permission_scope ps
WHERE ps.permission_id = '<sequence.permissionId>'
AND ps.scope_id = '<sequence.scopes.scopeId>'
AND ps.row_status <> 'DELETED'
AND ('<sequence.scopes.id>' IS NULL OR ps.id <> '<sequence.scopes.id>') -- omitted child insert id is typed SQL NULL
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### QUERY - Check role permission scope in use

```SQL
SELECT
    rps.id as role_permission_scope_id
FROM author.t_role_permission_scope rps
WHERE rps.permission_scope_id = '<sequence.scopes.id>' -- only when the scope item is deleted
AND rps.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission scope in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_scope_id = '<sequence.scopes.id>' -- only when the scope item is deleted
AND up.row_status <> 'DELETED'
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### INSERT - Create permission

```SQL
INSERT INTO author.m_permission (
    created_by,
    created_at,
    row_status,
    name,
    description
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.rowStatus>',
    '<sequence.name>',
    '<sequence.description>'
)
RETURNING id as permission_id
```

### Table: [author.m_permission](../../../schema/author/m_permission.md)

#### UPDATE - Update or delete permission

```SQL
UPDATE author.m_permission
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.rowStatus>',
    name = '<sequence.name>',
    description = '<sequence.description>'
WHERE id = '<sequence.id>'
AND row_status <> 'DELETED'
RETURNING id as permission_id
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### INSERT - Create permission scope

```SQL
INSERT INTO author.t_permission_scope (
    created_by,
    created_at,
    row_status,
    permission_id,
    scope_id
)
VALUES (
    '<sequence.createdBy>',
    '<sequence.now>',
    '<sequence.scopes.rowStatus>',
    '<sequence.permissionId>',
    '<sequence.scopes.scopeId>'
)
RETURNING id as permission_scope_id
```

### Table: [author.t_permission_scope](../../../schema/author/t_permission_scope.md)

#### UPDATE - Update or delete permission scope

```SQL
UPDATE author.t_permission_scope
SET
    updated_by = '<sequence.updatedBy>',
    updated_at = '<sequence.now>',
    row_status = '<sequence.scopes.rowStatus>'
WHERE id = '<sequence.scopes.id>'
AND permission_id = '<sequence.permissionId>'
AND scope_id = '<sequence.scopes.scopeId>'
AND row_status <> 'DELETED'
RETURNING id as permission_scope_id
```
