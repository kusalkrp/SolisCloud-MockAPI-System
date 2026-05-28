# SolisCloud Platform API Document V2.0

Comprehensive API reference documentation for the Ginlong (Solis) Technologies Cloud Platform (V2.0). All interface encryption, requests, device operations, plant operations, and code examples are detailed below.

---

## Table of Contents
1. [Global Description & Authentication](#1-global-description--authentication)
   - [Authentication Header Protocol](#authentication-header-protocol)
   - [Content-MD5 Calculation](#content-md5-calculation)
   - [Signature (Sign) Calculation](#signature-sign-calculation)
   - [Date Header Specification](#date-header-specification)
   - [Standard Response Format](#standard-response-format)
   - [Signature Implementation Examples](#signature-implementation-examples)
2. [Device Interfaces](#2-device-interfaces)
   - [3.1 Obtain Inverter List Under Account](#31-obtain-inverter-list-under-account)
   - [3.2 Obtain Details of a Single Inverter](#32-obtain-details-of-a-single-inverter)
   - [3.3 Obtain Details of Multiple Inverters](#33-obtain-details-of-multiple-inverters)
   - [3.4 Obtain Real-Time Data of a Single Inverter (Day)](#34-obtain-real-time-data-of-a-single-inverter-day)
   - [3.5 Obtain Daily Data of a Single Inverter (Month)](#35-obtain-daily-data-of-a-single-inverter-month)
   - [3.6 Obtain Monthly Data of a Single Inverter (Year)](#36-obtain-monthly-data-of-a-single-inverter-year)
   - [3.7 Obtain Annual Data of a Single Inverter](#37-obtain-annual-data-of-a-single-inverter)
   - [3.8 Obtain Quality Assurance Data for Multiple Inverters](#38-obtain-quality-assurance-data-for-multiple-inverters)
   - [3.9 Obtain Device Alarm List Under Account](#39-obtain-device-alarm-list-under-account)
   - [3.10 Obtain Collector List Under Account](#310-obtain-collector-list-under-account)
   - [3.11 Obtain Details of a Single Collector](#311-obtain-details-of-a-single-collector)
   - [3.12 Obtain Single Collector Signal Values (Day Timeline)](#312-obtain-single-collector-signal-values-day-timeline)
   - [3.13 Obtain EPM List Under Account](#313-obtain-epm-list-under-account)
   - [3.14 Obtain Details of a Single EPM](#314-obtain-details-of-a-single-epm)
   - [3.15 Obtain Real-Time Data of a Single EPM (Day)](#315-obtain-real-time-data-of-a-single-epm-day)
   - [3.16 Obtain Daily Data of a Single EPM (Month)](#316-obtain-daily-data-of-a-single-epm-month)
   - [3.17 Obtain Monthly Data of a Single EPM (Year)](#317-obtain-monthly-data-of-a-single-epm-year)
   - [3.18 Obtain Annual Data for a Single EPM](#318-obtain-annual-data-for-a-single-epm)
   - [3.19 Obtain Meteorological Instruments List Under Account](#319-obtain-meteorological-instruments-list-under-account)
   - [3.20 Obtain Details of a Single Meteorological Instrument](#320-obtain-details-of-a-single-meteorological-instrument)
3. [Plant Interfaces](#3-plant-interfaces)
   - [4.1 Obtain Power Station List Under Account](#41-obtain-power-station-list-under-account)
   - [4.2 Obtain Details of Individual Power Station](#42-obtain-details-of-individual-power-station)
   - [4.3 Obtain Details of Multiple Power Stations](#43-obtain-details-of-multiple-power-stations)
   - [4.4 Obtain Real-Time Data of Multiple Power Stations (Day)](#44-obtain-real-time-data-of-multiple-power-stations-day)
   - [4.5 Obtain Daily Data of Multiple Power Stations (Month)](#45-obtain-daily-data-of-multiple-power-stations-month)
   - [4.6 Obtain Annual Data from Multiple Power Stations](#46-obtain-annual-data-from-multiple-power-stations)
   - [4.7 Obtain Real-Time Data of a Single Power Station (Day)](#47-obtain-real-time-data-of-a-single-power-station-day)
   - [4.8 Obtain Daily Data of a Single Power Station (Month)](#48-obtain-daily-data-of-a-single-power-station-month)
   - [4.9 Obtain Monthly Data of a Single Power Plant (Year)](#49-obtain-monthly-data-of-a-single-power-plant-year)
   - [4.10 Obtain Annual Data of a Power Plant](#410-obtain-annual-data-of-a-power-plant)
   - [4.11 Create a New Power Station](#411-create-a-new-power-station)
   - [4.12 Modify Power Station Information](#412-modify-power-station-information)
   - [4.13 Bind a New Collector to Power Station](#413-bind-a-new-collector-to-power-station)
   - [4.14 Unbind Collector from Power Station](#414-unbind-collector-from-power-station)
   - [4.15 Bind Inverter to Power Plant](#415-bind-inverter-to-power-plant)
4. [Appendices](#4-appendices)
   - [Appendix 1: Failure Error Codes](#appendix-1-failure-error-codes)
   - [Appendix 2: Types of Power Plants](#appendix-2-types-of-power-plants)
   - [Appendix 3: Types of Inverter Meters](#appendix-3-types-of-inverter-meters)

---

## 1. Global Description & Authentication

### Core Guidelines
1. **Protocol & Security**: All interface data encryption and communication are based on the **HTTPS** protocol.
2. **Frequency Updates**: The update cycle for all data points is **5 minutes**.
3. **HTTP Verb**: All request methods MUST be **POST**.
4. **Content-Type**: Requests must utilize the header `Content-Type: application/json;charset=UTF-8`.
5. **JSON Returns**: All response payloads are in standard JSON format.
6. **Required Headers**: Every request must attach the following headers:
   - `Content-MD5`
   - `Content-Type`
   - `Date`
   - `Authorization`
7. **Units**: Measurements returned (Power, Energy, Voltage, Current, Frequency) must be mapped alongside their corresponding string unit fields (e.g. `powerStr`, `etodayStr`, `pacStr`).

---

### Authentication Header Protocol

To access the API endpoints, requests must be authorized using your **API ID** and **API Secret Key**, obtainable under the SolisCloud Portal (`Account -> Basic Settings -> API Management`).

#### Headers Structure
```http
POST /v1/api/inverterList HTTP/1.1
Host: www.soliscloud.com:13333
Content-MD5: kxdxk7rbAsrzSIWgEwhH4w==
Content-Type: application/json;charset=UTF-8
Date: Fri, 26 Jul 2019 06:00:46 GMT
Authorization: API 1300386381676644416:nBYQWeuzy3Y+gp67BN8zXTmvSDk=
```

---

### Content-MD5 Calculation
The `Content-MD5` value is used to verify request body integrity:
1. Compute the MD5 hash of the request body string (UTF-8 encoding).
2. Convert the resulting MD5 digest into a 128-bit raw binary byte array.
3. Encode the binary array using standard Base64 representation.

*Example*: Request body `{"pageNo":1,"pageSize":10}` produces the `Content-MD5` value `kxdxk7rbAsrzSIWgEwhH4w==`.

---

### Signature (Sign) Calculation
The digital signature prevents tampering and authorizes credentials. It uses HMAC-SHA1 encryption.

$$\text{Signature} = \text{Base64}\Big(\text{HmacSHA1}\big(\text{API Secret},\, \text{StringToSign}\big)\Big)$$

Where **StringToSign** is formed by joining request metadata with newline delimiters (`\n`):

```text
POST
{Content-MD5}\n
{Content-Type}\n
{Date}\n
{CanonicalizedResource}
```

*Important Components:*
- **Method**: Always `POST`
- **Content-MD5**: The Base64 string calculated from the body.
- **Content-Type**: Fixed value `application/json;charset=UTF-8`
- **Date**: Exact value sent in request headers (e.g., `Fri, 26 Jul 2019 06:00:46 GMT`).
- **CanonicalizedResource**: The specific API request path (e.g., `/v1/api/inverterList`).

**Authorization Header Format:**
`Authorization: API {apiId}:{Signature}`

---

### Date Header Specification
- **Format**: `EEE, d MMM yyyy HH:mm:ss 'GMT'` in the GMT timezone (e.g., `Fri, 26 Jul 2019 06:00:46 GMT`).
- **Validation**: Request date headers cannot deviate from the server's time by more than **$\pm$ 15 minutes**; otherwise, the gateway returns a timestamp validation error.

---

### Standard Response Format
All API payloads return a JSON wrapper structure:
```json
{
  "success": true,
  "code": "0",
  "msg": "success",
  "data": {}
}
```
- **success**: `true` on successful gateway processing; `false` on failure.
- **code**: `"0"` denotes successful functional outcome. Other numeric/alphanumeric strings refer to failure details (see [Appendix 1](#appendix-1-failure-error-codes)).
- **msg**: Verbal status description or exception logs.
- **data**: Generic response payload container (maps to object or array depending on the interface).

---

### Signature Implementation Examples

> [!TIP]
> Ensure all newline characters in the signing buffer are explicitly represented by `\n` without additional carriage returns (`\r`).

#### Python 3 Example
```python
import base64
import hashlib
import hmac
import datetime

def generate_solis_headers(api_id, api_secret, path, body_str):
    # 1. Content-MD5
    md5_hash = hashlib.md5(body_str.encode('utf-8')).digest()
    content_md5 = base64.b64encode(md5_hash).decode('utf-8')
    
    # 2. Date in GMT
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 3. String to Sign
    content_type = "application/json;charset=UTF-8"
    string_to_sign = f"POST\n{content_md5}\n{content_type}\n{date_str}\n{path}"
    
    # 4. Signature
    hmac_key = api_secret.encode('utf-8')
    signature = hmac.new(hmac_key, string_to_sign.encode('utf-8'), hashlib.sha1).digest()
    sign_base64 = base64.b64encode(signature).decode('utf-8')
    
    headers = {
        "Content-MD5": content_md5,
        "Content-Type": content_type,
        "Date": date_str,
        "Authorization": f"API {api_id}:{sign_base64}"
    }
    return headers
```

#### Node.js / JavaScript Example
```javascript
const crypto = require('crypto');

function getSolisHeaders(apiId, apiSecret, path, bodyStr) {
    const contentMd5 = crypto.createHash('md5').update(bodyStr, 'utf8').digest('base64');
    const dateStr = new Date().toUTCString();
    const contentType = 'application/json;charset=UTF-8';
    
    const stringToSign = `POST\n${contentMd5}\n${contentType}\n${dateStr}\n${path}`;
    const sign = crypto.createHmac('sha1', apiSecret).update(stringToSign, 'utf8').digest('base64');
    
    return {
        'Content-MD5': contentMd5,
        'Content-Type': contentType,
        'Date': dateStr,
        'Authorization': `API ${apiId}:${sign}`
    };
}
```

---

## 2. Device Interfaces

### 3.1 Obtain Inverter List Under Account
Returns a paginated list of all grid-tied and storage inverters registered under the client profile.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | String | **Y** | Page index number to query (starts at `1`). |
| `pageSize` | String | **Y** | Records count per page (Default `20`, Max `100`). |
| `stationId` | Integer | N | Query inverters tied to a specific power station ID. |
| `nmiCode` | String | N | Query inverters matching a specific NMI code. |

#### Return parameters [Body -> `data -> page -> records`]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Integer | N | Unique Inverter Identification ID. |
| `sn` | String | N | Serial number (SN) of the inverter. |
| `stationId` | Integer | N | Associated Station ID. |
| `stationName` | String | N | Power plant designation. |
| `userId` | Integer | N | Owner identity code. |
| `power` | String | N | Configured system capacity. |
| `powerStr` | String | N | Capacity units (e.g. `kWp`). |
| `etoday` | Number | N | Accumulative energy generated today. |
| `etoday1` | Number | N | Original unrounded daily generation value. |
| `etodayStr` | String | N | Today's generation unit (typically `kWh`). |
| `etotal` | Number | N | Lifetime generated energy. |
| `etotal1` | Number | N | Original unrounded lifetime generation value. |
| `etotalStr` | String | N | Lifetime generation unit (typically `MWh`). |
| `fullHour` | Number | N | Equivalent full generation hours (etoday / rated power). |
| `pac` | Number | N | Current active power output. |
| `pacStr` | String | N | Active power output unit (typically `kW`). |
| `state` | Integer | N | Operation status: `1` = Online, `2` = Offline, `3` = Fault Alarm. |
| `dataTimestamp` | Integer | N | System UTC+8 data refresh epoch millisecond timestamp. |
| `collectorSn` | String | N | Associated datalogger serial number. |
| `productModel` | String | N | Inverter type: `1` = Grid-tied, `2` = Hybrid/Storage. |
| `dcInputType` | Integer | N | DC String configurations: Actual channels = `value + 1`. |
| `acOutputType` | Integer | N | Output Phase type: `0` = Single Phase, `1` = Three Phase. |
| `series` | String | N | Device series model. |
| `name` | String | N | Friendly device label. |
| `addr` | String | N | Physical power station address. |
| `collectorState` | Integer | N | Datalogger Status: `1` = Online, `2` = Offline. |
| `stateExceptionFlag`| Integer | N | Abnormal disconnection tracking: `0` = Normal, `1` = Abnormal. |
| `totalFullHour` | Number | N | Total cumulative full generation hours. |
| `inverterMeterModel`| Integer | N | Inverter meter classification profile (see [Appendix 3](#appendix-3-types-of-inverter-meters)). |
| `createDate` | Integer | N | Creation timestamp. |
| `updateShelfEndTime`| Integer | N | Warranty expiration epoch timestamp. |

#### Request Example
```json
{
  "pageNo": "1",
  "pageSize": "10",
  "stationId": "1298491919448631809",
  "nmiCode": "41028459350"
}
```

#### Response Example
```json
{
  "success": true,
  "code": "0",
  "msg": "success",
  "data": {
    "inverterStatusVo": {
      "all": 8,
      "normal": 0,
      "fault": 0,
      "offline": 8,
      "mppt": 0
    },
    "page": {
      "records": [
        {
          "id": "1308675217944611083",
          "sn": "120B40198150131",
          "model": "b4",
          "collectorSn": "404314859",
          "productModel": "b4",
          "nationalStandards": "0",
          "inverterSoftwareVersion": "000000",
          "inverterSoftwareVersion2": "000000",
          "dcInputType": 3,
          "acOutputType": 1,
          "stationId": "1298491919448631809",
          "tag": "YingZhen",
          "rs485ComAddr": "101",
          "simFlowState": -5,
          "power": 8.000,
          "powerStr": "kW",
          "pac": 5.025,
          "pacStr": "kW",
          "state": 1,
          "stateExceptionFlag": 0,
          "fullHour": 4.38,
          "totalFullHour": 4549.63,
          "timeZone": -9.00,
          "timeZoneStr": "UTC-9:00",
          "dataTimestamp": "1687846773000",
          "dataTimestampStr": "2023-06-26 22:19:33 (UTC-9:00)",
          "etotal": 36.397,
          "etoday": 27.800,
          "etotalStr": "MWh",
          "etodayStr": "kWh"
        }
      ],
      "total": 1,
      "size": 10,
      "current": 1,
      "pages": 1
    }
  }
}
```

---

### 3.2 Obtain Details of a Single Inverter
Returns detailed real-time telemetries, DC strings voltages/currents, AC grid phases, temperatures, and battery storage diagnostics.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterDetail`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Integer | **Y\*** | Database Unique Inverter ID. |
| `sn` | String | **Y\*** | Physical Inverter Serial Number. |

> [!IMPORTANT]
> Both `id` and `sn` cannot be empty at the same time. Provide at least one valid parameter to query.

#### Return parameters [Body -> `data`]
This payload returns a comprehensive telemetric map. Key telemetry parameters include:
- **String Inputs**: `uPv1` to `uPv32` (Voltages in V), `iPv1` to `iPv32` (Currents in A), `pow1` to `pow32` (DC string active power in W).
- **AC Phases**: `uAc1`, `uAc2`, `uAc3` (Phase Voltages), `iAc1`, `iAc2`, `iAc3` (Phase Currents).
- **Hybrid Storage Metrics**:
  - `batteryCapacitySoc`: Battery state of charge percentage (%).
  - `batteryHealthSoh`: Battery health state percentage (%).
  - `batteryPower`: Active charging/discharging power (kW).
  - `batteryVoltage`: Battery pack voltage.
  - `bstteryCurrent`: Battery current.
  - `batteryTodayChargeEnergy` / `batteryTodayDischargeEnergy`: Daily storage metrics.
  - `gridPurchasedTodayEnergy` / `gridSellTodayEnergy`: Daily grid exchanges.
  - `homeLoadTodayEnergy`: Local residential consumption tracking today.
- **Temperatures**: `inverterTemperature` (Inverter internal chassis temperature).

#### Request Example
```json
{
  "id": "1308675217944611083",
  "sn": "120B40198150131"
}
```

---

### 3.3 Obtain Details of Multiple Inverters
Enables batch telemetry queries for multiple inverter stations under the user profile.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterDetailList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | String | N | Page query index (Default `1`). |
| `pageSize` | Integer | **Y** | Maximum entries count per page (Max `100`). |

#### Return parameters [Body -> `data -> records`]
Returns a list of inverter telemetries matching the detailed structure described in Section [3.2](#32-obtain-details-of-a-single-inverter).

---

### 3.4 Obtain Real-Time Data of a Single Inverter (Day)
Provides historical 5-minute interval telemetric data points for a single inverter on a designated day.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterDay`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Integer | N | Inverter Database ID (Conditional requirement). |
| `sn` | String | N | Inverter Serial Number (Conditional requirement). |
| `time` | String | **Y** | The queried date, format: `yyyy-MM-dd`. |
| `money` | String | **Y** | Financial currency identifier (e.g. `EUR`, `CNY`, `USD`). |
| `timeZone` | Integer | **Y** | Target offset location timezone index (e.g. `8` for UTC+8). |

#### Request Example
```json
{
  "id": "1308675217944611083",
  "sn": "120B40198150131",
  "money": "CNY",
  "time": "2023-06-27",
  "timeZone": "8"
}
```

#### Response Example
```json
{
  "success": true,
  "code": "0",
  "msg": "success",
  "data": [
    {
      "dataTimestamp": "1687813291000",
      "timeStr": "2023-06-27 05:01:31",
      "acOutputType": 1,
      "dcInputType": 3,
      "state": 1,
      "time": "05:01:31",
      "pac": 74.000,
      "pacStr": "kW",
      "pacPec": "0.001",
      "eToday": 0.000,
      "eTotal": 36362.000,
      "uPv1": 245.3,
      "iPv1": 0.1,
      "uPv2": 243.0,
      "iPv2": 0.1,
      "uPv3": 244.7
    }
  ]
}
```

---

### 3.5 Obtain Daily Data of a Single Inverter (Month)
Returns daily generation totals and basic battery metrics for a selected month.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterMonth`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Number | N | Inverter Database ID. |
| `sn` | String | N | Inverter Serial Number. |
| `month` | String | **Y** | Target query month, format: `yyyy-MM` (e.g. `2023-06`). |
| `money` | String | **Y** | Financial currency lookup (e.g. `AUD`). |

#### Return parameters [Body -> `data`]
Returns daily records detailing generation (`energy`), financial savings (`money`), battery energy cycles (`batteryChargeEnergy`, `batteryDischargeEnergy`), and grid feeds (`gridPurchasedEnergy`, `gridSellEnergy`).

---

### 3.6 Obtain Monthly Data of a Single Inverter (Year)
Provides monthly production totals for a specific calendar year.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterYear`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Number | N | Inverter Database ID. |
| `sn` | String | N | Inverter Serial Number. |
| `year` | String | **Y** | Target year, format: `yyyy` (e.g. `2023`). |
| `money` | String | **Y** | Currency code. |

---

### 3.7 Obtain Annual Data of a Single Inverter
Provides historical yearly generation totals.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverterAll`
* **Rate Limit**: 2 requests/sec

---

### 3.8 Obtain Quality Assurance Data for Multiple Inverters
Allows queries of manufacturing warranty details and active coverage statuses in batch.

* **URL**: `https://www.soliscloud.com:13333/v1/api/inverter/shelfTime`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | Number | **Y** | Page navigation number index. |
| `pageSize` | Number | **Y** | Records limit count per page (Max `100`). |
| `sn` | String | N | Query target serial numbers. Support multiple comma-separated keys (Max `1000` SNs). |

#### Return parameters [Body -> `data -> records`]
| Parameter Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | Number | Inverter database identification. |
| `sn` | String | Serial Number verified. |
| `shelfBeginTime` | Number | Initial date start of warranty. |
| `shelfEndTime` | Number | Final expiration epoch date of warranty. |
| `shelfTime` | Number | Duration of warranty coverage period. |
| `shelfState` | Number | Warranty coverage status: `0` = Under warranty, `1` = Over/Expired. |

---

### 3.9 Obtain Device Alarm List Under Account
Lists system alerts, warning codes, emergency states, and handling recommendations.

* **URL**: `https://www.soliscloud.com:13333/v1/api/alarmList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | String | N | Target page index query. |
| `pageSize` | Integer | **Y** | Number of alarms returned (Max `100`). |
| `stationId` | Integer | N | Limit alarm search to target Station ID. |
| `alarmDeviceSn` | String | N | Filter queries for a specific inverter serial number. |
| `alarmBegIntegerime` | String | N | Query alarms since date, format: `yyyy-MM-dd`. |
| `alarmEndTime` | String | N | End date of query, format: `yyyy-MM-dd`. |
| `nmiCode` | String | N | Query alarms associated with NMI profile. |

#### Return parameters [Body -> `data -> records`]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | String | Y | Alarm record unique ID. |
| `stationId` | Long | Y | Station ID origin. |
| `stationName` | String | N | Station name. |
| `alarmDeviceSn` | String | N | Faulty inverter SN. |
| `alarmCode` | String | N | Factory error diagnostic code. |
| `alarmLevel` | String | N | Alarm severity level: `1` = Tip (Warning), `2` = General, `3` = Emergency. |
| `alarmBeginTime` | Long | N | Alarm trigger start timestamp (epoch ms). |
| `alarmEndTime` | Long | N | Alarm resolution end timestamp (epoch ms). |
| `alarmMsg` | String | N | Verbose alarm condition text. |
| `advice` | String | N | Recommended troubleshooting step. |
| `state` | String | N | Alarm resolution state: `0` = Pending, `1` = Processed, `2` = Restored. |
| `warningInfoData`| Integer | N | Sub-alarm auxiliary code. |

---

### 3.10 Obtain Collector List Under Account
Returns a list of all datalogging devices registered under your profile.

* **URL**: `https://www.soliscloud.com:13333/v1/api/collectorList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | String | **Y** | Target page index. |
| `pageSize` | String | **Y** | Page size limit. |
| `stationId` | Integer | N | Filter collectors by station ID. |
| `nmiCode` | String | N | Filter collectors by NMI. |

#### Return parameters [Body -> `data -> page -> records`]
Returns details of the dataloggers, including:
- `id` (Collector unique ID)
- `sn` (Collector serial number)
- `model` (Datalogger hardware model)
- `state` (Status: `1` = Online, `2` = Offline)
- `rssiLevel` (Signal strength category)
- `simFlowState` (SIM card data billing state)

---

### 3.11 Obtain Details of a Single Collector
Returns system telemetries and network configs for a designated datalogger.

* **URL**: `https://www.soliscloud.com:13333/v1/api/collectorDetail`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Integer | **Y\*** | Collector Unique database ID. |
| `sn` | String | **Y\*** | Collector Serial Number. |

> [!IMPORTANT]
> Both `id` and `sn` cannot be empty at the same time.

#### Return parameters [Body -> `data`]
Provides detailed collector telemetry including `lanIp`, `connectedSsid`, `maximumNumber` (maximum connected devices capacity), `actualNumber` (currently connected physical devices count), `rssiLevel`, `timeZoneStr`, and `gprsPackage`.

---

### 3.12 Obtain Single Collector Signal Values (Day Timeline)
Returns daily signal trends for troubleshooting connectivity issues.

* **URL**: `https://www.soliscloud.com:13333/v1/api/collector/day`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | **Y** | Target Collector serial number. |
| `time` | String | **Y** | The queried date, format: `yyyy-MM-dd`. |
| `timeZone` | Number | **Y** | Location timezone index offset (e.g. `8`). |

---

### 3.13 Obtain EPM List Under Account
Returns a list of all Export Power Managers (EPM) under the user profile.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epmList`
* **Rate Limit**: 2 requests/sec

---

### 3.14 Obtain Details of a Single EPM
Returns configuration metrics and software details for a designated EPM.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epmDetail`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | **Y** | Export Power Manager Serial Number. |

#### Return parameters [Body -> `data`]
Returns EPM properties including `empSoftwareVersion`, grid limits (`pLimit`, `ctRatio`), local power measurements (`pEpmTotal`, `eTotalBuy`, `eTotalSell`), and phase values (`uAc1` to `uAc3`, `iAc1` to `iAc3`, `pAc1` to `pAc3`).

---

### 3.15 Obtain Real-Time Data of a Single EPM (Day)
Provides historical 5-minute interval telemetric data points for an EPM.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epm/day`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | **Y** | EPM serial number. |
| `searchinfo` | String | **Y** | Comma-separated list of target fields to fetch (e.g., `u_ac1,u_ac2,e_total_buy,e_total_sell`). |
| `time` | String | **Y** | Query date, format: `yyyy-MM-dd`. |
| `timeZone` | number | **Y** | Target timezone index. |

---

### 3.16 Obtain Daily Data of a Single EPM (Month)
Returns daily EPM measurements for a selected month.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epm/month`
* **Rate Limit**: 2 requests/sec

---

### 3.17 Obtain Monthly Data of a Single EPM (Year)
Provides monthly EPM measurements for a specific calendar year.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epm/year`
* **Rate Limit**: 2 requests/sec

---

### 3.18 Obtain Annual Data for a Single EPM
Provides historical yearly EPM measurements.

* **URL**: `https://www.soliscloud.com:13333/v1/api/epm/all`
* **Rate Limit**: 2 requests/sec

---

### 3.19 Obtain Meteorological Instruments List Under Account
Returns a list of environmental monitoring equipment (e.g., weather stations).

* **URL**: `https://www.soliscloud.com:13333/v1/api/weatherList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | number | **Y** | Page index number query. |
| `pageSize` | number | **Y** | Page size limit. |
| `stationId` | number | N | Filter instruments by station ID. |
| `nmiCode` | String | N | Filter instruments by NMI. |

#### Return parameters [Body -> `data -> page -> records`]
| Parameter Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | number | Unique Meteorological instrument database ID. |
| `name` | String | Meteorological equipment model label. |
| `weatherModel` | String | Model type: `1` = Jinzhou Sunshine, `2` = Jinzhou Licheng. |
| `totalR` | number | Real-time Global Horizontal Irradiance ($W/m^2$). |
| `directR` | number | Direct solar radiation measurement ($W/m^2$). |
| `scatteredR` | number | Scattered solar radiation measurement ($W/m^2$). |
| `temp` | number | External Ambient Temperature. |
| `humidity` | number | Relative humidity level percentage (%RH). |
| `windSpeed` | number | Local wind speed ($m/s$). |
| `windDirection` | number | Wind direction angle degrees. |
| `rainfall` | number | Cumulative precipitation height ($mm$). |
| `pvTemp` | number | PV module backsheet temperature. |

---

### 3.20 Obtain Details of a Single Meteorological Instrument
Returns system telemetries and network configs for a designated datalogger.

* **URL**: `https://www.soliscloud.com:13333/v1/api/weatherDetail`
* **Rate Limit**: 2 requests/sec

---

## 3. Plant Interfaces

### 4.1 Obtain Power Station List Under Account
Returns a paginated list of all solar energy power stations under the user profile.

* **URL**: `https://www.soliscloud.com:13333/v1/api/userStationList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | number | **Y** | Target page index to query (starts at `1`). |
| `pageSize` | number | **Y** | Records count per page. |
| `nmiCode` | String | N | Query station matching a specific NMI profile. |

#### Return parameters [Body -> `data -> page -> records`]
| Parameter Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | number | Unique Power Station ID. |
| `stationName` | String | Station name. |
| `addr` | String | Physical address of the power station. |
| `capacity` | Number | Installed system capacity. |
| `capacityStr` | String | Capacity unit (e.g. `kWp`). |
| `dayEnergy` | Number | Cumulative energy generated today (kWh). |
| `monthEnergy` | Number | Cumulative energy generated this month. |
| `yearEnergy` | Number | Cumulative energy generated this year. |
| `allEnergy` | Number | Lifetime generated energy. |
| `dayIncome` | Number | Financial earnings generated today. |
| `allIncome` | Number | Lifetime financial earnings. |
| `synchronizationType`| number | Grid configuration type: `0` = Grid-tied, `1` = Self-use, `2` = Off-grid. |
| `stationTypeNew` | number | Power plant type index (see [Appendix 2](#appendix-2-types-of-power-plants)). |

---

### 4.2 Obtain Details of Individual Power Station
Returns detailed configurations, weather updates, financial metrics, and environmental benefits for a designated power station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationDetail`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | number | **Y\*** | Power Station database unique ID. |
| `nmiCode` | String | **Y\*** | Power station unique NMI identifier. |

> [!IMPORTANT]
> Both `id` and `nmiCode` cannot be empty at the same time.

#### Return parameters [Body -> `data`]
Returns a detailed plant configuration map including:
- **Environmental Benefits**: `powerStationAvoidedCo2` (CO2 offset in metric tons), `powerStationNumTree` (equivalent trees planted).
- **Meteorology**: `weather` (current conditions), `tmpMax` / `tmpMin` (ambient temperature range), `sunshineTim` (active sunlight hours).
- **Financial Settings**: `price` (revenue per kWh), `money` (currency type code like `AUD`, `USD`, `CNY`), `sysGridPriceList` (time-of-use tariffs configuration).

---

### 4.3 Obtain Details of Multiple Power Stations
Returns detailed configurations, weather updates, financial metrics, and environmental benefits for multiple power stations in batch.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationDetailList`
* **Rate Limit**: 2 requests/sec

---

### 4.4 Obtain Real-Time Data of Multiple Power Stations (Day)
Provides historical 5-minute interval telemetric data points for multiple power stations.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationDayEnergyList`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `pageNo` | String | N | Target page index. |
| `pageSize` | Integereger | **Y** | Records limit count (Max `100`). |
| `time` | String | **Y** | Target date to query, format: `yyyy-MM-dd`. |
| `stationIds` | String | N | Commas-separated station IDs list. |

---

### 4.5 Obtain Daily Data of Multiple Power Stations (Month)
Returns daily generation trends for multiple power stations over a selected month.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationMonthEnergyList`
* **Rate Limit**: 10 requests/sec

---

### 4.6 Obtain Annual Data from Multiple Power Stations
Provides annual production totals for multiple power stations.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationYearEnergyList`
* **Rate Limit**: 10 requests/sec

---

### 4.7 Obtain Real-Time Data of a Single Power Station (Day)
Provides historical 5-minute interval telemetric data points for a single power station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationDay`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | Integer | N | Station ID (Conditional requirement). |
| `nmiCode` | String | N | Station NMI profile (Conditional requirement). |
| `time` | String | **Y** | Target date, format: `yyyy-MM-dd`. |
| `money` | String | **Y** | Currency code. |
| `timeZone` | Integer | **Y** | Target timezone index offset (e.g. `8`). |

---

### 4.8 Obtain Daily Data of a Single Power Station (Month)
Returns daily production totals and basic battery metrics for a selected month.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationMonth`
* **Rate Limit**: 2 requests/sec

---

### 4.9 Obtain Monthly Data of a Single Power Plant (Year)
Provides monthly production totals for a specific calendar year.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationYear`
* **Rate Limit**: 2 requests/sec

---

### 4.10 Obtain Annual Data of a Power Plant
Provides historical yearly production totals.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationAll`
* **Rate Limit**: 2 requests/sec

---

### 4.11 Create a New Power Station
Enables programmatic registration of a new physical solar power plant.

* **URL**: `https://www.soliscloud.com:13333/v1/api/addStation`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `stationName` | String | **Y** | Unique Name designation for the station. |
| `capacity` | String | **Y** | Installed solar design capacity (Unit: kWp). |
| `money` | String | **Y** | Financial currency lookup key (e.g., `USD`, `CNY`). |
| `addr` | String | **Y** | Physical address of the power plant. |
| `price` | Integer | **Y** | Revenue pricing tier per kWh. |
| `inverterSn` | String | N | Inverter SN to associate during creation. |
| `collectorSn` | String | N | Collector SN to associate during creation. |
| `userId` | Integer | N | Owner identity database ID. |
| `mobile` | String | N | Owner mobile phone number string. |
| `latitude` | String | N | Geographical latitude coordinate. |
| `Integeritude` | String | N | Geographical longitude coordinate. |
| `dip` | Number | N | Array tilt angle degrees. |
| `azimuth` | Number | N | Array azimuth angle degrees. |
| `gdAreaCode` | String | N | Retrieve address code via Google Maps API. |
| `countryStr` | Integer | N | Country identifier. |
| `regionStr` | Integer | N | Region/State identifier. |
| `cityStr` | Integer | N | City location. |
| `offset` | Number | N | GMT timezone offset. |
| `module` | String | N | Total number of modules/panels. |
| `installerEmail`| String | N | Installer contact email. |
| `installerMobile`| String | N | Installer contact phone. |
| `nmiCode` | Number | N | National Metering Identifier. |

#### Return parameters [Body -> `data`]
| Parameter Name | Data Type | Description |
| :--- | :--- | :--- |
| `stationId` | Integer | Unique database ID assigned to the newly created station. |

#### Request Example
```json
{
  "stationName": "autotest22",
  "mobile": "18957465251",
  "capacity": "10",
  "longitude": "120.01144",
  "latitude": "30.320861",
  "dip": "45",
  "money": "CNY",
  "gdAreaCode": "330110",
  "country": 1,
  "region": 862,
  "city": 863
}
```

#### Response Example
```json
{
  "success": true,
  "code": "0",
  "msg": "success",
  "data": {
    "id": 123456
  }
}
```

---

### 4.12 Modify Power Station Information
Updates administrative metadata, system capacities, location fields, or financial details for an existing station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/stationUpdate`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `id` | number | N | Database Power Station ID. |
| `stationName` | String | **Y** | Updated station name designation. |
| `capacity` | String | **Y** | Updated system design capacity. |
| `price` | Number | **Y** | Updated revenue pricing tier. |
| `addr` | String | **Y** | Updated physical address. |
| `nmiCode` | String | N | NMI profile update. |

---

### 4.13 Bind a New Collector to Power Station
Binds an offline datalogging collector to an active power station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/addStationBindCollector`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | N | Datalogger Collector SN to bind. Separate multiple values with commas. |
| `stationName` | String | **Y** | Station name. |
| `capacity` | String | **Y** | System capacity (kWp). |

---

### 4.14 Unbind Collector from Power Station
Unbinds a datalogger collector from an active power station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/delCollector`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | N | Datalogger Collector SN to unbind. |
| `deleteInvert` | Integereger | **Y** | `1` = automatically delete all associated inverters; `0` = preserve inverters. |

---

### 4.15 Bind Inverter to Power Plant
Associates one or more inverter serial numbers with a power station.

* **URL**: `https://www.soliscloud.com:13333/v1/api/addDevice`
* **Rate Limit**: 2 requests/sec

#### Request parameters [Body]
| Parameter Name | Data Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `sn` | String | **Y** | Inverter Serial Number to bind. Support multiple comma-separated keys. |
| `id` | Integer | N | Target Power Station database ID. |
| `nmiCode` | String | N | Target Power Station NMI. |

---

## 4. Appendices

### Appendix 1: Failure Error Codes

| Return Code | Description | Corrective Troubleshooting Steps |
| :---: | :--- | :--- |
| **R0000** | No authority | Verify signature (Sign) values, check API credentials, and validate header syntax. |
| **B0001** | Has been bound to other users | The serial number (SN) is already associated with another profile. |
| **I0003** | Please enter SN | Request payload is missing the required Inverter or Collector Serial Number. |
| **B0049** | Collector does not exist / No permission | Verify the collector SN or check station access rights. |
| **I0000** | Necessary parameters are empty | Inspect request payload structure and fill in missing required parameters. |
| **B0011** | User does not exist | Check API user ID validity. |
| **I0012** | Incorrect account or password | Validate API Management credentials. |

---

### Appendix 2: Types of Power Plants

| Value | Power Plant Category |
| :---: | :--- |
| **0** | Grid-tied system |
| **1** | Hybrid/Energy storage system |
| **2** | AC Couple system |
| **3** | Export Power Manager (EPM grid + meter) |
| **4** | Built-in meter configuration |
| **5** | External display meter configuration |
| **6** | S5 offline and parallel energy storage |
| **7** | S5 grid-tied and parallel energy storage |
| **8** | Grid + AC Couple hybrid system |
| **9** | Standalone Off-Grid energy storage |
| **10** | S6 grid-tied and parallel energy storage |
| **11** | S6 offline and parallel energy storage |

---

### Appendix 3: Types of Inverter Meters

| Value | Meter Configuration Profile |
| :---: | :--- |
| **1** | Grid-tied configuration meter |
| **2** | Grid and load side combined meter |
| **3** | Grid connected and grid side active electricity meter |
| **4** | Energy storage and load side monitoring meter |
| **5** | Energy storage and grid side monitoring meter |
| **6** | Reserved for future integration |
| **7** | Standalone Off-Grid energy storage profile meter |
| **8** | Grid connected energy storage dual-meter configuration |
| **1001**| AC Couple configuration (without Current Transformer - CT) |
| **1002**| AC Couple configuration (with Current Transformer - CT) |
