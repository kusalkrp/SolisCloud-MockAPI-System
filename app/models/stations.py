from typing import Optional
from pydantic import BaseModel, Field

class StationListRequest(BaseModel):
    pageNo: int = Field(..., ge=1, description="Page number.")
    pageSize: int = Field(..., ge=1, le=100, description="Page size.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")

class StationDetailRequest(BaseModel):
    id: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI Code.")

class StationDayRequest(BaseModel):
    id: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")
    time: str = Field(..., max_length=50, description="Format 'yyyy-MM-dd'.")
    money: str = Field(..., max_length=10, description="Currency.")
    timeZone: int = Field(..., description="Timezone index.")

class StationMonthRequest(BaseModel):
    id: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")
    month: str = Field(..., max_length=50, description="Format 'yyyy-MM'.")
    money: str = Field(..., max_length=10, description="Currency.")
    timeZone: int = Field(..., description="Timezone.")

class StationYearRequest(BaseModel):
    id: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")
    year: str = Field(..., max_length=50, description="Format 'yyyy'.")
    money: str = Field(..., max_length=10, description="Currency.")
    timeZone: int = Field(..., description="Timezone.")

class StationAllRequest(BaseModel):
    id: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")
    money: str = Field(..., max_length=10, description="Currency.")
    timeZone: int = Field(..., description="Timezone.")

class AddStationRequest(BaseModel):
    stationName: str = Field(..., max_length=100)
    capacity: str = Field(..., max_length=50)
    money: str = Field(..., max_length=10)
    addr: str = Field(..., max_length=255)
    price: str = Field(..., max_length=50)
    inverterSn: Optional[str] = Field(None, max_length=100)
    collectorSn: Optional[str] = Field(None, max_length=100)
    userId: Optional[int] = None
    mobile: Optional[str] = Field(None, max_length=50)
    latitude: Optional[str] = Field(None, max_length=50)
    Integeritude: Optional[str] = Field(None, max_length=50)
    dip: Optional[float] = None
    azimuth: Optional[float] = None
    gdAreaCode: Optional[str] = Field(None, max_length=50)
    countryStr: Optional[int] = None
    regionStr: Optional[int] = None
    cityStr: Optional[int] = None
    offset: Optional[float] = None
    module: Optional[str] = Field(None, max_length=50)
    installerEmail: Optional[str] = Field(None, max_length=100)
    installerMobile: Optional[str] = Field(None, max_length=50)
    nmiCode: Optional[int] = None

class UpdateStationRequest(BaseModel):
    id: Optional[int] = None
    stationName: str = Field(..., max_length=100)
    capacity: str = Field(..., max_length=50)
    price: float
    addr: str = Field(..., max_length=255)
    nmiCode: Optional[str] = Field(None, max_length=50)
