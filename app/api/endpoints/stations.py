import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.api.deps import verify_solis_signature
from app.models.base import SolisResponse
from app.models.stations import (
    StationListRequest,
    StationDetailRequest,
    StationDayRequest,
    AddStationRequest,
    UpdateStationRequest
)
from app.models.collectors import (
    BindCollectorRequest,
    UnbindCollectorRequest
)
from app.models.inverters import BindInverterRequest
from app.core.security import (
    check_station_ownership,
    check_nmi_ownership,
    check_device_ownership,
    get_tenant_stations,
    add_station_to_tenant
)
from app.database.mock_db import (
    STATIONS,
    COLLECTORS,
    get_solar_multiplier,
    get_station_summary,
    DATA_LOCK
)
from app.core.exceptions import SolisTenancyError

router = APIRouter(dependencies=[Depends(verify_solis_signature)])

@router.post("/userStationList", response_model=SolisResponse[Dict[str, Any]])
async def post_user_station_list(req: StationListRequest, request: Request):
    api_id = request.state.api_id
    tenant_stations = get_tenant_stations(api_id)
    
    records = []
    for st_id in STATIONS.keys():
        if st_id in tenant_stations:
            summary = await get_station_summary(st_id)
            records.append(summary)
        
    payload = {
        "stationStatusVo": {
            "all": len(records),
            "normal": len(records),
            "fault": 0,
            "offline": 0,
            "building": 0,
            "mppt": 0
        },
        "page": {
            "records": records,
            "total": len(records),
            "size": req.pageSize,
            "current": req.pageNo,
            "pages": 1
        }
    }
    return SolisResponse(data=payload)


@router.post("/stationDetail", response_model=SolisResponse[Dict[str, Any]])
async def post_station_detail(req: StationDetailRequest, request: Request):
    api_id = request.state.api_id
    target_id = req.id
    
    if not target_id and req.nmiCode:
        for st_key, meta in STATIONS.items():
            if meta["nmiCode"] == req.nmiCode:
                target_id = st_key
                break
                
    if not target_id or target_id not in STATIONS:
        raise HTTPException(status_code=404, detail="Station not found in database.")
        
    if not check_station_ownership(api_id, target_id):
        raise SolisTenancyError("Access Denied: Station does not belong to your account.")
        
    details = await get_station_summary(target_id)
    return SolisResponse(data=details)


@router.post("/stationDetailList", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_station_detail_list(request: Request):
    api_id = request.state.api_id
    tenant_stations = get_tenant_stations(api_id)
    
    records = []
    for sid in STATIONS.keys():
        if sid in tenant_stations:
            summary = await get_station_summary(sid)
            records.append(summary)
            
    return SolisResponse(data=records)


@router.post("/stationDay", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_station_day(req: StationDayRequest, request: Request):
    api_id = request.state.api_id
    target_id = req.id
    
    if not target_id and req.nmiCode:
        for st_key, meta in STATIONS.items():
            if meta["nmiCode"] == req.nmiCode:
                target_id = st_key
                break
                
    if not target_id or target_id not in STATIONS:
        raise HTTPException(status_code=404, detail="Station not found in database.")
        
    if not check_station_ownership(api_id, target_id):
        raise SolisTenancyError("Access Denied: Station does not belong to your account.")
        
    mult = get_solar_multiplier()
    result = [
        {
            "time": "12:00:00",
            "power": round(12.0 * mult, 3),
            "powerStr": "kW",
            "familyLoadPower": 1.5,
            "psum": round(12.0 * mult - 1.5, 3),
            "oneSelf": round(1.5, 3)
        }
    ]
    return SolisResponse(data=result)


@router.post("/addStation", response_model=SolisResponse[Dict[str, Any]])
async def post_add_station(req: AddStationRequest, request: Request):
    api_id = request.state.api_id
    new_id = int(time.time())
    nmi_str = str(req.nmiCode or "")
    
    with DATA_LOCK:
        STATIONS[new_id] = {
            "id": new_id,
            "stationName": req.stationName,
            "addr": req.addr,
            "capacity": float(req.capacity),
            "capacityStr": "kWp",
            "price": float(req.price or 1.0),
            "money": req.money,
            "nmiCode": nmi_str,
            "createDate": int(time.time() * 1000),
            "state": 1,
            "timeZone": 8.0,
            "timeZoneStr": "UTC+08:00",
            "timeZoneName": "(UTC+08:00)",
        }
        
    add_station_to_tenant(api_id, new_id, nmi_str)
    return SolisResponse(data={"id": new_id})


@router.post("/stationUpdate", response_model=SolisResponse[Any])
async def post_station_update(req: UpdateStationRequest, request: Request):
    api_id = request.state.api_id
    
    if req.id not in STATIONS:
        raise HTTPException(status_code=404, detail="Station ID not found.")
        
    if not check_station_ownership(api_id, req.id):
        raise SolisTenancyError("Access Denied: Station does not belong to your account.")
        
    with DATA_LOCK:
        STATIONS[req.id].update({
            "stationName": req.stationName,
            "capacity": float(req.capacity),
            "price": req.price,
            "addr": req.addr
        })
    return SolisResponse(msg="Update completed successfully.", data=None)


@router.post("/addStationBindCollector", response_model=SolisResponse[Any])
async def post_bind_collector(req: BindCollectorRequest, request: Request):
    api_id = request.state.api_id
    
    if req.nmiCode:
        if not check_nmi_ownership(api_id, req.nmiCode):
            raise SolisTenancyError("Access Denied: You do not own the associated NMI station.")
            
    return SolisResponse(msg="Collector bound successfully.", data="1298491919448634915")


@router.post("/delCollector", response_model=SolisResponse[Any])
async def post_unbind_collector(req: UnbindCollectorRequest, request: Request):
    api_id = request.state.api_id
    
    if req.sn:
        if req.sn not in COLLECTORS:
            raise HTTPException(status_code=404, detail="Collector SN not found.")
        if not check_device_ownership(api_id, req.sn, "collector"):
            raise SolisTenancyError("Access Denied: You do not own this collector stick.")
            
    return SolisResponse(msg="Collector stick unbound successfully.", data=None)


@router.post("/addDevice", response_model=SolisResponse[Any])
async def post_bind_inverter(req: BindInverterRequest, request: Request):
    api_id = request.state.api_id
    
    if req.id:
        if not check_station_ownership(api_id, req.id):
            raise SolisTenancyError("Access Denied: Target Station ID does not belong to your account.")
    if req.nmiCode:
        if not check_nmi_ownership(api_id, req.nmiCode):
            raise SolisTenancyError("Access Denied: Target NMI does not belong to your account.")
            
    return SolisResponse(msg="Inverter unit bound successfully.", data=None)
