from app.tasks import celery_app
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.ad_campaign import AdCampaign
from app.services.ad_pool import AdPoolService


@celery_app.task
def deliver_ads_to_consumer(consumer_id: int, tags: list):
    """将匹配的广告投放给消费者"""
    db = SessionLocal()
    try:
        # 将消费者添加到匿名池
        anonymous_id = AdPoolService.add_consumer_to_pool(tags, consumer_id)
        
        # 匹配符合标签的广告活动
        matched_campaigns = AdPoolService.match_campaigns_for_consumer(tags)
        
        # 这里可以进一步处理广告投放逻辑
        # TODO: 发送广告给消费者（通过 WebSocket、推送等）
    finally:
        db.close()


@celery_app.task
def sync_ad_campaigns_to_cache():
    """同步活跃的广告活动到缓存"""
    db = SessionLocal()
    try:
        from app.core.cache import Cache, CacheKey
        from datetime import datetime
        
        # 获取所有活跃的活动
        active_campaigns = db.query(AdCampaign).filter(
            AdCampaign.is_active == True,
            AdCampaign.status == "active"
        ).all()
        
        for campaign in active_campaigns:
            cache_key = f"{CacheKey.AD_PREFIX}{campaign.id}"
            Cache.set(cache_key, {
                "id": campaign.id,
                "name": campaign.name,
                "target_tags": campaign.target_tags,
                "daily_budget": campaign.daily_budget,
                "spent_budget": campaign.spent_budget,
            }, ex=3600)
    finally:
        db.close()
