from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ConsumerProfile(BaseModel):
    """消费者档案"""
    __tablename__ = "consumer_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # 匿名广告池标签（用于隐私保护）
    tags = Column(JSON, default=list)  # ["电子产品", "运动", "女性"]
    
    # 偏好设置
    preferences = Column(JSON, default=dict)  # {"language": "zh", "currency": "CNY"}
    
    # 关系
    user = relationship("User", back_populates="consumer", uselist=False)
    subscriptions = relationship("Subscription", back_populates="consumer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ConsumerProfile user_id={self.user_id}>"

    def __str__(self):
        return self.nickname or f"Consumer #{self.user_id}"
