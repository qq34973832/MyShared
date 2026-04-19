from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AdCampaign(BaseModel):
    """广告活动"""
    __tablename__ = "ad_campaigns"
    
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 基本信息
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # 投放设置
    target_tags = Column(JSON, default=list)  # 目标标签 ["电子产品", "女性"]
    daily_budget = Column(Float, nullable=False)  # 日预算
    total_budget = Column(Float, nullable=False)  # 总预算
    spent_budget = Column(Float, default=0)      # 已消耗
    
    # 时间
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # 状态
    status = Column(String(20), default="draft")  # draft, active, paused, ended
    is_active = Column(Boolean, default=False)
    
    # 关系 (延迟导入以避免循环导入)
    merchant = relationship("Merchant", back_populates="ad_campaigns")
    events = relationship("AdEvent", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdCampaign {self.name}>"


# 导入 AdEvent
from app.models.ad_event import AdEvent  # noqa: E402, F401
