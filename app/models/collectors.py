from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CollectorListRequest(BaseModel):
    pageNo: str = Field(..., description="Page number.")
    pageSize: str = Field(..., description="Page size.")
    stationId: Optional[int] = Field(None, description="Station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="NMI.")

    @field_validator("pageNo")
    @classmethod
    def validate_page_no(cls, v: str) -> str:
        try:
            val = int(v)
            if val < 1:
                raise ValueError("pageNo must be greater than or equal to 1")
        except ValueError:
            raise ValueError("pageNo must be a valid integer string")
        return v

    @field_validator("pageSize")
    @classmethod
    def validate_page_size(cls, v: str) -> str:
        try:
            val = int(v)
            if val < 1 or val > 100:
                raise ValueError("pageSize must be between 1 and 100")
        except ValueError:
            raise ValueError("pageSize must be a valid integer string")
        return v

class CollectorDetailRequest(BaseModel):
    id: Optional[int] = Field(None, description="Collector Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Collector Serial Number.")

class BindCollectorRequest(BaseModel):
    sn: Optional[str] = Field(None, max_length=100)
    stationName: str = Field(..., max_length=100)
    capacity: str = Field(..., max_length=50)
    picName: Optional[str] = Field(None, max_length=100)
    latitude: Optional[str] = Field(None, max_length=50)
    longitude: Optional[str] = Field(None, max_length=50)
    dip: Optional[float] = None
    azimuth: Optional[float] = None
    money: Optional[str] = Field(None, max_length=10)
    addr: Optional[str] = Field(None, max_length=255)
    gdAreaCode: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = None
    offset: Optional[float] = None
    type: Optional[int] = None
    synchronizationType: Optional[int] = None
    installTime: Optional[str] = Field(None, max_length=50)
    module: Optional[int] = None
    installerEmail: Optional[str] = Field(None, max_length=100)
    installerMobile: Optional[str] = Field(None, max_length=50)
    nmiCode: Optional[str] = Field(None, max_length=50)

class UnbindCollectorRequest(BaseModel):
    sn: Optional[str] = Field(None, max_length=100)
    deleteInvert: int = Field(..., description="1 = delete inverters, 0 = keep.")
