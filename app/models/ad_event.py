from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class AdEvent(BaseModel):
    """广告事件（曝光、点击等）"""
    __tablename__ = "ad_events"
    
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 事件类型
    event_type = Column(String(20), nullable=False)  # exposure, click, conversion
    event_count = Column(Integer, default=1)
    
    # 消费者匿名标识（保护隐私）
    anonymous_id = Column(String(100), nullable=True)  # 匿名哈希ID
    
    # 消耗
    cost = Column(Float, default=0)
    
    # 事件发生时间
    event_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    campaign = relationship("AdCampaign", back_populates="events")
    
    def __repr__(self):
        return f"<AdEvent campaign_id={self.campaign_id} type={self.event_type}>"
