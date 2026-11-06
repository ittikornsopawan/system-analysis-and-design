# [GET]: v1/consent/pending

| Title       | Description                                                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name        | Inquiry Pending Consent API                                                                                                                                   |
| Method      | GET                                                                                                                                                           |
| Endpoint    | v{version}/consent/pending                                                                                                                                    |
| Version     | 1                                                                                                                                                             |
| Description | Inquiry the list of active consents that the user has not read or submitted for the current version, such as a consent that has been updated to a new version |

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

|     | Parameter Name     | Data Type         | M/O       | Source           | Field                              | Description                                                                                | Example                                   |
| --- | ------------------ | ----------------- | --------- | ---------------- | ---------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------- |
| 1   | consentId          | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentId          | Consent Id                                                                                 | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d      |
| 2   | code               | String            | MANDATORY | Sequence Diagram | data.consents[].code               | Consent Code                                                                               | TERMS_AND_CONDITIONS                      |
| 3   | consentTypeId      | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentTypeId      | Consent Type Id                                                                            | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d      |
| 4   | consentTypeName    | String            | MANDATORY | Sequence Diagram | data.consents[].consentTypeName    | Consent Type Name                                                                          | Terms and Conditions                      |
| 5   | consentVersion     | String            | MANDATORY | Sequence Diagram | data.consents[].consentVersion     | Current Consent Version                                                                    | 1.1.0                                     |
| 6   | submittedVersion   | String            | OPTIONAL  | Sequence Diagram | data.consents[].submittedVersion   | Latest Consent Version that the user has submitted, Null when the user has never submitted | 1.0.0                                     |
| 7   | consentName        | String            | MANDATORY | Sequence Diagram | data.consents[].consentName        | Consent Name                                                                               | Terms and Conditions                      |
| 8   | consentDescription | String            | OPTIONAL  | Sequence Diagram | data.consents[].consentDescription | Consent Description                                                                        | Terms and conditions of using the service |
| 9   | effectiveAt        | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.consents[].effectiveAt        | Consent Effective Timestamp (Without time zone UTC)                                        | 2026-11-01T00:00:00.000Z                  |
| 10  | expiredAt          | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.consents[].expiredAt          | Consent Expired Timestamp (Without time zone UTC)                                          | 2027-01-01T00:00:00.000Z                  |
| 11  | isRequired         | Boolean           | MANDATORY | Sequence Diagram | data.consents[].isRequired         | Consent is required to be accepted                                                         | true                                      |
| 12  | body               | Object            | MANDATORY | Sequence Diagram | data.consents[].body               | Consent Body                                                                               |                                           |

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

---

## Database Relations

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
AND c.effective_at <= NOW() AT TIME ZONE 'UTC'
AND (c.expired_at IS NULL OR c.expired_at > NOW() AT TIME ZONE 'UTC')
AND NOT EXISTS (
    SELECT 1
    FROM authen.t_user_consent uc
    WHERE uc.user_id = '<sequence.userId>'
    AND uc.consent_id = c.id
    AND uc.consent_version = c.consent_version
    AND uc.is_read = TRUE
    AND uc.row_status = 'ACTIVE'
)
ORDER BY c.effective_at
```

### Table: [authen.t_user_consent](../../../schema/authen/t_user_consent.md)

#### QUERY - Get latest submitted version

```SQL
SELECT DISTINCT ON (uc.consent_id)
    uc.consent_id,
    uc.consent_version as submitted_version
FROM authen.t_user_consent uc
WHERE uc.user_id = '<sequence.userId>'
AND uc.consent_id IN ('<sequence.consentIds>')
AND uc.row_status = 'ACTIVE'
ORDER BY uc.consent_id, uc.created_at DESC
```

### Table: [consent.m_consent_type](../../../schema/consent/m_consent_type.md)

#### QUERY - Get consent type

```SQL
SELECT
    ct.id as consent_type_id,
    ct.name as consent_type_name
FROM consent.m_consent_type ct
WHERE ct.id IN ('<sequence.consentTypeIds>')
AND ct.row_status = 'ACTIVE'
```
