from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Subscription(BaseModel):
    """订阅关系"""
    __tablename__ = "subscriptions"
    
    consumer_id = Column(Integer, ForeignKey("consumer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("shared_products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 订阅类型
    subscription_type = Column(String(50), nullable=False)  # merchant, category, product, news
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 关系
    consumer = relationship("ConsumerProfile", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription consumer_id={self.consumer_id} type={self.subscription_type}>"
