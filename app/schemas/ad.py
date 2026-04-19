from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AdCampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_tags: List[str]
    daily_budget: float
    total_budget: float
    start_date: datetime
    end_date: datetime


class AdCampaignCreate(AdCampaignBase):
    pass


class AdCampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_tags: Optional[List[str]] = None
    daily_budget: Optional[float] = None
    status: Optional[str] = None


class AdCampaignResponse(AdCampaignBase):
    id: int
    merchant_id: int
    status: str
    spent_budget: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdEventResponse(BaseModel):
    id: int
    campaign_id: int
    event_type: str
    event_count: int
    cost: float
    event_time: datetime
    
    class Config:
        from_attributes = True


class AdAnalyticsResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    exposure_count: int  # 曝光数
    click_count: int     # 点击数
    ctr: float          # 点击率 (click_count / exposure_count)
    ppc: float          # 单次点击成本 (spent / click_count)
    spent_budget: float
    daily_budget: float
    remaining_budget: float


class AnonymousAdPoolRequest(BaseModel):
    tags: List[str]
