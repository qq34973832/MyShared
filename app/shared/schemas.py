"""通用共享 Pydantic Schemas"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BaseResponse(BaseModel):
    """基础响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    """分页响应"""
    total: int
    skip: int
    limit: int
    items: list


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    details: Optional[dict] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    code: int = 200
    message: str = "Success"
    data: Optional[dict] = None
