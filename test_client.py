import json
import base64
import hashlib
import hmac
import datetime
import requests
import time
from typing import Dict, Any

# Local server details
BASE_URL = "http://127.0.0.1:8000"
API_ID = "1300386381676644416"
API_SECRET = "mock_secret_key_12345"

def generate_solis_headers(api_id: str, api_secret: str, path: str, body: Dict[str, Any]) -> Dict[str, str]:
    """
    Computes SolisCloud V2.0 signature authentication headers exactly as required by the API.
    """
    # 1. Stringify payload to JSON (compact representation with no whitespace spaces)
    body_str = json.dumps(body, separators=(',', ':'))
    
    # 2. Compute Content-MD5
    md5_hash = hashlib.md5(body_str.encode('utf-8')).digest()
    content_md5 = base64.b64encode(md5_hash).decode('utf-8')
    
    # 3. Format Date exactly in GMT/UTC format
    now = datetime.datetime.now(datetime.timezone.utc)
    # Using Solis specification: 'EEE, d MMM yyyy HH:mm:ss GMT' (Locale.US)
    # E.g. Fri, 26 Jul 2019 06:00:46 GMT
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 4. Formulate StringToSign
    content_type = "application/json;charset=UTF-8"
    string_to_sign = f"POST\n{content_md5}\n{content_type}\n{date_str}\n{path}"
    
    # 5. Compute HMAC-SHA1 signature
    key = api_secret.encode('utf-8')
    msg = string_to_sign.encode('utf-8')
    signature = hmac.new(key, msg, hashlib.sha1).digest()
    sign_base64 = base64.b64encode(signature).decode('utf-8')
    
    headers = {
        "Content-MD5": content_md5,
        "Content-Type": content_type,
        "Date": date_str,
        "Authorization": f"API {api_id}:{sign_base64}"
    }
    return headers

def perform_post(endpoint: str, body: Dict[str, Any], api_id: str = API_ID, api_secret: str = API_SECRET, skip_delay: bool = False) -> requests.Response:
    """
    Assembles headers, computes signature, and performs a POST request to the mock server.
    """
    if not skip_delay:
        time.sleep(0.55)  # Spacer to prevent triggering rate limits on standard tests
    url = f"{BASE_URL}{endpoint}"
    headers = generate_solis_headers(api_id, api_secret, endpoint, body)
    
    # Crucial: Send compact JSON body to match our MD5 hash input
    response = requests.post(url, data=json.dumps(body, separators=(',', ':')), headers=headers)
    return response

# --- Running tests against the FastAPI Server ---

def run_tests():
    print("=" * 60)
    print("MOCK SOLISCLOUD PLATFORM API VERIFICATION CLIENT")
    print("=" * 60)
    
    # --- Diagnostic Health Check ---
    print("\n[Health Check] Querying base status (no auth)...")
    try:
        diag = requests.get(BASE_URL)
        print(f"Server diagnostic check: {diag.status_code} - {diag.json()}")
    except requests.exceptions.ConnectionError:
        print("[-] CONNECTION ERROR: Please make sure the FastAPI server is running!")
        print("    Run: uvicorn app.main:app --reload")
        return

    # --- Test 1: Successful Inverter List ---
    print("\n[Test 1] Querying Inverter List under Station with correct credentials...")
    body_inv_list = {
        "pageNo": "1",
        "pageSize": "10",
        "stationId": 1298491919448631809
    }
    r = perform_post("/v1/api/inverterList", body_inv_list)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Success Flag: {data.get('success')}")
        print(f"Records Count: {len(data['data']['page']['records'])}")
        print(f"Sample Record SN: {data['data']['page']['records'][0]['sn']}")
        print(f"Sample Record Power Output (pac): {data['data']['page']['records'][0]['pac']} kW")
    else:
        print(f"Failed! Response: {r.text}")

    # --- Test 2: Successful Inverter Detail ---
    print("\n[Test 2] Querying Inverter Details for specific SN...")
    body_inv_detail = {
        "id": 1308675217944611083,
        "sn": "120B40198150131"
    }
    r = perform_post("/v1/api/inverterDetail", body_inv_detail)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Success Flag: {data.get('success')}")
        print(f"Inverter Temperature: {data['data'].get('inverterTemperature')} °C")
        print(f"DC Input Voltage (uPv1): {data['data'].get('uPv1')} V")
        print(f"Battery Capacity (SOC): {data['data'].get('batteryCapacitySoc')} %")
    else:
        print(f"Failed! Response: {r.text}")

    # --- Test 3: Successful Power Station List ---
    print("\n[Test 3] Querying Power Station list...")
    body_station_list = {
        "pageNo": 1,
        "pageSize": 10
    }
    r = perform_post("/v1/api/userStationList", body_station_list)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        stations = data['data']['page']['records']
        print(f"Stations Found: {len(stations)}")
        for st in stations:
            print(f"  - Station: '{st['stationName']}' | Capacity: {st['capacity']} kWp | Today income: {st['dayIncome']} AUD")
    else:
        print(f"Failed! Response: {r.text}")

    # --- Test 4: Authentication Mismatch (Expects 401) ---
    print("\n[Test 4] Querying using wrong API Secret (expects 401 Signature mismatch)...")
    r = perform_post("/v1/api/inverterList", body_inv_list, api_secret="incorrect_secret_xyz")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json() if r.status_code == 401 else r.text}")

    # --- Test 5: Request Payload Tampering (Expects 401) ---
    print("\n[Test 5] Simulating payload tampering (expects 401 Content-MD5 mismatch)...")
    time.sleep(0.6)  # Spacer to prevent triggering rate limit on raw request
    headers = generate_solis_headers(API_ID, API_SECRET, "/v1/api/inverterList", body_inv_list)
    # Tamper the body *after* header calculations
    tampered_body = {**body_inv_list, "pageSize": "20"} 
    url = f"{BASE_URL}/v1/api/inverterList"
    r = requests.post(url, json=tampered_body, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json() if r.status_code == 401 else r.text}")

    # --- Test 6: Expired / Outdated Date header (Expects 401) ---
    print("\n[Test 6] Querying with old date header (expects 401 timestamp date skew)...")
    time.sleep(0.6)  # Spacer to prevent triggering rate limit on raw request
    headers = generate_solis_headers(API_ID, API_SECRET, "/v1/api/inverterList", body_inv_list)
    # Set date to yesterday
    yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    headers["Date"] = yesterday.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Recalculate signature with tampered date to show skew triggers skew checks (and not sign checks first)
    content_type = "application/json;charset=UTF-8"
    string_to_sign = f"POST\n{headers['Content-MD5']}\n{content_type}\n{headers['Date']}\n/v1/api/inverterList"
    signature = hmac.new(API_SECRET.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1).digest()
    headers["Authorization"] = f"API {API_ID}:{base64.b64encode(signature).decode('utf-8')}"
    
    r = requests.post(url, data=json.dumps(body_inv_list, separators=(',', ':')), headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json() if r.status_code == 401 else r.text}")

    # --- Test 7: Rate Limiting DDoS Protection (Expects 429) ---
    print("\n[Test 7] Performing rapid requests to inverterList to trigger rate limits (expects 429)...")
    for i in range(5):
        r = perform_post("/v1/api/inverterList", body_inv_list, skip_delay=True)
        print(f"  Request {i+1} Status: {r.status_code}")
        if r.status_code == 429:
            print(f"  [+] Success! Rate limit triggered: {r.json()}")
            break
    else:
        print("  [-] Failed: Rate limit not triggered. Check limit config.")

    # --- Test 8: IDOR Relational Multi-Tenancy Validation (Expects 403 / Isolation Check) ---
    print("\n[Test 8] Simulating IDOR attack (Tenant 1 querying Station 2, expects 403 Forbidden)...")
    body_station_2_detail = {
        "id": 1298491919448632027 # Owned by Tenant 2 (userId: 10002)
    }
    r = perform_post("/v1/api/stationDetail", body_station_2_detail)
    print(f"Tenant 1 querying Station 2 Status: {r.status_code}")
    print(f"Response: {r.json()}")
    
    print("\n[Test 8b] Listing power stations for Tenant 1 (expects only YingZhen Station)...")
    body_station_list = {
        "pageNo": 1,
        "pageSize": 10
    }
    r = perform_post("/v1/api/userStationList", body_station_list)
    if r.status_code == 200:
        data = r.json()
        stations = data['data']['page']['records']
        print(f"Tenant 1 stations found: {len(stations)}")
        for st in stations:
            print(f"  - Owned Station Name: '{st['stationName']}' (ID: {st['id']})")
    else:
        print(f"Failed! {r.text}")

    # --- Test 9: Input Sanitization Constraints (Expects 422) ---
    print("\n[Test 9] Querying with excessive page size pageSize: '1000' (expects 422 Unprocessable Entity)...")
    body_excessive_page = {
        "pageNo": "1",
        "pageSize": "1000", # Max allowed is 100
        "stationId": 1298491919448631809
    }
    r = perform_post("/v1/api/inverterList", body_excessive_page)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json() if r.status_code == 422 else r.text}")

    print("\n[Test 9b] Querying with negative pageNo: '-5' (expects 422 Unprocessable Entity)...")
    body_negative_page = {
        "pageNo": "-5",
        "pageSize": "10",
        "stationId": 1298491919448631809
    }
    r = perform_post("/v1/api/inverterList", body_negative_page)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json() if r.status_code == 422 else r.text}")

if __name__ == "__main__":
    run_tests()
