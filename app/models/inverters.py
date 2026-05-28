from typing import Optional
from pydantic import BaseModel, Field, field_validator

class InverterListRequest(BaseModel):
    pageNo: str = Field(..., description="Page number to return, default 1.")
    pageSize: str = Field(..., description="Number of records per page (default 20, max 100).")
    stationId: Optional[int] = Field(None, description="Query inverters under a specific power station ID.")
    nmiCode: Optional[str] = Field(None, max_length=50, description="Query inverters matching a specific NMI.")

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

class InverterDetailRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique Inverter Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Inverter Serial Number.")

class InverterDayRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique Inverter Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Inverter Serial Number.")
    time: str = Field(..., max_length=50, description="Query day format 'yyyy-MM-dd'.")
    money: str = Field(..., max_length=10, description="Revenue calculation currency (e.g. EUR, CNY).")
    timeZone: int = Field(..., description="Local device timezone index (e.g. 8).")

class InverterMonthRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique Inverter Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Inverter Serial Number.")
    month: str = Field(..., max_length=50, description="Query month format 'yyyy-MM'.")
    money: str = Field(..., max_length=10, description="Currency (e.g. AUD).")

class InverterYearRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique Inverter Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Inverter Serial Number.")
    year: str = Field(..., max_length=50, description="Query year format 'yyyy'.")
    money: str = Field(..., max_length=10, description="Currency.")

class InverterAllRequest(BaseModel):
    id: Optional[int] = Field(None, description="Unique Inverter Database ID.")
    sn: Optional[str] = Field(None, max_length=100, description="Inverter Serial Number.")
    money: str = Field(..., max_length=10, description="Currency.")

class BindInverterRequest(BaseModel):
    sn: str = Field(..., max_length=255, description="Comma separated inverter SNs.")
    id: Optional[int] = None
    nmiCode: Optional[str] = Field(None, max_length=50)
