"""
Common Response & Pagination Schemas
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)

class MessageResponse(BaseModel):
    message: str
    success: bool = True
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
