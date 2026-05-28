import time
import datetime
import math
import threading
from typing import Dict, Any, List

DATA_LOCK = threading.Lock()

# In-memory database tables
STATIONS = {
    1298491919448631809: {
        "id": 1298491919448631809,
        "stationName": "YingZhen Station",
        "addr": "Aquatic Drive, Forster",
        "capacity": 12.000,
        "capacityStr": "kWp",
        "capacity1": 12.0,
        "userId": 10001,
        "nmiCode": "41028459350",
        "timeZone": 10.0,
        "timeZoneStr": "UTC+10:00",
        "timeZoneName": "(UTC+10:00)",
        "price": 1.0,
        "money": "AUD",
        "createDate": 1677119648000,
        "state": 1, # Online
        "batteryPercent": 65, # Battery SOC %
        "familyLoadPower": 1.5,
    },
    1298491919448632027: {
        "id": 1298491919448632027,
        "stationName": "Autotest Station",
        "addr": "Hangzhou, Zhejiang",
        "capacity": 20.000,
        "capacityStr": "kWp",
        "capacity1": 20.0,
        "userId": 10002,
        "nmiCode": "330110862",
        "timeZone": 8.0,
        "timeZoneStr": "UTC+08:00",
        "timeZoneName": "(UTC+08:00)",
        "price": 0.5,
        "money": "CNY",
        "createDate": 1687918406814,
        "state": 1,
        "batteryPercent": 0,
        "familyLoadPower": 0.0,
    }
}

INVERTERS = {
    "120B40198150131": {
        "id": 1308675217944611083,
        "sn": "120B40198150131",
        "model": "b4",
        "stationId": 1298491919448631809,
        "collectorSn": "404314859",
        "productModel": "b4",
        "series": "Solis-3P8K-5G",
        "name": "Primary Inverter",
        "dcInputType": 3, # 4 Channels (0=1, 1=2, 2=3, 3=4)
        "acOutputType": 1, # Three-phase
        "state": 1,
        "inverterMeterModel": 1,
        "createDate": 1687846773000,
        "updateShelfEndTime": 1845936000000, # Warranty
    },
    "00FFFC445594901": {
        "id": 1308675217944612385,
        "sn": "00FFFC445594901",
        "model": "1E",
        "stationId": 1298491919448632027,
        "collectorSn": "FFFC4455949",
        "productModel": "1E",
        "series": "Solis-Mini-2000-4G",
        "name": "Sec Inverter",
        "dcInputType": 1, # 2 Channels
        "acOutputType": 0, # Single-phase
        "state": 1,
        "inverterMeterModel": 1,
        "createDate": 1687846773000,
        "updateShelfEndTime": 1845936000000,
    }
}

COLLECTORS = {
    "404314859": {
        "id": 1306858901386141423,
        "sn": "404314859",
        "stationId": 1298491919448631809,
        "model": "WIFI-BOX",
        "name": "Collector 1",
        "state": 1,
        "rssiLevel": "3",
        "lanIp": "192.168.1.150",
        "connectedSsid": "SolarNet_2.4G",
        "maximumNumber": 10,
        "actualNumber": 1,
        "simFlowState": 1,
    },
    "FFFC4455949": {
        "id": 1306858901386142563,
        "sn": "FFFC4455949",
        "stationId": 1298491919448632027,
        "model": "GPRS-STICK",
        "name": "Collector 2",
        "state": 1,
        "rssiLevel": "2",
        "lanIp": "10.0.0.8",
        "connectedSsid": "Mobile-GPRS",
        "maximumNumber": 10,
        "actualNumber": 1,
        "simFlowState": -4,
    }
}

EPMS = {
    "00FFC0011557002": {
        "id": 1306507149505459510,
        "sn": "00FFC0011557002",
        "stationId": 1298491919448631809,
        "collectorId": 1306858901386141423,
        "collectorSn": "404314859",
        "state": 1,
        "pLimit": 90.0,
        "ctRatio": 3000,
        "pSet": 10.0,
        "empSoftwareVersion": "V12",
        "failSafe": 0,
    }
}

WEATHER_SENSORS = {
    "FFC00115570": {
        "id": 1306858901386142611,
        "sn": "FFC00115570",
        "stationId": 1298491919448631809,
        "name": "WeatherStation-North",
        "weatherModel": "2",  # Jinzhou Licheng
        "state": 1,
    }
}

ALARMS = [
    {
        "id": "1",
        "stationId": "1298491919448631809",
        "alarmDeviceSn": "120B40198150131",
        "alarmDeviceType": "3",
        "alarmType": 0,
        "alarmLevel": "1",
        "alarmCode": "2129",
        "alarmBeginTime": 1687918458326,
        "alarmEndTime": 1687918484635,
        "alarmLong": "26308",
        "state": "1",
        "advice": "System restored automatically.",
        "alarmMsg": "Grid Overvoltage",
        "model": "b4",
        "warningInfoData": 0,
        "type": 0
    }
]

# Track system startup to accumulate simulated energy
STARTUP_TIME = time.time()

def get_solar_multiplier() -> float:
    """
    Returns a dynamic solar multiplier (0.0 to 1.0) based on the current hour of the day.
    Simulates a peak curve peaking at 13:00 (1 PM) and dropping to 0 at night.
    """
    now = datetime.datetime.now()
    hour = now.hour + now.minute / 60.0
    
    # Sunset/Sunrise margins
    sunrise = 6.0
    sunset = 18.0
    
    if hour < sunrise or hour > sunset:
        return 0.0
    
    # Shift sine wave to peak at 12:30 PM (halfway between 6am and 6pm)
    val = math.sin((hour - sunrise) / (sunset - sunrise) * math.pi)
    return max(0.0, val)

async def get_dynamic_telemetry(inverter_sn: str) -> Dict[str, Any]:
    """
    Generates dynamic real-time telemetries for a given inverter SN based on current time.
    Calculates active power (pac), daily production (etoday), string voltages, etc.
    """
    inv = INVERTERS.get(inverter_sn)
    if not inv:
        return {}
        
    mult = get_solar_multiplier()
    station = STATIONS.get(inv["stationId"], {})
    capacity = inv.get("power", station.get("capacity", 10.0))
    
    # 1. Power Output (pac)
    pac = round(capacity * mult * 0.85, 3) # Max 85% of rating active power
    
    # 2. Accumulated Energy Today (etoday)
    # Increment energy count dynamically since server started (simulate 0.1 kWh per minute per kW capacity)
    elapsed_minutes = (time.time() - STARTUP_TIME) / 60.0
    etoday = round(min(capacity * 6.5, elapsed_minutes * 0.05 * capacity * (mult + 0.1)), 3)
    etotal = round(5400.0 + etoday, 3)
    
    # 3. DC Strings inputs calculations
    strings = {}
    channels_count = inv["dcInputType"] + 1
    total_dc_power = 0.0
    
    for i in range(1, 33):
        if i <= channels_count:
            # Generate active channel voltages & currents
            upv = round(320.0 + 50.0 * mult + (i * 5.0), 1) if mult > 0 else 0.0
            ipv = round(5.0 * mult + (i * 0.2), 2) if mult > 0 else 0.0
            pow_val = round(upv * ipv, 1)
            total_dc_power += pow_val
            
            strings[f"uPv{i}"] = upv
            strings[f"iPv{i}"] = ipv
            strings[f"pow{i}"] = pow_val
        else:
            # Empty channel placeholder
            strings[f"uPv{i}"] = 0.0
            strings[f"iPv{i}"] = 0.0
            strings[f"pow{i}"] = 0.0
            
    # 4. Phase telemetry (three-phase or single-phase)
    phases = {}
    if inv["acOutputType"] == 1: # Three-phase
        phases["uAc1"] = round(230.0 + 3.0 * mult, 1)
        phases["uAc2"] = round(231.0 - 2.0 * mult, 1)
        phases["uAc3"] = round(229.5 + 1.0 * mult, 1)
        phases["iAc1"] = round((pac * 1000 / 3) / phases["uAc1"], 2) if pac > 0 else 0.0
        phases["iAc2"] = round((pac * 1000 / 3) / phases["uAc2"], 2) if pac > 0 else 0.0
        phases["iAc3"] = round((pac * 1000 / 3) / phases["uAc3"], 2) if pac > 0 else 0.0
    else: # Single-phase
        phases["uAc1"] = round(230.0 + 2.0 * mult, 1)
        phases["uAc2"] = 0.0
        phases["uAc3"] = 0.0
        phases["iAc1"] = round((pac * 1000) / phases["uAc1"], 2) if pac > 0 else 0.0
        phases["iAc2"] = 0.0
        phases["iAc3"] = 0.0
 
    # 5. Build dynamic battery state (if storage/hybrid inverter product)
    battery = {}
    if inv["productModel"] == "b4" or inv["productModel"] == "1E": # Hybrid models
        soc = station.get("batteryPercent", 75)
        # Charging during peak daylight hours (10 AM to 3 PM), discharging in morning/evening
        now = datetime.datetime.now()
        bat_power = 0.0
        if 10 <= now.hour <= 15:
            # Charging state
            bat_power = round(2.5 * mult, 3) # Charging at max 2.5 kW
            soc = min(100, int(soc + elapsed_minutes * 0.1))
        elif now.hour >= 17 or now.hour <= 8:
            # Discharging state
            bat_power = -1.2 # Discharging at 1.2 kW
            soc = max(15, int(soc - elapsed_minutes * 0.05))
            
        battery.update({
            "batteryCapacitySoc": float(soc),
            "batteryHealthSoh": 98.0,
            "batteryPower": abs(bat_power),
            "batteryPowerStr": "kW",
            "batteryVoltage": round(350.0 + 10.0 * (soc / 100.0), 1),
            "bstteryCurrent": round(abs(bat_power * 1000 / 360.0), 2) if bat_power != 0 else 0.0,
            "batteryTodayChargeEnergy": round(2.4 + max(0.0, elapsed_minutes * 0.02), 3),
            "batteryTodayDischargeEnergy": round(1.2 + max(0.0, elapsed_minutes * 0.015), 3),
        })
 
    # Combined payload mapping
    result = {
        "id": inv["id"],
        "sn": inv["sn"],
        "stationId": inv["stationId"],
        "stationName": station.get("stationName"),
        "userId": inv["createDate"],
        "collectorSn": inv["collectorSn"],
        "pac": pac,
        "pacStr": "kW",
        "power": capacity,
        "powerStr": "kWp",
        "etoday": etoday,
        "etodayStr": "kWh",
        "etotal": etotal,
        "etotalStr": "MWh",
        "state": 1 if mult > 0 else 2,  # Online in day, Offline at night
        "dataTimestamp": int(time.time() * 1000),
        "inverterTemperature": round(32.5 + 15.0 * mult, 1),
        **strings,
        **phases,
        **battery
    }
    
    return result

async def get_station_summary(station_id: int) -> Dict[str, Any]:
    """
    Compiles dynamic production summaries for a Power Station.
    """
    st = STATIONS.get(station_id)
    if not st:
        return {}
        
    # Aggregate dynamic values from connected inverters
    inverters_under_station = [inv for inv in INVERTERS.values() if inv["stationId"] == station_id]
    
    total_capacity = 0.0
    total_pac = 0.0
    total_today = 0.0
    total_lifetime = 0.0
    
    for inv in inverters_under_station:
        telemetry = await get_dynamic_telemetry(inv["sn"])
        total_capacity += telemetry.get("power", 0.0)
        total_pac += telemetry.get("pac", 0.0)
        total_today += telemetry.get("etoday", 0.0)
        total_lifetime += telemetry.get("etotal", 0.0)
        
    mult = get_solar_multiplier()
    
    return {
        "id": st["id"],
        "stationName": st["stationName"],
        "addr": st["addr"],
        "capacity": total_capacity or st["capacity"],
        "capacityStr": "kWp",
        "power": round(total_pac, 3),
        "powerStr": "kW",
        "dayEnergy": round(total_today, 3),
        "dayEnergyStr": "kWh",
        "monthEnergy": round(240.0 + total_today, 3),
        "monthEnergyStr": "kWh",
        "yearEnergy": round(1520.0 + total_today, 3),
        "yearEnergyStr": "kWh",
        "allEnergy": round(total_lifetime or 5400.0, 3),
        "allEnergyStr": "MWh",
        "dayIncome": round(total_today * st["price"], 2),
        "allIncome": round((5400.0 * 1000 + total_today) * st["price"], 2),
        "state": 1 if mult > 0 else 2,
        "timeZone": st["timeZone"],
        "timeZoneStr": st["timeZoneStr"],
        "timeZoneName": st["timeZoneName"],
    }
