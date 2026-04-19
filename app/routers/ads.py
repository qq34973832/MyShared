from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.ad_campaign import AdCampaign
from app.schemas.ad import (
    AdCampaignCreate, AdCampaignResponse, AdCampaignUpdate,
    AdAnalyticsResponse, AnonymousAdPoolRequest
)
from app.dependencies.auth import get_current_user
from app.dependencies.role import require_merchant
from app.services.ad_pool import AdPoolService
from app.services.analytics import AnalyticsService
from app.models.merchant import Merchant

router = APIRouter(prefix="/ads", tags=["ads"])


@router.post("/campaigns", response_model=AdCampaignResponse)
def create_ad_campaign(
    campaign_in: AdCampaignCreate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建广告活动"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    campaign = AdCampaign(
        merchant_id=merchant_info.id,
        name=campaign_in.name,
        description=campaign_in.description,
        target_tags=campaign_in.target_tags,
        daily_budget=campaign_in.daily_budget,
        total_budget=campaign_in.total_budget,
        start_date=campaign_in.start_date,
        end_date=campaign_in.end_date,
        status="draft"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=AdCampaignResponse)
def get_ad_campaign(
    campaign_id: int,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取广告活动"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    campaign = db.query(AdCampaign).filter(
        AdCampaign.id == campaign_id,
        AdCampaign.merchant_id == merchant_info.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.get("/analytics/{campaign_id}", response_model=AdAnalyticsResponse)
def get_campaign_analytics(
    campaign_id: int,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取广告效果报告"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    campaign = db.query(AdCampaign).filter(
        AdCampaign.id == campaign_id,
        AdCampaign.merchant_id == merchant_info.id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    analytics = AnalyticsService.get_campaign_stats(db, campaign_id)
    return analytics


@router.post("/pool/join")
def join_anonymous_pool(
    pool_request: AnonymousAdPoolRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """消费者加入匿名广告池"""
    anonymous_id = AdPoolService.add_consumer_to_pool(pool_request.tags, current_user.id)
    
    return {
        "anonymous_id": anonymous_id,
        "message": "Successfully joined the ad pool"
    }


@router.post("/pool/leave")
def leave_anonymous_pool(
    anonymous_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """消费者离开匿名广告池"""
    AdPoolService.remove_consumer_from_pool(anonymous_id)
    
    return {
        "message": "Successfully left the ad pool"
    }
