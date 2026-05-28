from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.api.deps import verify_solis_signature
from app.models.base import SolisResponse
from app.models.collectors import (
    CollectorListRequest,
    CollectorDetailRequest
)
from app.models.epms import EpmDayRequest
from app.core.security import (
    check_station_ownership,
    check_device_ownership,
    get_tenant_stations
)
from app.database.mock_db import COLLECTORS
from app.core.exceptions import SolisTenancyError

import time

router = APIRouter(dependencies=[Depends(verify_solis_signature)])

@router.post("/collectorList", response_model=SolisResponse[Dict[str, Any]])
async def post_collector_list(req: CollectorListRequest, request: Request):
    api_id = request.state.api_id
    
    if req.stationId:
        if not check_station_ownership(api_id, req.stationId):
            raise SolisTenancyError("Access Denied: Station ID does not belong to your account.")

    tenant_stations = get_tenant_stations(api_id)
    records = []
    for r in COLLECTORS.values():
        if r["stationId"] not in tenant_stations:
            continue
        if req.stationId and r["stationId"] != req.stationId:
            continue
        records.append(r)
        
    payload = {
        "collectionStatusVo": {
            "all": len(records),
            "normal": sum(1 for r in records if r["state"] == 1),
            "fault": 0,
            "offline": sum(1 for r in records if r["state"] != 1)
        },
        "page": {
            "records": records,
            "total": len(records),
            "size": int(req.pageSize),
            "current": int(req.pageNo),
            "pages": 1
        }
    }
    return SolisResponse(data=payload)


@router.post("/collectorDetail", response_model=SolisResponse[Dict[str, Any]])
async def post_collector_detail(req: CollectorDetailRequest, request: Request):
    api_id = request.state.api_id
    target_sn = req.sn
    
    if not target_sn and req.id:
        for sn_key, meta in COLLECTORS.items():
            if meta["id"] == req.id:
                target_sn = sn_key
                break
                
    if not target_sn or target_sn not in COLLECTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collector not found."
        )

    if not check_device_ownership(api_id, target_sn, "collector"):
        raise SolisTenancyError("Access Denied: You do not own this collector device.")
        
    return SolisResponse(data=COLLECTORS[target_sn])


@router.post("/collector/day", response_model=SolisResponse[List[Dict[str, Any]]])
async def post_collector_day(req: EpmDayRequest, request: Request):
    api_id = request.state.api_id
    
    if req.sn not in COLLECTORS:
        raise HTTPException(status_code=404, detail="Collector not found.")
        
    if not check_device_ownership(api_id, req.sn, "collector"):
        raise SolisTenancyError("Access Denied: You do not own this collector device.")
        
    result = [
        {
            "dataTimestamp": int(time.time() * 1000) - 3600000,
            "timeStr": "05:03:07",
            "rssi": 85,
            "rssiLevel": 3,
            "pec": 100
        }
    ]
    return SolisResponse(data=result)
