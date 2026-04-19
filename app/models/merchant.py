from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Merchant(BaseModel):
    """商家表"""
    __tablename__ = "merchants"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    shop_name = Column(String(255), unique=True, nullable=False, index=True)
    shop_description = Column(String(1000), nullable=True)
    shop_logo_url = Column(String(500), nullable=True)
    shop_banner_url = Column(String(500), nullable=True)
    
    # 商家信息
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    
    # 营业资质
    business_license = Column(String(500), nullable=True)  # 营业执照URL
    is_verified = Column(Boolean, default=False)
    
    # 统计信息
    total_products = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # 平均评分（0-5）
    total_reviews = Column(Integer, default=0)
    
    # 扩展数据
    settings = Column(JSON, default=dict)
    
    # 关系
    owner = relationship("User", back_populates="merchant", uselist=False)
    categories = relationship("Category", back_populates="merchant", cascade="all, delete-orphan")
    products = relationship("SharedProduct", back_populates="merchant", cascade="all, delete-orphan")
    ad_campaigns = relationship("AdCampaign", back_populates="merchant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Merchant {self.shop_name}>"
