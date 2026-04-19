from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Webhook(BaseModel):
    """Webhook 配置"""
    __tablename__ = "webhooks"
    
    # 基本信息
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    # 事件配置
    events = Column(JSON, default=list)  # ["user.created", "order.paid"]
    
    # 认证
    secret = Column(String(255), nullable=False)

    # 过期时间（为空表示永久有效）
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 关系
    logs = relationship("WebhookLog", back_populates="webhook", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Webhook {self.name}>"

    def __str__(self):
        return self.name


class WebhookLog(BaseModel):
    """Webhook 日志（用于调试和审计）"""
    __tablename__ = "webhook_logs"
    
    webhook_id = Column(Integer, ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 事件信息
    event = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    
    # 响应
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    
    # 重试
    retry_count = Column(Integer, default=0)
    is_success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # 关系
    webhook = relationship("Webhook", back_populates="logs")
    
    def __repr__(self):
        return f"<WebhookLog webhook_id={self.webhook_id} event={self.event}>"
