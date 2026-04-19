from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class APIToken(BaseModel):
    """开放 API Token"""
    __tablename__ = "api_tokens"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token 信息
    token = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    
    # 权限范围
    scopes = Column(JSON, default=list)  # ["user:read", "product:write"]
    
    # 过期时间
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False)
    
    # IP 限制（可选）
    allowed_ips = Column(JSON, default=list)  # 允许的IP列表
    
    # 最后使用
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="api_tokens")
    
    def __repr__(self):
        return f"<APIToken token={self.token[:10]}...>"
