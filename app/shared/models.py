"""通用共享基类模型"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.db import Base


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """软删除混入类"""
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class BaseSharedModel(Base, TimestampMixin):
    """基础共享模型"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
