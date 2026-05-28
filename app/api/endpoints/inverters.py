import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.api.deps import verify_solis_signature
from app.models.base import SolisResponse
from app.models.inverters import (
    InverterListRequest,
    InverterDetailRequest,
    InverterDayRequest,
    InverterMonthRequest,
    InverterYearRequest,
    InverterAllRequest
)
from app.models.collectors import CollectorListRequest
from app.core.security import (
    check_station_ownership,
    check_nmi_ownership,
    check_device_ownership,
    get_tenant_stations
)
from app.database.mock_db import (
    INVERTERS,
    STATIONS,
    ALARMS,
    get_dynamic_telemetry
)
from app.core.exceptions import SolisTenancyError

router = APIRouter(dependencies=[Depends(verify_solis_signature)])

@router.post("/inverterList", response_model=SolisResponse[Dict[str, Any]])
async def post_inverter_list(req: InverterListRequest, request: Request):
    api_id = request.state.api_id
    
    if req.stationId:
        if not check_station_ownership(api_id, req.stationId):
            raise SolisTenancyError(f"Access Denied: Station ID {req.stationId} does not belong to your account.")
    if req.nmiCode:
        if not check_nmi_ownership(api_id, req.nmiCode):
            raise SolisTenancyError(f"Access Denied: NMI Code {req.nmiCode} does not belong to your account.")

    tenant_stations = get_tenant_stations(api_id)
    records = []
    
    for inv_sn, inv_meta in INVERTERS.items():
        if inv_meta["stationId"] not in tenant_stations:
            continue
            
        if req.stationId and inv_meta["stationId"] != req.stationId:
            continue
        if req.nmiCode:
            station = STATIONS.get(inv_meta["stationId"], {})
            if station.get("nmiCode") != req.nmiCode:
                continue
                
        telemetry = await get_dynamic_telemetry(inv_sn)
        records.append(telemetry)
        
    inverter_status_vo = {
        "all": len(records),
        "normal": sum(1 for r in records if r["state"] == 1),
        "fault": sum(1 for r in records if r["state"] == 3),
        "offline": sum(1 for r in records if r["state"] == 2),
        "mppt": 0
    }
    
    page_no = int(req.pageNo)
    page_size = int(req.pageSize)
    
    start_idx = (page_no - 1) * page_size
    end_idx = start_idx + page_size
    paginated_records = records[start_idx:end_idx]
    
    payload = {
        "inverterStatusVo": inverter_status_vo,
        "page": {
            "records": paginated_records,
            "total": len(records),
            "size": page_size,
            "current": page_no,
            "pages": (len(records) + page_size - 1) // page_size
        }
    }
    return SolisResponse(data=payload)


@router.post("/inverterDetail", response_model=SolisResponse[Dict[str, Any]])
async def post_inverter_detail(req: InverterDetailRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in INVERTERS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break
                
    if not target_sn or target_sn not in INVERTERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inverter with SN '{req.sn}' or ID '{req.id}' not found in database."
        )

    if not check_device_ownership(api_id, target_sn, "inverter"):
        raise SolisTenancyError("Access Denied: You do not own this inverter device.")
        
    telemetry = await get_dynamic_telemetry(target_sn)
    return SolisResponse(data=telemetry)


@router.post("/inverterDetailList", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_inverter_detail_list(request: Request):
    api_id = request.state.api_id
    tenant_stations = get_tenant_stations(api_id)
    
    records = []
    for sn, inv in INVERTERS.items():
        if inv["stationId"] in tenant_stations:
            telemetry = await get_dynamic_telemetry(sn)
            records.append(telemetry)
            
    return SolisResponse(data=records)


@router.post("/inverterDay", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_inverter_day(req: InverterDayRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in INVERTERS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break

    if not target_sn or target_sn not in INVERTERS:
        raise HTTPException(status_code=404, detail="Inverter not found.")
        
    if not check_device_ownership(api_id, target_sn, "inverter"):
        raise SolisTenancyError("Access Denied: You do not own this inverter device.")
        
    time_str_prefix = req.time
    data_points = [
        {"time": "06:00:00", "pac": 0.5, "eToday": 0.1, "uPv1": 250.0},
        {"time": "12:00:00", "pac": 5.4, "eToday": 18.2, "uPv1": 395.0},
        {"time": "18:00:00", "pac": 0.2, "eToday": 27.8, "uPv1": 220.0}
    ]
    
    result = []
    for dp in data_points:
        result.append({
            "dataTimestamp": int(time.time() * 1000) - 3600000,
            "timeStr": f"{time_str_prefix} {dp['time']}",
            "time": dp["time"],
            "pac": dp["pac"],
            "pacStr": "kW",
            "pacPec": "0.001",
            "eToday": dp["eToday"],
            "eTotal": 36362.0,
            "uPv1": dp["uPv1"],
            "iPv1": 0.1,
            "uPv2": dp["uPv1"] - 2.0,
            "iPv2": 0.1,
            "state": 1
        })
    return SolisResponse(data=result)


@router.post("/inverterMonth", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_inverter_month(req: InverterMonthRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in INVERTERS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break

    if not target_sn or target_sn not in INVERTERS:
        raise HTTPException(status_code=404, detail="Inverter not found.")
        
    if not check_device_ownership(api_id, target_sn, "inverter"):
        raise SolisTenancyError("Access Denied: You do not own this inverter device.")
        
    month_str = req.month
    result = []
    for day in range(1, 6):
        date_str = f"{month_str}-{day:02d}"
        result.append({
            "inverterId": str(INVERTERS[target_sn]["id"]),
            "id": f"130867624734423351{day}",
            "money": round(25.0 * day * 1.1, 2),
            "moneyStr": req.money,
            "moneyPec": "1",
            "energy": round(25.0 * day, 1),
            "energyStr": "kWh",
            "energyPec": "1",
            "fullHour": 5.2,
            "date": int(time.time() * 1000) - day * 86400000,
            "dateStr": date_str,
            "timeZone": 8,
            "batteryDischargeEnergy": 0.0,
            "batteryChargeEnergy": 0.0,
            "gridPurchasedEnergy": 0.0,
            "gridPurchasedIncome": 0.0,
            "gridSellEnergy": 0.0,
            "gridSellIncome": 0.0,
            "consumeEnergy": 0,
            "produceEnergy": 0,
            "errorFlag": 0
        })
    return SolisResponse(data=result)


@router.post("/inverterYear", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_inverter_year(req: InverterYearRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in INVERTERS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break

    if not target_sn or target_sn not in INVERTERS:
        raise HTTPException(status_code=404, detail="Inverter not found.")
        
    if not check_device_ownership(api_id, target_sn, "inverter"):
        raise SolisTenancyError("Access Denied: You do not own this inverter device.")
        
    year_str = req.year
    result = []
    for m in range(1, 4):
        result.append({
            "inverterId": str(INVERTERS[target_sn]["id"]),
            "id": f"130867521817574963{m}",
            "money": 350.0 * m,
            "moneyStr": req.money,
            "moneyPec": "0.001",
            "energy": 866.0 * m,
            "energyStr": "kWh",
            "energyPec": "0.001",
            "fullHour": 108.25 * m,
            "date": int(time.time() * 1000) - m * 2592000000,
            "dateStr": f"{year_str}-{m:02d}",
            "timeZone": 8,
            "batteryDischargeEnergy": 0.0,
            "batteryChargeEnergy": 0.0,
            "gridPurchasedEnergy": 0.0,
            "gridSellEnergy": 0.0
        })
    return SolisResponse(data=result)


@router.post("/inverterAll", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_inverter_all(req: InverterAllRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in INVERTERS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break

    if not target_sn or target_sn not in INVERTERS:
        raise HTTPException(status_code=404, detail="Inverter not found.")
        
    if not check_device_ownership(api_id, target_sn, "inverter"):
        raise SolisTenancyError("Access Denied: You do not own this inverter device.")
        
    result = [
        {"year": 2022, "energy": 12500.0, "energyStr": "kWh", "money": 12500.0},
        {"year": 2023, "energy": 14200.0, "energyStr": "kWh", "money": 14200.0}
    ]
    return SolisResponse(data=result)


@router.post("/inverter/shelfTime", response_model=SolisResponse[Dict[str, Any]])
async def post_inverter_shelf_time(req: CollectorListRequest, request: Request):
    api_id = request.state.api_id
    
    if req.stationId:
        if not check_station_ownership(api_id, req.stationId):
            raise SolisTenancyError("Access Denied: Station ID does not belong to your account.")
            
    tenant_stations = get_tenant_stations(api_id)
    records = []
    
    for inv_sn, inv_meta in INVERTERS.items():
        if inv_meta["stationId"] not in tenant_stations:
            continue
        if req.stationId and inv_meta["stationId"] != req.stationId:
            continue
            
        records.append({
            "id": inv_meta["id"],
            "sn": inv_sn,
            "shelfBeginTime": inv_meta["createDate"],
            "shelfEndTime": inv_meta["updateShelfEndTime"],
            "shelfTime": 5,
            "shelfState": 0
        })
    return SolisResponse(data={"records": records, "total": len(records)})


@router.post("/alarmList", response_model=SolisResponse[Dict[str, Any]])
async def post_alarm_list(request: Request):
    api_id = request.state.api_id
    tenant_stations = get_tenant_stations(api_id)
    
    filtered_alarms = []
    for alarm in ALARMS:
        if int(alarm["stationId"]) in tenant_stations:
            filtered_alarms.append(alarm)
            
    return SolisResponse(data={
        "records": filtered_alarms,
        "total": len(filtered_alarms),
        "size": 10,
        "current": 1,
        "pages": 1
    })
