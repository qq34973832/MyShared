from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    ADMIN = "admin"
    MERCHANT = "merchant"
    CONSUMER = "consumer"
    GUEST = "guest"


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_banned = Column(Boolean, default=False, index=True)
    ban_reason = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CONSUMER, index=True)
    
    # 权限和元数据
    permissions = Column(JSON, default=list)  # 权限列表
    metadata_ = Column(JSON, default=dict)    # 扩展数据
    
    # 关系
    merchant = relationship("Merchant", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    consumer = relationship("ConsumerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserPermission(BaseModel):
    """用户权限表"""
    __tablename__ = "user_permissions"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(String(100), nullable=False)
    
    __table_args__ = (UniqueConstraint('user_id', 'permission', name='uq_user_permission'),)
