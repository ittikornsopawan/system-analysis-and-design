---
name: Submit Consent API Specification
description: Defines authenticated read-only consent display, later answers, no-op repeated reads, current active-type eligibility, atomic user-scoped batch SQL and history preservation for POST v1/consent/submit.
status: in-review
approved_by: null
approved_at: null
---

# [POST]: v1/consent/submit

| Title       | Description                                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Name        | Submit Consent API                                                                                                             |
| Method      | POST                                                                                                                           |
| Endpoint    | v{version}/consent/submit                                                                                                      |
| Version     | 1                                                                                                                              |
| Description | Submit multiple consents of the user at the same time, Result can be omitted to only update that the user has read the consent |

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

|     | Parameter Name | Data Type | M/O       | Description                                                            | Example                                        |
| --- | -------------- | --------- | --------- | ---------------------------------------------------------------------- | ---------------------------------------------- |
| 1   | content-type   | String    | MANDATORY | Content type of the request                                            | application/json                               |
| 2   | authorization  | String    | MANDATORY | Access token with token type, User is identified from the access token | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 3   | timestamp      | DateTime  | MANDATORY | Request timestamp                                                      | 2026-11-05T12:42:00.123Z                       |
| 4   | requestId      | String    | OPTIONAL  | API Request Id                                                         | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Body Parameters

|     | Parameter Name | Data Type                           | M/O       | Description        | Example |
| --- | -------------- | ----------------------------------- | --------- | ------------------ | ------- |
| 1   | consents       | [Array of Consent](#consent-object) | MANDATORY | Consents to submit |         |

#### Consent Object

|     | Parameter Name | Data Type    | M/O       | Description                                                                                                   | Example                              |
| --- | -------------- | ------------ | --------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1   | consentId      | String: UUID | MANDATORY | Consent Id                                                                                                    | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | consentVersion | String       | MANDATORY | Consent Version that the user has read, Must be the current version of the consent                            | 1.1.0                                |
| 3   | isRead         | Boolean      | MANDATORY | Must be true: this call records display/read; an already-read version keeps its first readAt                  | true                                 |
| 4   | result         | Boolean      | OPTIONAL  | Consent result (Accept, Reject), Keep the current result when not specified, Defaults to FALSE when inserting | true                                 |

### Submit Consent Rules

- Governing decisions: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q3/Q5/Q8/Q13/Q16/Q17, approved by the product owner. This detailed revision remains in-review and includes no backend implementation.
- On displaying a consent, call this endpoint with its consentId, displayed consentVersion and isRead=true, without result. Answering later calls the same endpoint with result=true or false. An existing answer survives a read-only request. An already-read version keeps its original read_at: do not write read state again. An already-read read-only request, or the same explicit answer on already-read evidence, performs no UPDATE at all (including audit columns). An answer change may update result while preserving read state/timestamp.
- Validate JSON, mandatory content-type/timestamp, consents as a non-empty array, each UUID consentId, non-empty consentVersion (maximum 8 characters), mandatory boolean isRead=true, and optional boolean result before database access. Omission of result means read-only; null, a string or a number is not an omitted boolean. Duplicate consentIds return 400 E10001; do not apply the same consent twice or pick one answer. Invalid body/ordinary headers return 400 before BEGIN. Missing/malformed/invalid Bearer credentials return the same 401 E10002 `Invalid or expired access token.`
- Verify JWT signature, issuer, audience, exp and UUID sub using server configuration; derive userId only from the verified sub and accessTokenHash as SHA-256 (32 bytes) of the exact presented JWT. No body userId or token-supplied role changes the target user. Any ACTIVE authenticated user may submit their own consents; no administrator role is required and no assignment-table lookup authorizes this endpoint.
- Lock order: BEGIN READ COMMITTED -> lock ACTIVE authen.m_user by verified userId FOR UPDATE -> capture fresh UTC now after the lock -> recheck JWT expiry and the ACTIVE stored access-token hash/user/expiry -> validate the complete current consent set -> process evidence in ascending consentId order -> COMMIT before 200. Logout/reset and other writes for this user take the same user lock. A waiter must check token revocation after acquiring the lock; do not authorize from a pre-lock snapshot or transaction-start NOW(). Missing user/token or expired JWT returns 401 after ROLLBACK, with no evidence changes.
- The eligibility query reads submitted consents and ACTIVE types in one READ COMMITTED statement snapshot: consent itself ACTIVE, effective_at <= now, expired_at IS NULL or expired_at > now, and an ACTIVE referenced type. Compare the complete returned id set with the request before any evidence write. A hidden/missing/future/expired consent or inactive type returns 404 E10004 `Consent not found.` A displayed version unequal to the returned current version returns the existing 409 E10003 `Consent version is not the current version.` Reject the whole batch, never a partial success. Eligibility is evaluated at that one validation snapshot; later policy publications affect subsequent calls while existing evidence is retained.
- Every supplied item records its displayed current version as read. A new evidence row stores result=false when result was omitted, is_read=TRUE and read_at=now. Optional rejection is also read. Required rejection/read-only is allowed for an existing user and stays pending until both read and accepted (Q8/Q9); this API adds no service-access gate.
- Existing evidence is keyed logically by (userId, consentId, consentVersion). The schema has no unique constraint; serialize all calls under the user lock so concurrent display/answer requests cannot both insert. For legacy multiple ACTIVE rows, select the newest created_at, then greatest id as a deterministic canonical row. Update/return only that row; preserve all older rows and all other versions. Pending/inquiry must use the same canonical choice when their own API review is delivered; do not infer acceptance from any arbitrary older duplicate. Register creates a new user and cannot race an authenticated request for that same uncommitted user.
- For an existing unread row, mark it read once and set read_at=now; preserve its current result when result is omitted. For an already-read row, preserve read_at even when NULL in legacy data; do not invent a first-read time. For an explicit answer change, update result only as part of the guarded evidence update. resultSpecified records presence independently of its boolean value, so explicit false is never treated as omission. The SQL predicate prevents no-op UPDATEs; Application skips the UPDATE entirely when already read and result is omitted/unchanged.
- Use typed bound UUID arrays, timestamps and booleans, never string-concatenated SQL. userId/createdBy/updatedBy are the authenticated server-derived user id. Each item maps its query/INSERT/UPDATE result to consentId, consentVersion, isRead, readAt and result. Return data.consents in original request order, even though processing is sorted. No stored token/hash or internal evidence id is returned.
- New-row INSERT, existing-row UPDATE and no-op are mutually exclusive per item. UPDATE guards id, user_id, consent_id, consent_version and ACTIVE state; an unexpected zero-row guarded update is an internal consistency failure, causing whole-batch ROLLBACK and generic 500, not a partial 200. An empty id array never reaches SQL because the request is invalid.
- All evidence writes are one transaction. A later item/DB failure rolls back earlier item changes. Timeout before COMMIT rolls back and returns 408 E90001; unexpected failure rolls back and returns generic 500 without a new bizCode. Return 200 only after COMMIT succeeds, including all-no-op batches. Lost response after commit does not undo evidence; retrying the same displayed version preserves its first read timestamp and is a no-op when the answer is unchanged. Old versions and inactive-type evidence are never deleted or rewritten by this call.

#### Scenario correspondence with sequence.wsd

| Scenario                                                            | Required sequence behavior                             | HTTP             | Durable effects        |
| ------------------------------------------------------------------- | ------------------------------------------------------ | ---------------- | ---------------------- |
| Invalid body/headers or duplicate ids                               | No SQL or BEGIN                                        | 400 E10001       | None                   |
| Invalid/missing JWT                                                 | Verify before BEGIN; no SQL                            | 401 E10002       | None                   |
| Missing/inactive user or revoked/expired credential after lock wait | ROLLBACK before response                               | 401 E10002       | None                   |
| Missing/hidden consent or inactive type                             | Full-batch eligibility check before writes; ROLLBACK   | 404 E10004       | None                   |
| Stale displayed version                                             | Compare all versions before writes; ROLLBACK           | 409 E10003       | None                   |
| First display, no answer                                            | INSERT false/TRUE/now for new row; COMMIT              | 200 S10000       | Read evidence          |
| First display of existing unread row                                | UPDATE read flag/time; preserve omitted answer; COMMIT | 200 S10000       | First read             |
| Repeated display / unchanged answer on already-read row             | No INSERT/UPDATE; reuse canonical row; COMMIT          | 200 S10000       | Unchanged              |
| Answer after display                                                | UPDATE explicit answer; preserve first read_at; COMMIT | 200 S10000       | Answer only plus audit |
| Any pre-commit failure                                              | ROLLBACK every item before response                    | 408 E90001 / 500 | None                   |

All database notes show the exact SQL visibly; every query/write result returns to Application before its next branch or response mapping.

#### Example Body Parameters

```JSON
{
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.1.0",
            "isRead": true,
            "result": true
        },
        {
            "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "consentVersion": "1.0.0",
            "isRead": true
        }
    ]
}
```

#### Example Body Parameters - Display only

```JSON
{
    "consents": [
        {
            "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "consentVersion": "1.0.0",
            "isRead": true
        }
    ]
}
```

## Example Request

### HTTP Request

```HTTP
POST /api-dev/v1/consent/submit HTTP/1.1
Host: www.domain.com
content-type: application/json
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.1.0",
            "isRead": true,
            "result": true
        },
        {
            "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "consentVersion": "1.0.0",
            "isRead": true
        }
    ]
}
```

### cUrl Request

```JSON
curl --location --request POST 'https://www.domain.com/api-dev/v1/consent/submit' \
--header 'content-type: application/json' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
--header 'requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d' \
--data-raw '{
    "consents": [
        {
            "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
            "consentVersion": "1.1.0",
            "isRead": true,
            "result": true
        },
        {
            "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
            "consentVersion": "1.0.0",
            "isRead": true
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

|     | Parameter Name | Data Type                                               | M/O       | Source           | Field         | Description        | Example |
| --- | -------------- | ------------------------------------------------------- | --------- | ---------------- | ------------- | ------------------ | ------- |
| 1   | consents       | [Array of Submitted Consent](#submitted-consent-object) | MANDATORY | Sequence Diagram | data.consents | Submitted consents |         |

#### Submitted Consent Object

|     | Parameter Name | Data Type         | M/O       | Source           | Field                          | Description                                                      | Example                              |
| --- | -------------- | ----------------- | --------- | ---------------- | ------------------------------ | ---------------------------------------------------------------- | ------------------------------------ |
| 1   | consentId      | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentId      | Consent Id                                                       | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d |
| 2   | consentVersion | String            | MANDATORY | Sequence Diagram | data.consents[].consentVersion | Consent Version                                                  | 1.1.0                                |
| 3   | isRead         | Boolean           | MANDATORY | Sequence Diagram | data.consents[].isRead         | User has read the consent                                        | true                                 |
| 4   | readAt         | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.consents[].readAt         | Timestamp when the user read the consent (Without time zone UTC) | 2026-11-05T12:42:00.123Z             |
| 5   | result         | Boolean           | MANDATORY | Sequence Diagram | data.consents[].result         | Consent result (Accept, Reject)                                  | true                                 |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Submit Consent Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consents": [
            {
                "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "consentVersion": "1.1.0",
                "isRead": true,
                "readAt": "2026-11-05T12:42:00.123Z",
                "result": true
            },
            {
                "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "consentVersion": "1.0.0",
                "isRead": true,
                "readAt": "2026-11-05T12:42:00.123Z",
                "result": false
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
        "bizMessage": "Consents must be non-empty; consentId, consentVersion and isRead=true are required.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
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
        "bizMessage": "Consent not found.",
        "requestId": "req-404a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:05.321Z",
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
        "bizMessage": "Consent version is not the current version.",
        "requestId": "req-409a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:44:20.789Z",
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

#### Fail - Internal Server Error

```JSON
{
    "status": {
        "code": 500,
        "message": "Internal Server Error",
        "bizMessage": "An unexpected error occurred.",
        "requestId": "req-submit-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

The consent eligibility statement includes its type in one statement snapshot via EXISTS; both tables are read together. Evidence query/insert/update execute per item under the common user lock, in consentId order. Parameters are typed and bound, not interpolated.

### Table: [authen.m_user](../../../schema/authen/m_user.md)

#### QUERY - Lock the user

```SQL
SELECT
    u.id as user_id
FROM authen.m_user u
WHERE u.id = '<sequence.userId>'
AND u.row_status = 'ACTIVE'
FOR UPDATE -- user lock precedes token and evidence reads
```

### Table: [authen.t_user_access_token](../../../schema/authen/t_user_access_token.md)

#### QUERY - Check the active access token

```SQL
SELECT
    at.id as access_token_id
FROM authen.t_user_access_token at
WHERE at.token = '<sequence.accessTokenHash>'
AND at.user_id = '<sequence.userId>'
AND at.row_status = 'ACTIVE'
AND at.expired_at > '<sequence.now>'
```

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Get active consents

```SQL
SELECT
    c.id as consent_id,
    c.consent_version
FROM consent.t_consent c
WHERE c.id = ANY ('<sequence.consentIds>'::UUID[])
AND c.row_status = 'ACTIVE'
AND c.effective_at <= '<sequence.now>'
AND (c.expired_at IS NULL OR c.expired_at > '<sequence.now>')
AND EXISTS (
    SELECT 1
    FROM consent.m_consent_type ct
    WHERE ct.id = c.consent_type_id
    AND ct.row_status = 'ACTIVE'
)
ORDER BY c.id
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### QUERY - Get existing user consent

```SQL
SELECT
    uc.id as user_consent_id,
    uc.consent_id,
    uc.consent_version,
    uc.result,
    uc.is_read,
    uc.read_at
FROM authen.t_user_consent uc
WHERE uc.user_id = '<sequence.userId>'
AND uc.consent_id = '<sequence.consents.consentId>'
AND uc.consent_version = '<sequence.consents.consentVersion>'
AND uc.row_status = 'ACTIVE'
ORDER BY uc.created_at DESC, uc.id DESC
LIMIT 1
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### INSERT - Create user consent

```SQL
INSERT INTO authen.t_user_consent (
    created_by,
    user_id,
    consent_id,
    consent_version,
    result,
    is_read,
    read_at
)
VALUES (
    '<sequence.userId>',
    '<sequence.userId>',
    '<sequence.consents.consentId>',
    '<sequence.consents.consentVersion>',
    '<sequence.consents.result>', -- explicit result, or false for a new read-only row
    TRUE,
    '<sequence.now>'
)
RETURNING id as user_consent_id, consent_id, consent_version, result, is_read, read_at
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### UPDATE - Update user consent

```SQL
UPDATE authen.t_user_consent
SET
    updated_by = '<sequence.userId>',
    updated_at = '<sequence.now>',
    result = CASE WHEN '<sequence.consents.resultSpecified>'::BOOLEAN THEN '<sequence.consents.result>'::BOOLEAN ELSE result END,
    read_at = CASE WHEN is_read THEN read_at ELSE '<sequence.now>'::TIMESTAMP END,
    is_read = TRUE
WHERE id = '<sequence.userConsentId>'
AND user_id = '<sequence.userId>'
AND consent_id = '<sequence.consents.consentId>'
AND consent_version = '<sequence.consents.consentVersion>'
AND row_status = 'ACTIVE'
AND (NOT is_read OR ('<sequence.consents.resultSpecified>'::BOOLEAN AND result IS DISTINCT FROM '<sequence.consents.result>'::BOOLEAN))
RETURNING id as user_consent_id, consent_id, consent_version, result, is_read, read_at
```
