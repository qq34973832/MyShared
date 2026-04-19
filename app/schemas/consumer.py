from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConsumerProfileBase(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: List[str] = []


class ConsumerProfileCreate(ConsumerProfileBase):
    pass


class ConsumerProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ConsumerProfileResponse(ConsumerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    subscription_type: str  # merchant, category, product, news
    merchant_id: Optional[int] = None
    category_id: Optional[int] = None
    product_id: Optional[int] = None


class SubscriptionResponse(BaseModel):
    id: int
    subscription_type: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagPoolRequest(BaseModel):
    tags: List[str]
