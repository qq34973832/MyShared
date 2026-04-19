from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[str]


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    events: List[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookLogResponse(BaseModel):
    id: int
    webhook_id: int
    event: str
    payload: dict
    status_code: Optional[int]
    is_success: bool
    retry_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookEventPayload(BaseModel):
    event: str
    data: dict
    timestamp: datetime
