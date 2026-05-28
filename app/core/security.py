import base64
import hashlib
import hmac
import datetime
import threading
from fastapi import Request, HTTPException, status
from app.core.config import settings

# Map of valid credentials: apiId -> apiSecret
CREDENTIALS_DB = {
    settings.SOLIS_API_ID: settings.SOLIS_API_SECRET,
    settings.SOLIS_API_ID_2: settings.SOLIS_API_SECRET_2
}

# Relational multi-tenancy map: apiId -> user profile metadata
API_TENANT_MAP = {
    settings.SOLIS_API_ID: {
        "userId": 10001,
        "stations": [1298491919448631809],
        "nmiCodes": ["41028459350"]
    },
    settings.SOLIS_API_ID_2: {
        "userId": 10002,
        "stations": [1298491919448632027],
        "nmiCodes": ["330110862"]
    }
}

API_LOCK = threading.Lock()

def parse_date_header(date_str: str) -> datetime.datetime:
    """
    Parses Solis date format 'EEE, d MMM yyyy HH:mm:ss GMT' into a timezone-aware UTC datetime.
    """
    try:
        return datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        pass
    
    try:
        return datetime.datetime.strptime(date_str, "%a, %e %b %Y %H:%M:%S GMT").replace(tzinfo=datetime.timezone.utc)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Date format. Expected GMT format. Error: {str(e)}"
        )

def check_station_ownership(api_id: str, station_id: int) -> bool:
    if settings.SOLIS_DISABLE_AUTH:
        return True
    with API_LOCK:
        tenant = API_TENANT_MAP.get(api_id)
        if not tenant:
            return False
        return station_id in tenant["stations"]

def check_nmi_ownership(api_id: str, nmi_code: str) -> bool:
    if settings.SOLIS_DISABLE_AUTH:
        return True
    with API_LOCK:
        tenant = API_TENANT_MAP.get(api_id)
        if not tenant:
            return False
        return nmi_code in tenant["nmiCodes"]

def check_device_ownership(api_id: str, sn: str, device_type: str) -> bool:
    if settings.SOLIS_DISABLE_AUTH:
        return True
    
    station_id = None
    from app.database.mock_db import INVERTERS, COLLECTORS, EPMS, WEATHER_SENSORS
    
    if device_type == "inverter":
        device = INVERTERS.get(sn)
        if device:
            station_id = device.get("stationId")
    elif device_type == "collector":
        device = COLLECTORS.get(sn)
        if device:
            station_id = device.get("stationId")
    elif device_type == "epm":
        device = EPMS.get(sn)
        if device:
            station_id = device.get("stationId")
    elif device_type == "weather":
        device = WEATHER_SENSORS.get(sn)
        if device:
            station_id = device.get("stationId")
            
    if station_id is None:
        return False
        
    return check_station_ownership(api_id, station_id)

def get_tenant_stations(api_id: str) -> list:
    if settings.SOLIS_DISABLE_AUTH:
        from app.database.mock_db import STATIONS
        return list(STATIONS.keys())
    with API_LOCK:
        tenant = API_TENANT_MAP.get(api_id)
        return tenant["stations"].copy() if tenant else []

def get_tenant_nmi_codes(api_id: str) -> list:
    if settings.SOLIS_DISABLE_AUTH:
        from app.database.mock_db import STATIONS
        return [st["nmiCode"] for st in STATIONS.values() if "nmiCode" in st]
    with API_LOCK:
        tenant = API_TENANT_MAP.get(api_id)
        return tenant["nmiCodes"].copy() if tenant else []

def add_station_to_tenant(api_id: str, station_id: int, nmi_code: str = None):
    if settings.SOLIS_DISABLE_AUTH:
        return
    with API_LOCK:
        if api_id in API_TENANT_MAP:
            if station_id not in API_TENANT_MAP[api_id]["stations"]:
                API_TENANT_MAP[api_id]["stations"].append(station_id)
            if nmi_code and nmi_code not in API_TENANT_MAP[api_id]["nmiCodes"]:
                API_TENANT_MAP[api_id]["nmiCodes"].append(nmi_code)
