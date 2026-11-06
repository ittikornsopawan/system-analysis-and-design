# [GET]: v1/consent/active

| Title       | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| Name        | Inquiry Active Consent API                                                                      |
| Method      | GET                                                                                             |
| Endpoint    | v{version}/consent/active                                                                       |
| Version     | 1                                                                                               |
| Description | Inquiry the list of consents that are currently active, which are effective and not yet expired |

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

|     | Parameter Name | Data Type | M/O       | Description       | Example                                  |
| --- | -------------- | --------- | --------- | ----------------- | ---------------------------------------- |
| 1   | timestamp      | DateTime  | MANDATORY | Request timestamp | 2026-11-05T12:42:00.123Z                 |
| 2   | requestId      | String    | OPTIONAL  | API Request Id    | req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d |

## Example Request

### HTTP Request

```HTTP
GET /api-dev/v1/consent/active HTTP/1.1
Host: www.domain.com
timestamp: 2026-11-05T12:42:00.123Z
requestId: req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### cUrl Request

```JSON
curl --location --request GET 'https://www.domain.com/api-dev/v1/consent/active' \
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

|     | Parameter Name | Data Type                           | M/O       | Source           | Field         | Description                                                  | Example |
| --- | -------------- | ----------------------------------- | --------- | ---------------- | ------------- | ------------------------------------------------------------ | ------- |
| 1   | consents       | [Array of Consent](#consent-object) | MANDATORY | Sequence Diagram | data.consents | Active consents, Empty array when there is no active consent |         |

#### Consent Object

|     | Parameter Name     | Data Type         | M/O       | Source           | Field                              | Description                                         | Example                                   |
| --- | ------------------ | ----------------- | --------- | ---------------- | ---------------------------------- | --------------------------------------------------- | ----------------------------------------- |
| 1   | consentId          | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentId          | Consent Id                                          | c1a2b3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d      |
| 2   | code               | String            | MANDATORY | Sequence Diagram | data.consents[].code               | Consent Code                                        | TERMS_AND_CONDITIONS                      |
| 3   | consentTypeId      | String: UUID      | MANDATORY | Sequence Diagram | data.consents[].consentTypeId      | Consent Type Id                                     | a7b8c9d0-1e2f-4a3b-8c4d-5e6f7a8b9c0d      |
| 4   | consentTypeName    | String            | MANDATORY | Sequence Diagram | data.consents[].consentTypeName    | Consent Type Name                                   | Terms and Conditions                      |
| 5   | consentVersion     | String            | MANDATORY | Sequence Diagram | data.consents[].consentVersion     | Consent Version                                     | 1.0.0                                     |
| 6   | consentName        | String            | MANDATORY | Sequence Diagram | data.consents[].consentName        | Consent Name                                        | Terms and Conditions                      |
| 7   | consentDescription | String            | OPTIONAL  | Sequence Diagram | data.consents[].consentDescription | Consent Description                                 | Terms and conditions of using the service |
| 8   | effectiveAt        | String: TIMESTAMP | MANDATORY | Sequence Diagram | data.consents[].effectiveAt        | Consent Effective Timestamp (Without time zone UTC) | 2026-01-01T00:00:00.000Z                  |
| 9   | expiredAt          | String: TIMESTAMP | OPTIONAL  | Sequence Diagram | data.consents[].expiredAt          | Consent Expired Timestamp (Without time zone UTC)   | 2027-01-01T00:00:00.000Z                  |
| 10  | isRequired         | Boolean           | MANDATORY | Sequence Diagram | data.consents[].isRequired         | Consent is required to be accepted                  | true                                      |
| 11  | body               | Object            | MANDATORY | Sequence Diagram | data.consents[].body               | Consent Body                                        |                                           |

### Example Response Parameters

#### Success

```JSON
{
    "status": {
        "code": 200,
        "message": "Ok",
        "bizCode": "S10000",
        "bizMessage": "Inquiry Active Consent Success",
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
                "consentVersion": "1.0.0",
                "consentName": "Terms and Conditions",
                "consentDescription": "Terms and conditions of using the service",
                "effectiveAt": "2026-01-01T00:00:00.000Z",
                "expiredAt": null,
                "isRequired": true,
                "body": {
                    "title": "Terms and Conditions",
                    "content": "By using this service, you agree to the following terms and conditions..."
                }
            },
            {
                "consentId": "d2b3c4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
                "code": "MARKETING_COMMUNICATION",
                "consentTypeId": "b8c9d0e1-2f3a-4b4c-9d5e-6f7a8b9c0d1e",
                "consentTypeName": "Marketing",
                "consentVersion": "1.0.0",
                "consentName": "Marketing Communication",
                "consentDescription": "Receive promotions and news",
                "effectiveAt": "2026-01-01T00:00:00.000Z",
                "expiredAt": "2027-01-01T00:00:00.000Z",
                "isRequired": false,
                "body": {
                    "title": "Marketing Communication",
                    "content": "I agree to receive promotions and news..."
                }
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
        "bizMessage": "Timestamp is a required header.",
        "requestId": "req-400a1b2c-3d4e-5f6a-7b8c-9d0e1f2a3b4c",
        "timestamp": "2026-11-05T12:43:45.123Z",
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

#### QUERY - Get active consents

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
ORDER BY c.effective_at
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
