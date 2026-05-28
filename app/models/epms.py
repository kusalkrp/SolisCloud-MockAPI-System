from pydantic import BaseModel, Field

class EpmDetailRequest(BaseModel):
    sn: str = Field(..., max_length=100)

class EpmDayRequest(BaseModel):
    sn: str = Field(..., max_length=100)
    searchinfo: str = Field(..., max_length=255, description="Fields to retrieve (e.g. u_ac1,e_total_buy).")
    time: str = Field(..., max_length=50)
    timeZone: int
