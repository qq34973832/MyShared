from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class APITokenCreate(BaseModel):
    name: Optional[str] = None
    scopes: List[str]
    expires_at: Optional[datetime] = None
    allowed_ips: Optional[List[str]] = None


class APITokenResponse(BaseModel):
    id: int
    name: Optional[str]
    token: str
    scopes: List[str]
    is_active: bool
    is_revoked: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APITokenListResponse(BaseModel):
    id: int
    name: Optional[str]
    token: str  # 只显示最后4位
    scopes: List[str]
    is_active: bool
    is_revoked: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class APITokenRevokeRequest(BaseModel):
    reason: Optional[str] = None


class OpenAPIRequest(BaseModel):
    """第三方 API 请求"""
    pass
