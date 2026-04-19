from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.db import Base


class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BaseModel(Base, TimestampMixin):
    """基础模型"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
