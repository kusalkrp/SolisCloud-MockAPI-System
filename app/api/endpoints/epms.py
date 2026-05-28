from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import verify_solis_signature
from app.models.base import SolisResponse
from app.models.collectors import CollectorListRequest
from app.models.epms import (
    EpmDetailRequest,
    EpmDayRequest
)
from app.core.security import (
    check_station_ownership,
    check_device_ownership,
    get_tenant_stations
)
from app.database.mock_db import EPMS, get_solar_multiplier
from app.core.exceptions import SolisTenancyError

import time

router = APIRouter(dependencies=[Depends(verify_solis_signature)])

@router.post("/epmList", response_model=SolisResponse[Dict[str, Any]])
async def post_epm_list(req: CollectorListRequest, request: Request):
    api_id = request.state.api_id
    
    if req.stationId:
        if not check_station_ownership(api_id, req.stationId):
            raise SolisTenancyError("Access Denied: Station ID does not belong to your account.")
            
    tenant_stations = get_tenant_stations(api_id)
    records = []
    for r in EPMS.values():
        if r["stationId"] not in tenant_stations:
            continue
        if req.stationId and r["stationId"] != req.stationId:
            continue
        records.append(r)
        
    payload = {
        "epmStatusVo": {"all": len(records), "normal": len(records), "fault": 0, "offline": 0},
        "page": {
            "records": records,
            "total": len(records),
            "size": int(req.pageSize),
            "current": int(req.pageNo),
            "pages": 1
        }
    }
    return SolisResponse(data=payload)


@router.post("/epmDetail", response_model=SolisResponse[Dict[str, Any]])
async def post_epm_detail(req: EpmDetailRequest, request: Request):
    api_id = request.state.api_id
    
    if req.sn not in EPMS:
        raise HTTPException(status_code=404, detail="EPM device not found.")
        
    if not check_device_ownership(api_id, req.sn, "epm"):
        raise SolisTenancyError("Access Denied: You do not own this EPM device.")
        
    epm = EPMS[req.sn].copy()
    mult = get_solar_multiplier()
    epm.update({
        "uAc1": 230.1,
        "uAc2": 230.5,
        "uAc3": 229.8,
        "iAc1": 15.2 * mult,
        "iAc2": 15.0 * mult,
        "iAc3": 15.3 * mult,
        "pEpmTotal": round(10.2 * mult, 3),
        "pEpmTotalStr": "kW",
        "eTotalBuy": 45.2,
        "eTotalSell": 120.8,
        "powerFactor": 0.99
    })
    return SolisResponse(data=epm)


@router.post("/epm/day", response_model=SolisResponse[Dict[str, Any]])
async def post_epm_day(req: EpmDayRequest, request: Request):
    api_id = request.state.api_id
    
    if req.sn not in EPMS:
        raise HTTPException(status_code=404, detail="EPM device not found.")
        
    if not check_device_ownership(api_id, req.sn, "epm"):
        raise SolisTenancyError("Access Denied: You do not own this EPM device.")
        
    return SolisResponse(data={
        "data_timestamp": [int(time.time()*1000)],
        "timeStr": [req.time],
        "u_ac1": [230.5],
        "e_total_buy": [45.2],
        "e_total_sell": [120.8]
    })
