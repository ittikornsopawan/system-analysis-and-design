---
name: Pending Consent API Specification
description: Defines authenticated pending-consent inquiry using canonical current-version read/acceptance evidence, active types, a coherent read-only snapshot, response mapping and exact SQL for GET v1/consent/pending.
status: in-review
approved_by: null
approved_at: null
---

# [GET]: v1/consent/pending

| Title       | Description                                                                                                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Pending Consent API                                                                                                                                                     |
| Method      | GET                                                                                                                                                                             |
| Endpoint    | v{version}/consent/pending                                                                                                                                                      |
| Version     | 1                                                                                                                                                                               |
| Description | Return visible current consents pending for the authenticated user: required until read and accepted, optional until read; include latest recorded version and active type name |

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
| 1   | authorization  | String    | MANDATORY | Access token with token type, User is identified from the access token | Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... |
| 2   | timestamp      | DateTime  | MANDATORY | Request timestamp                                                      | 2026-11-05T12:42:00.123Z                       |
| 3   | requestId      | String    | OPTIONAL  | API Request Id                                                         | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d       |

### Pending Consent Rules

- Governing decisions: [owner-confirmed review](../../../../../docs/superpowers/specs/2026-11-07-api-review-design.md), Q3/Q8/Q9/Q13/Q16/Q17, approved by the product owner. This detailed endpoint revision remains in-review; it includes no backend implementation.
- This GET has no body or query parameters. Validate the mandatory timestamp as a UTC timestamp before SQL; invalid/missing timestamp returns 400 E10001. Generate requestId when omitted. Missing/malformed/invalid Bearer credentials return the same 401 E10002 `Invalid or expired access token.` Verify JWT signature, issuer, audience, exp and UUID sub; derive userId only from verified sub and accessTokenHash as SHA-256 (32 bytes) of the exact JWT. This endpoint requires no administrator role or assignment-table query and only returns that user's pending state.
- Use BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY. Capture UTC now immediately before the first credential query, which establishes the transaction snapshot. Check the stored access token hash, verified userId, ACTIVE token, unexpired stored expiry and ACTIVE user together; recheck JWT expiry at now. Failure rolls back and returns 401 before consent queries. Every later policy/evidence/type query uses this same snapshot and now, so a type name, version or submission cannot change halfway through the response. No FOR UPDATE, advisory lock or evidence write is needed for this inquiry.
- Credential eligibility is checked at the first database snapshot. A request whose credential/user was revoked before that snapshot is rejected; an already-authorized in-flight read may finish against its established snapshot. This does not revive a revoked token or authorize a later request. This read-only snapshot must not be reused by submission, which takes the user lock and rechecks fresh token state as specified in its own API review.
- Visible consents must be ACTIVE, effective_at <= now, not expired (expired_at IS NULL or expired_at > now), and reference an ACTIVE consent type. A consent with an inactive/locked/archived/deleted type is hidden even if the consent itself is ACTIVE. Required means c.is_required, not a type default.
- Select the canonical ACTIVE evidence row for (userId, consentId, current consentVersion): newest created_at, then greatest id. Only that row determines pending; do not let any older accepted duplicate hide a newer rejection or unread row. Evidence for another user, another version or a non-ACTIVE row never clears pending. The same canonical rule is specified by submit-consent's separate review; older/history rows are retained.
- Required consent is complete only when the canonical current-version row has BOTH is_read=true AND result=true. Missing evidence, unread acceptance, read-only/default false and explicit rejection all remain pending. Optional consent is complete once canonical current-version is_read=true, regardless of result. An unread optional acceptance still remains pending. No evidence means pending for either kind. A new current version is pending even if an older version was accepted.
- For the non-empty pending list, collect pending consentIds and distinct consentTypeIds, then load latest ACTIVE recorded version across all versions and the type names. Both queries use typed UUID arrays and the same snapshot. Latest recorded version means newest created_at, then greatest id, including a read-only record; submittedVersion does not itself prove acceptance and may equal the current version while a required consent is still pending. Map no evidence to explicit null, never a default version or empty string.
- Keep pending results ordered by effective_at ASC, id ASC. Map each row to consentId, code, consentTypeId, consentTypeName, consentVersion, submittedVersion, consentName, consentDescription, effectiveAt, expiredAt, isRequired and body; preserve this order after merging query results. Type names are mandatory: the same snapshot's ACTIVE-type predicate and lookup guarantee the referenced name. A missing type-name mapping is an internal consistency failure, not a partly populated success. Do not silently expose hidden types to fill that name.
- If no pending rows exist, skip history/type lookups and return 200 S10000 with data.consents=[] after COMMIT. There is no 404 for an empty list. The SQL's NOT COALESCE handles missing evidence as pending; never treat NULL as acceptance. Parameters are typed bound values, not interpolated strings.
- This GET never marks a consent read, changes result/read_at or writes any history. The frontend calls submit-consent with the displayed version and isRead=true when it actually displays that consent; it adds result later on that same endpoint (Q16/Q17). Merely fetching this list creates no read evidence. Required pending does not block login or other APIs (Q9).
- Finish the read-only transaction with COMMIT before 200. On timeout before commit, ROLLBACK then 408 E90001; on unexpected pre-commit failure (including incomplete response mapping), ROLLBACK then generic 500 with no new bizCode. No pending/credential/error path inserts, updates or deletes data; no response includes stored token hashes or internal evidence ids.

#### Scenario correspondence with sequence.wsd

| Scenario                                                | Sequence behavior                                                    | HTTP             | Writes |
| ------------------------------------------------------- | -------------------------------------------------------------------- | ---------------- | ------ |
| Invalid timestamp                                       | No transaction or SQL                                                | 400 E10001       | None   |
| Missing/invalid JWT                                     | No transaction or SQL                                                | 401 E10002       | None   |
| Inactive/revoked/expired credential or user at snapshot | Credential lookup, ROLLBACK; no policy lookup                        | 401 E10002       | None   |
| Pending rows                                            | One coherent policy/evidence/type snapshot, complete mapping, COMMIT | 200 S10000       | None   |
| No pending rows                                         | Skip history/type queries, COMMIT, explicit empty array              | 200 S10000       | None   |
| Timeout / unexpected failure                            | ROLLBACK before response                                             | 408 E90001 / 500 | None   |

#### Pending truth table for a visible current consent

| Canonical evidence                             | Required | Optional |
| ---------------------------------------------- | -------- | -------- |
| None, other version/user, or non-ACTIVE only   | Pending  | Pending  |
| isRead=false, result=false                     | Pending  | Pending  |
| isRead=false, result=true                      | Pending  | Pending  |
| isRead=true, result=false (read-only/rejected) | Pending  | Complete |
| isRead=true, result=true                       | Complete | Complete |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/consent/pending HTTP/1.1
Host: www.domain.com
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/consent/pending' \
--header 'authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
--header 'timestamp: 2026-11-05T12:42:00.123Z' \
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
| 6   | timestamp      | String: TIMESTAMP | MANDATORY | Sequence Diagram | response.status.timestamp  | API Request Timestamp (Without time zone UTC) | 2026-11-05T12:42:00.123Z                 |
| 7   | status         | String            | MANDATORY | Sequence Diagram | response.status.status     | API Request Status (SUCCESS, ERROR)           | SUCCESS                                  |

### Data Object

|     | Parameter Name | Data Type                           | M/O       | Source           | Field         | Description                                                    | Example |
| --- | -------------- | ----------------------------------- | --------- | ---------------- | ------------- | -------------------------------------------------------------- | ------- |
| 1   | consents       | [Array of Consent](#consent-object) | MANDATORY | Sequence Diagram | data.consents | Pending consents, Empty array when there is no pending consent |         |

#### Consent Object

|     | Parameter Name     | Data Type         | M/O       | Source           | Field                              | Description                                                                                                 | Example                                   |
| --- | ------------------ | ----------------- | --------- | ---------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | consentId          | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentId          | Consent Id                                                                                                  | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d      |
| 2   | code               | String            | MANDATORY | Sequence Diagram | data.consents[].code               | Consent Code                                                                                                | TERMS_AND_CONDITIONS                      |
| 3   | consentTypeId      | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentTypeId      | Consent Type Id                                                                                             | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d      |
| 4   | consentTypeName    | String            | MANDATORY | Sequence Diagram | data.consents[].consentTypeName    | Consent Type Name                                                                                           | Terms and Conditions                      |
| 5   | consentVersion     | String            | MANDATORY | Sequence Diagram | data.consents[].consentVersion     | Current Consent Version                                                                                     | 1.1.0                                     |
| 6   | submittedVersion   | String            | OPTIONAL  | Sequence Diagram | data.consents[].submittedVersion   | Latest ACTIVE evidence version, including read-only display; null when none; this does not prove acceptance | 1.0.0                                     |
| 7   | consentName        | String            | MANDATORY | Sequence Diagram | data.consents[].consentName        | Consent Name                                                                                                | Terms and Conditions                      |
| 8   | consentDescription | String            | OPTIONAL  | Sequence Diagram | data.consents[].consentDescription | Consent Description                                                                                         | Terms and conditions of using the service |
| 9   | effectiveAt        | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.consents[].effectiveAt        | Consent Effective Timestamp (Without time zone UTC)                                                         | 2026-11-01T00:00:00.000Z                  |
| 10  | expiredAt          | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.consents[].expiredAt          | Consent Expired Timestamp (Without time zone UTC)                                                           | 2027-01-01T00:00:00.000Z                  |
| 11  | isRequired         | Boolean           | MANDATORY | Sequence Diagram | data.consents[].isRequired         | Consent is required to be accepted                                                                          | true                                      |
| 12  | body               | Object            | MANDATORY | Sequence Diagram | data.consents[].body               | Consent Body                                                                                                |                                           |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Pending Consent Success",
        "requestId": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "timestamp": "2026-11-05T12:42:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consents": [
            {
                "consentId": "c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
                "code": "TERMS_AND_CONDITIONS",
                "consentTypeId": "a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d",
                "consentTypeName": "Terms and Conditions",
                "consentVersion": "1.1.0",
                "submittedVersion": "1.0.0",
                "consentName": "Terms and Conditions",
                "consentDescription": "Terms and conditions of using the service",
                "effectiveAt": "2026-11-01T00:00:00.000Z",
                "expiredAt": null,
                "isRequired": true,
                "body": {
                    "title": "Terms and Conditions",
                    "content": "Terms and conditions of using the service"
                }
            },
            {
                "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "code": "MARKETING_COMMUNICATION",
                "consentTypeId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "consentTypeName": "Marketing",
                "consentVersion": "1.0.0",
                "submittedVersion": null,
                "consentName": "Marketing Communication",
                "consentDescription": "Receive promotions and news",
                "effectiveAt": "2026-11-01T00:00:00.000Z",
                "expiredAt": "2027-01-01T00:00:00.000Z",
                "isRequired": false,
                "body": {
                    "title": "Marketing Communication",
                    "content": "Receive promotions and news"
                }
            }
        ]
    }
}
```

#### Success - No Pending Consent

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Pending Consent Success",
        "requestId": "req-9a7b3c5d-6e8f-4a0b-c2d4-5e6f7a8b9c0d",
        "timestamp": "2026-11-05T12:49:00.123Z",
        "status": "SUCCESS"
    },
    "data": {
        "consents": []
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
        "bizMessage": "Timestamp is a required header.",
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
        "requestId": "req-pending-review",
        "timestamp": "2026-11-07T12:00:00.123Z",
        "status": "ERROR"
    }
}
```

---

## Database Relations

All SELECTs share one read-only REPEATABLE READ snapshot. The pending statement tests type and canonical evidence in the same SQL; later history/name lookups use its pending id sets. Every parameter is bound with its real UUID/array/byte/timestamp type.

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

### Table: [consent.t_consent](../../../schema/consent/t_consent.md)

#### QUERY - Get pending consents

```SQL
SELECT
    c.id as consent_id,
    c.code,
    c.consent_type_id,
    c.consent_version,
    c.consent_name,
    c.consent_description,
    c.effective_at,
    c.expired_at,
    c.is_required,
    c.body
FROM consent.t_consent c
WHERE c.row_status = 'ACTIVE'
AND c.effective_at <= '<sequence.now>'
AND (c.expired_at IS NULL OR c.expired_at > '<sequence.now>')
AND EXISTS (
    SELECT 1
    FROM consent.m_consent_type ct
    WHERE ct.id = c.consent_type_id
    AND ct.row_status = 'ACTIVE'
)
AND NOT COALESCE((
    SELECT uc.is_read AND (NOT c.is_required OR uc.result)
    FROM authen.t_user_consent uc
    WHERE uc.user_id = '<sequence.userId>'
    AND uc.consent_id = c.id
    AND uc.consent_version = c.consent_version
    AND uc.row_status = 'ACTIVE'
    ORDER BY uc.created_at DESC, uc.id DESC
    LIMIT 1
), FALSE)
ORDER BY c.effective_at, c.id
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### QUERY - Get latest submitted version

```SQL
SELECT DISTINCT ON (uc.consent_id)
    uc.consent_id,
    uc.consent_version as submitted_version
FROM authen.t_user_consent uc
WHERE uc.user_id = '<sequence.userId>'
AND uc.consent_id = ANY ('<sequence.consentIds>'::UUID[])
AND uc.row_status = 'ACTIVE'
ORDER BY uc.consent_id, uc.created_at DESC, uc.id DESC
```

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Get consent type

```SQL
SELECT
    ct.id as consent_type_id,
    ct.name as consent_type_name
FROM consent.m_consent_type ct
WHERE ct.id = ANY ('<sequence.consentTypeIds>'::UUID[])
AND ct.row_status = 'ACTIVE'
ORDER BY ct.id
```
