---
name: Author Me API Specification
description: Defines the calling JWT role snapshot and platform-administrator flag, current credential/user validation, deterministic mapping, read-only SQL and complete outcomes for GET v1/author/me.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/author/me

| Title       | Description                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Me API                                                                                                                         |
| Method      | GET                                                                                                                            |
| Endpoint    | v{version}/author/me                                                                                                           |
| Version     | 1                                                                                                                              |
| Description | Inquiry the roles of the logged-in user and whether the user is a platform administrator, The user comes from the access token |

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

No query parameters. The answer is about the caller.

### Me Rules

- Governing decisions: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q4/Q11/Q13, approved by the product owner. This detailed endpoint revision remains in-review; no backend implementation is included. Any caller with a valid access token can call this API, and sees only the caller's own snapshot.
- No body or query parameters are accepted as a target user. Validate mandatory timestamp as a UTC timestamp before SQL; missing/malformed timestamp returns 400 E10001. Generate requestId if omitted. Missing/malformed Bearer credentials or a failed JWT signature/issuer/audience/expiry/sub/role-claim validation return the same 401 E10002 `Invalid or expired access token.` before SQL.
- Verify signature using server configuration, issuer, audience, exp and a UUID sub. Validate the structured roles claim defined by [login](../../authen-and-author/02-login/spec.md#claim-resolution-and-payload): roles must be an array, including explicit [] for no roles; each object has a UUID roleId and non-empty string name. Missing/non-array roles, malformed objects or duplicate roleIds make the credential invalid (401); never silently replace malformed claims with an empty list or recover privileges from the database. Extra token claims are not extra response fields.
- userId comes only from verified sub; accessTokenHash is SHA-256 (32 bytes) of the exact presented JWT. Capture fresh server UTC now immediately before the one credential query and recheck JWT expiry at now. The query must find the ACTIVE, unexpired stored token for that hash/userId and an ACTIVE user. Missing/revoked/expired token, mismatched owner or inactive user returns the same 401. No request userId, role, role name or isPlatformAdmin value controls this lookup or the response.
- The SQL is one read-only autocommit SELECT; no explicit BEGIN, COMMIT, ROLLBACK or locking read is required. It checks credential and user together in one statement snapshot and creates no writes. An already-authorized in-flight read may finish; a credential revoked before the query is rejected. No response revives an inactive credential. Do not reuse a pre-lock snapshot for another API's writes.
- **Role source:** return the calling token's role snapshot. Do not query author.t_user_role or author.m_role to reload, filter, rename or replace those roles. Role/assignment changes after issuance do not change this token's response; an old PLATFORM_ADMIN token may still report true until its own expiry, exactly as its privileges remain usable under Q4. The current token/user status check still allows logout/password reset to revoke credentials immediately (Q13).
- Copy only roleId/name from verified roles; sort roles by name using ordinal case-sensitive comparison, then by roleId. isPlatformAdmin is true exactly when one returned role has name equal to PLATFORM_ADMIN (case-sensitive). Do not trust an independent isPlatformAdmin token claim or a request flag. roles=[] returns isPlatformAdmin=false. Database rows are not needed to sort or compute this flag.
- Every refresh resolves latest ACTIVE grants for the newly issued token. Calling this endpoint with that refreshed token reports the refreshed snapshot, while an older still-valid token keeps its own prior roles. The endpoint never refreshes a token or alters role assignments itself. Current profile/lifecycle data is not substituted for role claims.
- Preserve the response shape: data.userId, data.isPlatformAdmin and data.roles containing roleId/name only. Permissions and scopes are not returned by this endpoint even though login/refresh carry them; no permission grant is inferred from the response. Never return stored token hashes or internal credential ids.
- After valid input/JWT, perform the single credential query, then map the snapshot and return 200 S10000. There is no 403 for a non-admin or no-role token. Timeout returns 408 E90001; unexpected failure returns generic 500 with no new bizCode. No outcome writes data and no 200 is sent before credential validation and snapshot mapping complete.

#### Scenario correspondence with sequence.wsd

| Scenario                                    | Required sequence behavior                                                   | HTTP             | Role result                      |
| ------------------------------------------- | ---------------------------------------------------------------------------- | ---------------- | -------------------------------- |
| Invalid timestamp                           | Before SQL                                                                   | 400 E10001       | None                             |
| Missing/invalid JWT or malformed roles      | Signature/payload validation before SQL                                      | 401 E10002       | None                             |
| Inactive/revoked/expired credential or user | One credential lookup; no role-table query                                   | 401 E10002       | None                             |
| Valid token with roles                      | Sort roleId/name from that token                                             | 200 S10000       | Token snapshot only              |
| Valid token with PLATFORM_ADMIN             | Derive true from exact returned role name                                    | 200 S10000       | Token snapshot only              |
| Valid token with []                         | Return empty roles and false                                                 | 200 S10000       | Empty snapshot                   |
| Assignment revoked after issuance           | Keep old token's role snapshot until expiry if credential/user remain ACTIVE | 200 S10000       | May still contain PLATFORM_ADMIN |
| Refreshed token after revocation            | Use the refreshed token's newly resolved snapshot                            | 200 S10000       | May be []/false                  |
| Timeout / unexpected failure                | Read-only error; no transaction writes                                       | 408 E90001 / 500 | None                             |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/author/me HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-06T09:00:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/author/me' \
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

|     | Parameter Name  | Data Type                     | M/O       | Source           | Field                | Description                                                              | Example                              |
| --- | --------------- | ----------------------------- | --------- | ---------------- | -------------------- | ------------------------------------------------------------------------ | ------------------------------------ |
| 1   | userId          | String: UUID                  | MANDATORY | Sequence Diagram | data.userId          | User Id (the caller)                                                     | b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e |
| 2   | isPlatformAdmin | Boolean                       | MANDATORY | Sequence Diagram | data.isPlatformAdmin | TRUE when the caller has the role PLATFORM_ADMIN                         | false                                |
| 3   | roles           | [Array of Role](#role-object) | MANDATORY | Sequence Diagram | data.roles           | Role snapshot in the calling token; empty array when that token has none |                                      |

#### Role Object

|     | Parameter Name | Data Type    | M/O       | Source           | Field               | Description | Example                              |
| --- | -------------- | ------------ | --------- | ---------------- | ------------------- | ----------- | ------------------------------------ |
| 1   | roleId         | String: UUID | MANDATORY | Sequence Diagram | data.roles[].roleId | Role Id     | a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | name           | String       | MANDATORY | Sequence Diagram | data.roles[].name   | Role Name   | CATALOG_MANAGER                      |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-06T09:00:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "isPlatformAdmin": false,
        "roles": [
            {
                "roleId": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "name": "CATALOG_MANAGER"
            },
            {
                "roleId": "d0e1f2a3-b4c5-4d6e-9f7a-8b9c0d1e2f3a",
                "name": "SHOP_SUPPORT"
            }
        ]
    }
}
```

#### Success - Platform Administrator

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-8f6a2b4c-5d7e-4f9a-b1c3-4d5e6f7a8b9c",
        "timestamp": "2026-11-06T09:10:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "c2d3e4f5-a6b7-4c8d-9e0f-1a2b3c4d5e6f",
        "isPlatformAdmin": true,
        "roles": [
            {
                "roleId": "6f7a8b9c-0d1e-4f2a-9b3c-4d5e6f7a8b9c",
                "name": "PLATFORM_ADMIN"
            }
        ]
    }
}
```

#### Success - No Role

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Me Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-06T09:20:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "userId": "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e",
        "isPlatformAdmin": false,
        "roles": []
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

#### Fail - Bad Request

```JSON
{
    "status": {
        "code": 400,
        "message": "Bad Request",
        "bizCode": "E10001",
        "bizMessage": "Timestamp is a required header and must be a valid UTC timestamp.",
        "requestId": "req-me-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
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
        "requestId": "req-me-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

One typed, bound, read-only SELECT validates the stored credential and user. Roles and the administrator flag come from the already-verified JWT, not a role lookup. No explicit transaction or mutation is needed.

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check active credential and user

```SQL
SELECT
    at.user_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
AND EXISTS (
    SELECT 1
    FROM authen.m_user u
    WHERE u.id = at.user_id
    AND u.row_status = 'ACTIVE'
)
```
