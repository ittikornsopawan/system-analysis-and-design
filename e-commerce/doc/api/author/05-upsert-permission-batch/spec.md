---
name: Permission Batch Upsert API Specification
description: Defines atomic indexed permission and scope-link batch writes with JWT administration and final scoping invariants.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/author/permission/upsert/batch

| Title       | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Upsert Permission Batch API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Method      | POST                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Endpoint    | v{version}/author/permission/upsert/batch                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Version     | 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description | Insert, update or delete multiple permissions at the same time, only a platform administrator can call it, Each permission is inserted when id is not specified, updated when id is specified, deleted when rowStatus is DELETED, archived when rowStatus is ARCHIVED, The response is always HTTP 200 for a successful batch including when it deletes (each result is reported in the body with its action), All permissions are processed in one transaction in the request order, If any permission fails then no permission is changed |

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

|     | Parameter Name | Data Type                                 | M/O       | Description                                                    | Example |
| --- | -------------- | ----------------------------------------- | --------- | -------------------------------------------------------------- | ------- |
| 1   | permissions    | [Array of Permission](#permission-object) | MANDATORY | Permissions to insert, update or delete (min 1, max 100 items) |         |

#### Permission Object

|     | Parameter Name | Data Type                       | M/O       | Description                                                                                                                                                                                                                     | Example                              |
| --- | -------------- | ------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID                    | OPTIONAL  | Permission Id, Insert when not specified, Update, Delete or Archive when specified, The id of a DELETED permission counts as not found, Must not be duplicated in the request                                                   | e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b |
| 2   | name           | String                          | MANDATORY | Permission Name, Permission code (max 64 characters): lower-case letters, digits, `_` and `.`, at least two parts, Unique among permissions that are not DELETED                                                                | report.read                          |
| 3   | description    | String                          | MANDATORY | Permission Description (max 256 characters)                                                                                                                                                                                     | Reads the platform reports           |
| 4   | scopes         | [Array of Scope](#scope-object) | OPTIONAL  | Scopes of the permission, same rules as the single upsert                                                                                                                                                                       |                                      |
| 5   | rowStatus      | String                          | OPTIONAL  | Row status (ACTIVE, INACTIVE, DELETED, LOCKED, ARCHIVED), Defaults to ACTIVE, Delete when DELETED, Archive when ARCHIVED, DELETED is not allowed when inserting, Delete requires zero final non-DELETED scope definitions (Q24) | ACTIVE                               |

#### Scope Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                                                                                                                           | Example                              |
| --- | -------------- | ------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | id             | String: UUID | OPTIONAL  | Permission Scope Id, Insert when not specified, Update or Delete when specified, Must belong to this permission and must not be duplicated                                                                            | 3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f |
| 2   | scopeId        | String: UUID | MANDATORY | Scope Id, ACTIVE master required only for ACTIVE links (404 E10005), An owned existing link to a closed master can be removed (Q23), Immutable when id is specified, No duplicate scope among non-DELETED input items | 1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d |
| 3   | rowStatus      | String       | OPTIONAL  | Row status (ACTIVE, DELETED), Defaults to ACTIVE, Delete when DELETED (not allowed when inserting), A scope that a role or user still uses cannot be deleted                                                          | ACTIVE                               |

### Permission Rules (same as the single upsert, applied per permission)

- Every permission follows the rules of [the single upsert](../04-upsert-permission/spec.md#permission-rules): name is the permission code: lower-case letters, DELETED is final, delete and archive are rejected while a role (`author.t_role_permission`) or a user (`author.t_user_permission`) that is not DELETED still holds it.
- The permissions are processed in the request order in one transaction, so the checks of an item see the changes of the items before it. When any item fails the whole request is rolled back and no permission is changed. `id` must not be duplicated in the request, and `name` must not be duplicated among the items that are not DELETED (400, E10001). An item without `id` and with `rowStatus` DELETED is rejected with 400 (E10001). The response is HTTP 200 for every successful batch, including a batch that deletes. The 403 message has no item position (the permission is the caller's, not the item's).
- `scopes` lists the scopes the permission can have (`author.t_permission_scope`). An item without `id` is added, with `id` is updated, with `rowStatus` DELETED is removed. Scopes that are not listed are kept. Adding/retaining an ACTIVE link requires an ACTIVE master (404 E10005); deleting an existing owned link skips that master-status test under owner Q23. A scope cannot be deleted from the permission while a role (`author.t_role_permission_scope`) or a user (`author.t_user_permission`) still uses it (409, E10006). A permission without scopes has no scope dimension.
- Permission: only a platform administrator from the verified JWT roles claim can call this API; exact case-sensitive PLATFORM_ADMIN is required. Authorize once after all target existence checks and before scope/conflict work; valid non-admin claims return one 403 E10009 with no item index. Approved by the product owner (Q2/Q4/Q10/Q13); no live caller-assignment fallback.

### Credential, Batch Scope and Transaction Rules

- Governing decisions: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md); Q22/Q23 approved by the product owner on 2026-11-08. The detailed revision remains in-review; no backend/schema implementation.
- Validate the entire request before SQL: one JSON object containing only permissions, no unknown/repeated keys or query fields, JSON content type and mandatory UTC timestamp. Generate requestId if omitted. permissions must be an array of 1..100 objects. Each object allows only id/name/description/scopes/rowStatus; a supplied id is a non-null UUID. Required name/description are non-null nonblank strings, max 64/256 characters, with name matching ^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$ without trimming/case-normalization. Parent status defaults to ACTIVE only when omitted, else ACTIVE/INACTIVE/DELETED/LOCKED/ARCHIVED; insert-DELETED is 400 E10001.
- Reject duplicate parsed canonical parent ids, and exact duplicate names among non-DELETED input permissions, with 400 before SQL. Deleted input items do not reserve names. Every supplied scopes is an array (null invalid); scopes omitted or [] means no link change. Each scope object allows only id/scopeId/rowStatus: supplied id is a non-null UUID, required scopeId is a non-null UUID, status defaults to ACTIVE only when omitted and permits ACTIVE/DELETED. Reject insert-DELETED, duplicate canonical child ids within one permission and duplicate scopeIds among its non-DELETED input links. Required fields remain required for deletes. No new scope-array limit is introduced. Item input errors use permissions[i]; envelope/count/header errors have no invented index.
- Verify JWT signature/issuer/audience/expiry/UUID sub and structured unique roles before BEGIN. roles is an array including [], each object has UUID roleId/non-empty name and roleIds are unique; malformed/missing roles is generic 401 E10002, never [] fallback. callerUserId = verified sub, accessTokenHash = SHA-256 exact JWT, createdBy/updatedBy = caller UUID string; never accept request audit values or flags as authority.
- Begin one READ COMMITTED transaction, lock caller user first, capture fresh server UTC now after that lock and recheck JWT exp; require matching hash/caller, ACTIVE token/user and strict expired_at > now. Missing/revoked/inactive/expired credentials is generic 401 before target reads. Logout/reset share the caller lock. Old claims remain usable after grant withdrawal until token expiry; refresh resolves current grants.
- Lock order: caller user -> all existing target permissions ordered by id -> all ACTIVE referenced scope masters ordered by id -> requested owned permission-scope definitions ordered by id -> writes. targetPermissionIds is the typed UUID[] of all supplied parent ids (empty allowed). Lock matching non-DELETED parents in one query; map rows by id. Check all supplied target ids in original request order before permission, any missing/DELETED parent gives 404 E10004 permissions[i]: Permission not found. No resurrection. Authorize once from exact PLATFORM_ADMIN in verified JWT roles; do not query live caller grants.
- activeScopeIds contains only scopeIds requested ACTIVE anywhere in the batch; permissionScopeIds contains all supplied child ids. Lock ACTIVE masters globally, then requested non-DELETED definitions restricted to targetPermissionIds, both sorted by id. Map each returned child id to its stored permission_id and scope_id. For a current permission bind permissionId to its verified target id or typed SQL NULL for an insert; optional permissions.id, callerUserId and derived permissionId are distinct. After parent RETURNING replace permissionId with the actual returned UUID for child writes and final reads.
- Iterate permissions[i] in original input order, not lock order. Validate its child references before any of its writes: ACTIVE link requires a returned ACTIVE master (404 E10005); DELETED link skips master ACTIVE validation. An existing child must belong to this current parent, be non-DELETED and have the same immutable scopeId, else 404 E10004 or 400 E10001 for a changed scopeId. A supplied child cannot belong to a new parent. No other parent's data is disclosed.
- Q23 owner answer: “ใช่ อนุญาตถอน link ของ scope ที่ปิดแล้ว”. Removing an existing owned link permits an INACTIVE/LOCKED/ARCHIVED/DELETED master; ownership, immutable scopeId, non-DELETED reference and Q22 checks still apply. ACTIVE link creation/retention still requires an ACTIVE master. No master or grant row is changed.
- Capture beforeDefinitionCount as every non-DELETED definition of the current permission, irrespective of definition/master status. Run name/child duplicate and parent/link in-use checks before this permission's parent/child writes. Name uniqueness spans all non-DELETED parents; optional parent/child insert ids bind typed SQL NULL with null-safe exclusions. Every child precheck precedes the current parent's first write: deleting then readding the same existing scopeId within its array still conflicts in pre-write state. Omitted/unlisted links are kept.
- Each permission's conflict queries see earlier permission writes in the same transaction. Deleting a permission may release its name for a later insert; reversing the order returns duplicate 409 at that earlier insert. This is request-order visibility, not a final-state rename plan. Existing parent DELETED/ARCHIVED is 409 E10006 while any non-DELETED role/direct-user grant holds it; a DELETED child is 409 E10006 while any non-DELETED role-scope/direct-user row references it, including inactive/locked/archived references. These are business reads, never caller authorization.
- After all of the current permission's parent/child writes, query finalDefinitionCount again. Q22 triggers only when beforeDefinitionCount > 0 and finalDefinitionCount = 0, then freshly query non-DELETED role/direct-user grants. Any surviving grant gives 409 E10006 permissions[i]: Permission cannot become unscoped while assigned to roles or users. and rolls back every item, link and audit change. Owner answer: “ใช่ ปฏิเสธจนถอน grant เดิมครบ”. Already-unscoped metadata updates may keep valid unscoped grants. Because parent ids cannot repeat and child ownership is enforced, this post-item state is that permission's final whole-request state; no later item may alter its definitions. Count all non-DELETED definitions, not only ACTIVE or ACTIVE-master ones.
- Q24 approved by the product owner on 2026-11-09: owner answered “ต้องถอน links ให้ครบก่อนลบ permission (แนะนำ)”. After the current permission's child writes, reuse finalDefinitionCount before Q22 or result mapping. If rowStatus = DELETED and finalDefinitionCount > 0, return 409 E10006 `permissions[i]: Permission cannot be deleted while scope definitions remain.` and roll back the entire batch, including earlier permissions, links and audit writes; return no partial results. Count every non-DELETED definition (ACTIVE/INACTIVE/LOCKED/ARCHIVED), even if its master is closed. Omitted scopes, [] and partial withdrawal do not bypass this check. Complete explicit withdrawal and parent deletion in one request are allowed subject to ownership, immutable-id and reference checks. A parent with only DELETED history may be deleted. No implicit cascade; ARCHIVED and other reversible parent states may retain definitions. The no-duplicate-parent and child-ownership rules make this per-item post-write count the permission's final whole-request state. This prevents new stranded definitions without approving a legacy-data rewrite or a deleted-parent cleanup endpoint.
- Parent/child INSERTs explicitly set server created_at and must return exactly one UUID; missing/malformed results are generic 500. Parent UPDATE guards id/non-DELETED; child UPDATE guards id/derived permissionId/immutable scopeId/non-DELETED. A zero-row update is indexed 404 E10004; returned existing ids must match input ids. Preserve creation audit. Parent archive and reversible states keep unlisted child definitions. Parent delete requires no non-DELETED definitions after explicit child actions (Q24); keeping an unlisted live definition rejects the entire batch. Explicit child actions remain atomic and there is no implicit cascade. No grant history is rewritten.
- Append exactly index/permissionId/action from RETURNING for each permission, original zero-based index and order; action is INSERT for omitted id (including insert-ARCHIVED), otherwise DELETE for DELETED, ARCHIVE for ARCHIVED, UPDATE for ACTIVE/INACTIVE/LOCKED. Include delete results. Require one result per input, no duplicate returned parent ids and exactly data.permissions. Complete Q24 and Q22 for every permission. Finish all mapping before one COMMIT after the outer loop; then one HTTP 200 S10000 Batch Upsert Permission Success. No item-level 201/204, rowStatus, child ids or partial result is returned.
- Every item-specific 400/404/409 has permissions[i] prefix; authorization 403 has no item position. SQLSTATE 23505 from uq_m_permission_name maps to indexed 409 E10003 Permission name already exists.; uq_t_permission_scope_permission_id_scope_id maps to indexed 409 E10003 Scope already exists in the permission. Both roll back all earlier items. Unexpected SQL/result/mapping failures are request-level generic 500 without bizCode; timeout before COMMIT is request-level 408 E90001 after rollback. No retry is promised for an unknown commit result.
- Shared grant/reference writers must lock and recheck target users first, then permissions/definitions in ascending id order before creating/reopening bindings. Soft-status invariants are not guaranteed by foreign keys; this API's contract and reference SQL fixtures do not certify unmigrated writers. Existing JWT claims are not edited by this endpoint.
- Execution order: whole-input validation (400) -> JWT (401) -> BEGIN -> caller lock/current credentials (401) -> all target locks/existence (404) -> one claims permission (403, E10009) -> global ACTIVE-master/owned-child locks -> per-permission reference/pre-write conflicts, parent/child writes, final count, Q24 deletion guard, Q22 check and indexed mapping -> full result validation -> COMMIT -> one 200. Every post-BEGIN failure rolls back the entire batch.

#### Scenario correspondence with sequence.wsd

| Scenario                                                                               | Outcome                                      | Effects                                      |
| -------------------------------------------------------------------------------------- | -------------------------------------------- | -------------------------------------------- |
| Invalid count/items/duplicate canonical ids or names / malformed JWT                   | 400 / 401 before SQL                         | None                                         |
| Missing caller, current credential failure or expiry while waiting                     | Generic 401 before targets                   | Rollback                                     |
| Later target missing despite earlier potential conflict / valid non-admin              | Indexed 404 / unindexed 403                  | No writes                                    |
| ACTIVE child references closed master / missing or wrong-owner child / changed scopeId | Indexed 404 E10005 / 404 E10004 / 400 E10001 | Full rollback                                |
| Delete unused link of a closed master                                                  | Allowed Q23, subject to Q22                  | Explicit link removal                        |
| Last definition removed with any surviving role/direct grant                           | Indexed 409 E10006 Q22                       | Restore every earlier item/link/audit        |
| Delete parent with any final non-DELETED definition                                    | Indexed 409 E10006 Q24                       | Restore all earlier parent/link/audit writes |
| Delete parent with complete explicit withdrawal or only DELETED history                | One ordered 200 with DELETE action           | No cascade; history retained                 |
| Delete then reuse name / reverse order                                                 | One 200 / indexed 409                        | Request-order checks, atomic                 |
| Mixed/all-delete/insert-ARCHIVED or 100 valid items                                    | One ordered 200 result                       | One final COMMIT                             |
| Guarded update zero, unique race, timeout, SQL/mapping failure                         | Indexed 404/409, request-level 408/500       | No partial success                           |
| Opposite target order in concurrent requests                                           | Locks ascending, writes input order          | Shared lock protocol                         |

#### Example Body Parameters

```JSON
{
    "permissions": [
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
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
            "rowStatus": "DELETED"
        }
    ]
}
```

The Delete item explicitly withdraws its sole remaining definition. If other non-DELETED definitions exist, include every remaining owned link; omission is not a cascade. The JSON, HTTP and cURL bodies describe the same request.

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/author/permission/upsert/batch HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "permissions": [
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
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
            "rowStatus": "DELETED"
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/author/permission/upsert/batch' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-06T09:00:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "permissions": [
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
        },
        {
            "id": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
            "name": "report.write",
            "description": "Writes the platform reports",
            "scopes": [
                {
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "ACTIVE"
                }
            ],
            "rowStatus": "ACTIVE"
        },
        {
            "id": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
            "name": "review.moderate",
            "description": "Moderates product reviews",
            "scopes": [
                {
                    "id": "3c4d5e6f-7a8b-4c9d-8e1f-2a3b4c5d6e7f",
                    "scopeId": "1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    "rowStatus": "DELETED"
                }
            ],
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

|     | Parameter Name | Data Type                         | M/O       | Source           | Field            | Description                                          | Example |
| --- | -------------- | --------------------------------- | --------- | ---------------- | ---------------- | ---------------------------------------------------- | ------- |
| 1   | permissions    | [Array of Result](#result-object) | MANDATORY | Sequence Diagram | data.permissions | Result of each permission, Same order as the request |         |

#### Result Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field                           | Description                                                | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------------------- | ---------------------------------------------------------- | ------------------------------------ |
| 1   | index          | Numeric      | MANDATORY | Sequence Diagram | data.permissions[].index        | Index of the permission in the request, Starting from 0    | 0                                    |
| 2   | permissionId   | String: UUID | MANDATORY | Sequence Diagram | data.permissions[].permissionId | Inserted, Updated, Deleted or Archived Permission Id       | d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a |
| 3   | action         | String       | MANDATORY | Sequence Diagram | data.permissions[].action       | Action of the permission (INSERT, UPDATE, DELETE, ARCHIVE) | INSERT                               |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Batch Upsert Permission Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "permissions": [
            {
                "index": 0,
                "permissionId": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a",
                "action": "INSERT"
            },
            {
                "index": 1,
                "permissionId": "e5f6a7b8-c9d0-4e1f-8a2b-3c4d5e6f7a8b",
                "action": "UPDATE"
            },
            {
                "index": 2,
                "permissionId": "f6a7b8c9-d0e1-4f2a-9b3c-4d5e6f7a8b9c",
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
        "bizMessage": "permissions[0]: Name and Description are required fields.",
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
        "bizMessage": "permissions[1]: Permission name must be lower-case letters, digits, _ and ., with at least two parts separated by a dot, at most 64 characters.",
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
        "bizMessage": "permissions[1]: Row status must not be DELETED when inserting a permission.",
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
        "bizMessage": "Permissions must contain 1 to 100 items.",
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
        "bizMessage": "permissions[2]: Id is duplicated with permissions[1].",
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
        "bizMessage": "permissions[2]: Name is duplicated with permissions[0].",
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
        "bizMessage": "permissions[1]: Permission not found.",
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
        "bizMessage": "permissions[0]: Scope not found.",
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
        "bizMessage": "permissions[0]: Permission name already exists.",
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
        "bizMessage": "permissions[2]: Permission is used by roles or users.",
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
        "bizMessage": "permissions[0]: Scope is used by roles or users.",
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
        "bizMessage": "permissions[1]: Scope Id cannot be changed.",
        "requestId": "req-permission-batch-review",
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
        "bizMessage": "permissions[1]: Permission scope not found.",
        "requestId": "req-permission-batch-review",
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
        "bizMessage": "permissions[1]: Scope already exists in the permission.",
        "requestId": "req-permission-batch-review",
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
        "bizMessage": "permissions[1]: Permission cannot become unscoped while assigned to roles or users.",
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR",
        "bizCode": "E10006"
    }
}
```

#### Fail - Conflict Remaining Scopes

```JSON
{
    "status": {
        "code": 409,
        "message": "Conflict",
        "bizMessage": "permissions[1]: Permission cannot be deleted while scope definitions remain.",
        "requestId": "req-permission-batch-review",
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
        "requestId": "req-permission-batch-review",
        "timestamp": "2026-11-09T00:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One READ COMMITTED transaction for the entire batch. Every placeholder is bound. Global arrays are typed UUID[]; each item's optional request id and derived parent permissionId remain distinct from callerUserId. Before-parent queries use the verified existing parent id or typed SQL NULL for an insert; child writes/final queries use the actual returned parent UUID.

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

#### QUERY - Lock existing permissions

```SQL
SELECT
    p.id as permission_id
FROM author.m_permission p
WHERE p.id = ANY ('<sequence.targetPermissionIds>'::UUID[])
AND p.row_status <> 'DELETED' -- the id of a DELETED permission counts as not found
ORDER BY p.id
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
    ps.permission_id,
    ps.scope_id
FROM author.t_permission_scope ps
WHERE ps.id = ANY ('<sequence.permissionScopeIds>'::UUID[])
AND ps.permission_id = ANY ('<sequence.targetPermissionIds>'::UUID[])
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
WHERE p.name = '<sequence.permissions.name>'
AND p.row_status <> 'DELETED'
AND ('<sequence.permissions.id>' IS NULL OR p.id <> '<sequence.permissions.id>') -- omitted insert id is typed SQL NULL
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
AND ps.scope_id = '<sequence.permissions.scopes.scopeId>'
AND ps.row_status <> 'DELETED'
AND ('<sequence.permissions.scopes.id>' IS NULL OR ps.id <> '<sequence.permissions.scopes.id>') -- omitted child insert id is typed SQL NULL
```

### Table: [author.t_role_permission_scope](../../../schema/author/t_role_permission_scope.md)

#### QUERY - Check role permission scope in use

```SQL
SELECT
    rps.id as role_permission_scope_id
FROM author.t_role_permission_scope rps
WHERE rps.permission_scope_id = '<sequence.permissions.scopes.id>' -- only when the scope item is deleted
AND rps.row_status <> 'DELETED'
```

### Table: [author.t_user_permission](../../../schema/author/t_user_permission.md)

#### QUERY - Check user permission scope in use

```SQL
SELECT
    up.id as user_permission_id
FROM author.t_user_permission up
WHERE up.permission_scope_id = '<sequence.permissions.scopes.id>' -- only when the scope item is deleted
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
    '<sequence.permissions.rowStatus>',
    '<sequence.permissions.name>',
    '<sequence.permissions.description>'
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
    row_status = '<sequence.permissions.rowStatus>',
    name = '<sequence.permissions.name>',
    description = '<sequence.permissions.description>'
WHERE id = '<sequence.permissions.id>'
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
    '<sequence.permissions.scopes.rowStatus>',
    '<sequence.permissionId>',
    '<sequence.permissions.scopes.scopeId>'
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
    row_status = '<sequence.permissions.scopes.rowStatus>'
WHERE id = '<sequence.permissions.scopes.id>'
AND permission_id = '<sequence.permissionId>'
AND scope_id = '<sequence.permissions.scopes.scopeId>'
AND row_status <> 'DELETED'
RETURNING id as permission_scope_id
```
