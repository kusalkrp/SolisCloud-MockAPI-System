from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")

class SolisResponse(BaseModel, Generic[T]):
    """Standard SolisCloud API Response Wrapper"""
    success: bool = True
    code: str = "0"
    msg: str = "success"
    data: Optional[T] = None
