# [<api-method>]: <api-endpoint>

| Title       | Description       |
| ----------- | ----------------- |
| Name        | <api-name>        |
| Method      | <api-method>      |
| Endpoint    | <api-endpoint>    |
| Description | <api-description> |

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

|              | Parameter Name | Data Type   | M/O                   | Description             | Example             |
| ------------ | -------------- | ----------- | --------------------- | ----------------------- | ------------------- |
| <running-no> | <parameter>    | <data-type> | <MANDATORY, OPTIONAL> | <parameter-description> | <parameter-example> |

### Path Parameters

|              | Parameter Name | Data Type   | M/O                   | Description             | Example             |
| ------------ | -------------- | ----------- | --------------------- | ----------------------- | ------------------- |
| <running-no> | <parameter>    | <data-type> | <MANDATORY, OPTIONAL> | <parameter-description> | <parameter-example> |

### Query Parameters

|              | Parameter Name | Data Type   | M/O                   | Description             | Example             |
| ------------ | -------------- | ----------- | --------------------- | ----------------------- | ------------------- |
| <running-no> | <parameter>    | <data-type> | <MANDATORY, OPTIONAL> | <parameter-description> | <parameter-example> |

### Body Parameters

|              | Parameter Name | Data Type   | M/O                   | Description             | Example             |
| ------------ | -------------- | ----------- | --------------------- | ----------------------- | ------------------- |
| <running-no> | <parameter>    | <data-type> | <MANDATORY, OPTIONAL> | <parameter-description> | <parameter-example> |

#### Example Body Parameters

```JSON
```

## Example Request

### HTTP Request

```HTTP
<http request>
```

### cUrl Request

```JSON
<curl>
```

---

## Response Parameters

|     | Parameter Name | Data Type                          | M/O       | Source           | Field           | Description     | Example |
| --- | -------------- | ---------------------------------- | --------- | ---------------- | --------------- | --------------- | ------- |
| 1   | status         | [Object of Status](#status-object) | MANDATORY | Sequence Diagram | response.status | Response Status |         |
| 2   | data           | [Data of Status](#data-object)     | OPTIONAL  | Sequence Diagram | response.data   | Response Data   |         |

### Status Object

|     | Parameter Name | Data Type | M/O       | Source           | Field                      | Description                      | Example |
| --- | -------------- | --------- | --------- | ---------------- | -------------------------- | -------------------------------- | ------- |
| 1   | code           | Numeric   | MANDATORY | Sequence Diagram | response.status.code       | HTTP Status Code                 | 200     |
| 2   | Message        | String    | MANDATORY | Sequence Diagram | response.status.message    | HTTP Status Message              | Ok      |
| 3   | bizCode        | String    | OPTIONAL  | Sequence Diagram | response.status.bizCode    | Business Code Success or Fail    | S10000  |
| 4   | bizMessage     | String    | OPTIONAL  | Sequence Diagram | response.status.bizMessage | Business Message Success or Fail | Success |

### Data Object

|              | Parameter Name   | Data Type   | M/O                   | Source   | Field   | Description   | Example   |
| ------------ | ---------------- | ----------- | --------------------- | -------- | ------- | ------------- | --------- |
| <running-no> | <parameter-name> | <data-type> | <MANDATORY, OPTIONAL> | <source> | <field> | <description> | <example> |

### Example Response Parameters

#### Success

```JSON
{

}
```

#### Fail

```JSON
{

}
```

---

## Database Relations

### Table: <table-name-1>

#### QUERY

```SQL
```

#### INSERT

```SQL
```

#### UPDATE

```SQL
```

#### DELETE

```SQL
```

### Table: <table-name-2>

#### QUERY

```SQL
```

#### INSERT

```SQL
```

#### UPDATE

```SQL
```

#### DELETE

```SQL
```

---

## External Services

### API: <external-api-1-name> - <external-api-1-endpoint>

#### Request Parameters

|              | Parameter Name   | Data Type   | M/O                   | Source   | Field   | Description   | Example   |
| ------------ | ---------------- | ----------- | --------------------- | -------- | ------- | ------------- | --------- |
| <running-no> | <parameter-name> | <data-type> | <MANDATORY, OPTIONAL> | <source> | <field> | <description> | <example> |

#### Request Example

```HTTP
<http-request>
```

#### Response Parameters

|              | Parameter Name   | Data Type   | M/O                   | Description   | Example   |
| ------------ | ---------------- | ----------- | --------------------- | ------------- | --------- |
| <running-no> | <parameter-name> | <data-type> | <MANDATORY, OPTIONAL> | <description> | <example> |

#### Example Response Parameters

```JSON
<example-response-parameters>
```
