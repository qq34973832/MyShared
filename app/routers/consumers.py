from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.consumer import ConsumerProfile
from app.models.merchant import Merchant
from app.schemas.consumer import (
    ConsumerProfileCreate, ConsumerProfileResponse, ConsumerProfileUpdate,
    SubscriptionCreate, SubscriptionResponse
)
from app.dependencies.auth import get_current_user
from app.services.subscription import SubscriptionService
from app.services.ad_pool import AdPoolService

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.post("/profile", response_model=ConsumerProfileResponse)
def create_consumer_profile(
    profile_in: ConsumerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建消费者档案"""
    existing = db.query(ConsumerProfile).filter(
        ConsumerProfile.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Consumer profile already exists")
    
    profile = ConsumerProfile(
        user_id=current_user.id,
        nickname=profile_in.nickname,
        avatar_url=profile_in.avatar_url,
        tags=profile_in.tags
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/profile", response_model=ConsumerProfileResponse)
def get_consumer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取消费者档案"""
    profile = db.query(ConsumerProfile).filter(
        ConsumerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Consumer profile not found")
    
    return profile


@router.put("/profile", response_model=ConsumerProfileResponse)
def update_consumer_profile(
    profile_in: ConsumerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新消费者档案"""
    profile = db.query(ConsumerProfile).filter(
        ConsumerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Consumer profile not found")
    
    if profile_in.nickname:
        profile.nickname = profile_in.nickname
    if profile_in.avatar_url:
        profile.avatar_url = profile_in.avatar_url
    if profile_in.tags is not None:
        profile.tags = profile_in.tags
    
    db.commit()
    db.refresh(profile)
    
    # 如果更新了标签，将消费者添加到广告池
    if profile_in.tags is not None:
        AdPoolService.add_consumer_to_pool(profile_in.tags, current_user.id)
    
    return profile


@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(
    sub_in: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建订阅"""
    profile = db.query(ConsumerProfile).filter(
        ConsumerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Consumer profile not found")
    
    subscription = SubscriptionService.subscribe(
        db,
        profile.id,
        sub_in.subscription_type,
        sub_in.merchant_id,
        sub_in.category_id,
        sub_in.product_id
    )
    
    return subscription


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取消费者的订阅列表"""
    profile = db.query(ConsumerProfile).filter(
        ConsumerProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Consumer profile not found")
    
    return SubscriptionService.get_consumer_subscriptions(db, profile.id)


@router.delete("/subscriptions/{subscription_id}", status_code=204)
def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消订阅"""
    success = SubscriptionService.unsubscribe(db, subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
