from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import verify_solis_signature
from app.models.base import SolisResponse
from app.models.epms import EpmDetailRequest
from app.core.security import (
    check_device_ownership,
    get_tenant_stations
)
from app.database.mock_db import WEATHER_SENSORS, get_solar_multiplier
from app.database.cache import weather_cache
from app.core.exceptions import SolisTenancyError

router = APIRouter(dependencies=[Depends(verify_solis_signature)])

@router.post("/weatherList", response_model=SolisResponse[Dict[str, Any]])
async def post_weather_list(request: Request):
    api_id = request.state.api_id
    tenant_stations = get_tenant_stations(api_id)
    
    records = []
    for r in WEATHER_SENSORS.values():
        if r["stationId"] in tenant_stations:
            records.append(r)
            
    return SolisResponse(data={"page": {"records": records, "total": len(records)}})


@router.post("/weatherDetail", response_model=SolisResponse[Dict[str, Any]])
async def post_weather_detail(req: EpmDetailRequest, request: Request):
    api_id = request.state.api_id
    
    if req.sn not in WEATHER_SENSORS:
        raise HTTPException(status_code=404, detail="Weather sensor not found.")
        
    if not check_device_ownership(api_id, req.sn, "weather"):
        raise SolisTenancyError("Access Denied: You do not own this weather sensor.")
    
    cached_val = weather_cache.get(req.sn)
    if cached_val is not None:
        return SolisResponse(data=cached_val)
        
    mult = get_solar_multiplier()
    payload = WEATHER_SENSORS[req.sn].copy()
    payload.update({
        "temp": round(22.5 + 8.0 * mult, 1),
        "humidity": 45.0,
        "windSpeed": 1.5,
        "totalR": round(800.0 * mult, 1),
        "directR": round(600.0 * mult, 1),
        "scatteredR": round(200.0 * mult, 1),
        "pvTemp": round(25.0 + 15.0 * mult, 1)
    })
    
    weather_cache.set(req.sn, payload)
    return SolisResponse(data=payload)
