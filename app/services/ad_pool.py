from sqlalchemy.orm import Session
from app.models.ad_campaign import AdCampaign, AdEvent
from app.core.cache import Cache, CacheKey
from typing import List, Dict
import hashlib
from datetime import datetime


class AdPoolService:
    """匿名广告池服务（保护消费者隐私）"""
    
    @staticmethod
    def add_consumer_to_pool(tags: List[str], consumer_id: int) -> str:
        """将消费者添加到匿名池
        
        返回匿名ID（哈希值，不可逆）
        """
        # 生成匿名ID：哈希 consumer_id + timestamp
        anonymous_id = hashlib.sha256(
            f"{consumer_id}:{datetime.utcnow().timestamp()}".encode()
        ).hexdigest()[:32]
        
        # 缓存标签到匿名ID的映射（不包含消费者ID）
        pool_key = CacheKey.AD_POOL.format(anonymous_id)
        Cache.set(pool_key, {"tags": tags}, ex=86400)  # 24小时
        
        return anonymous_id
    
    @staticmethod
    def match_campaigns_for_consumer(tags: List[str]) -> List[int]:
        """根据消费者标签匹配广告活动
        
        返回匹配的广告活动ID列表
        """
        matched_campaigns = []
        
        # 从缓存中扫描所有活跃活动
        keys = Cache.redis_client.keys(f"{CacheKey.AD_PREFIX}*")
        for key in keys:
            campaign_data = Cache.get(key)
            if campaign_data and isinstance(campaign_data, dict):
                # 检查标签匹配
                target_tags = campaign_data.get("target_tags", [])
                if any(tag in tags for tag in target_tags):
                    campaign_id = int(key.split(":")[-1])
                    if campaign_id not in matched_campaigns:
                        matched_campaigns.append(campaign_id)
        
        return matched_campaigns
    
    @staticmethod
    def record_exposure(db: Session, campaign_id: int, anonymous_id: str, cost: float = 0.1):
        """记录广告曝光"""
        event = AdEvent(
            campaign_id=campaign_id,
            event_type="exposure",
            event_count=1,
            anonymous_id=anonymous_id,
            cost=cost
        )
        db.add(event)
        db.commit()
        
        # 更新统计缓存
        stats_key = CacheKey.AD_STATS.format(campaign_id)
        stats = Cache.get(stats_key) or {"exposure": 0, "click": 0, "spent": 0}
        stats["exposure"] += 1
        stats["spent"] += cost
        Cache.set(stats_key, stats, ex=86400)
    
    @staticmethod
    def record_click(db: Session, campaign_id: int, anonymous_id: str, cost: float = 0.5):
        """记录广告点击"""
        event = AdEvent(
            campaign_id=campaign_id,
            event_type="click",
            event_count=1,
            anonymous_id=anonymous_id,
            cost=cost
        )
        db.add(event)
        db.commit()
        
        # 更新统计缓存
        stats_key = CacheKey.AD_STATS.format(campaign_id)
        stats = Cache.get(stats_key) or {"exposure": 0, "click": 0, "spent": 0}
        stats["click"] += 1
        stats["spent"] += cost
        Cache.set(stats_key, stats, ex=86400)
    
    @staticmethod
    def remove_consumer_from_pool(anonymous_id: str):
        """从匿名池移除消费者"""
        pool_key = CacheKey.AD_POOL.format(anonymous_id)
        Cache.delete(pool_key)
