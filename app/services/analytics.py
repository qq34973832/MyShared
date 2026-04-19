from sqlalchemy.orm import Session
from app.models.ad_campaign import AdCampaign, AdEvent
from app.core.cache import Cache, CacheKey
from typing import Optional, Dict
from datetime import datetime


class AnalyticsService:
    """广告分析和报告服务"""
    
    @staticmethod
    def get_campaign_stats(db: Session, campaign_id: int) -> Dict:
        """获取活动的实时统计"""
        campaign = db.query(AdCampaign).filter(AdCampaign.id == campaign_id).first()
        if not campaign:
            return None
        
        # 尝试从缓存获取
        stats_key = CacheKey.AD_STATS.format(campaign_id)
        stats = Cache.get(stats_key)
        
        if not stats:
            # 从数据库统计
            exposure_events = db.query(AdEvent).filter(
                AdEvent.campaign_id == campaign_id,
                AdEvent.event_type == "exposure"
            ).all()
            
            click_events = db.query(AdEvent).filter(
                AdEvent.campaign_id == campaign_id,
                AdEvent.event_type == "click"
            ).all()
            
            exposure_count = len(exposure_events)
            click_count = len(click_events)
            spent = sum(e.cost for e in exposure_events + click_events)
            
            stats = {
                "exposure": exposure_count,
                "click": click_count,
                "spent": spent
            }
            Cache.set(stats_key, stats, ex=3600)
        
        # 计算 CTR 和 PPC
        exposure = stats.get("exposure", 0)
        click = stats.get("click", 0)
        spent = stats.get("spent", 0)
        
        ctr = (click / exposure * 100) if exposure > 0 else 0
        ppc = (spent / click) if click > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "exposure_count": exposure,
            "click_count": click,
            "ctr": round(ctr, 2),  # CTR%
            "ppc": round(ppc, 2),  # 单次点击成本
            "spent_budget": spent,
            "daily_budget": campaign.daily_budget,
            "remaining_budget": campaign.total_budget - campaign.spent_budget,
        }
    
    @staticmethod
    def get_merchant_campaigns_stats(db: Session, merchant_id: int) -> list:
        """获取商家的所有活动统计"""
        campaigns = db.query(AdCampaign).filter(
            AdCampaign.merchant_id == merchant_id
        ).all()
        
        stats_list = []
        for campaign in campaigns:
            stats = AnalyticsService.get_campaign_stats(db, campaign.id)
            if stats:
                stats_list.append(stats)
        
        return stats_list
    
    @staticmethod
    def get_ctr(exposure: int, click: int) -> float:
        """计算点击率"""
        if exposure == 0:
            return 0
        return round((click / exposure) * 100, 2)
    
    @staticmethod
    def get_ppc(spent: float, click: int) -> float:
        """计算单次点击成本"""
        if click == 0:
            return 0
        return round(spent / click, 2)
    
    @staticmethod
    def get_roi(revenue: float, spent: float) -> float:
        """计算投资回报率"""
        if spent == 0:
            return 0
        return round((revenue - spent) / spent * 100, 2)
