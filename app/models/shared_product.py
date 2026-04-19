from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SharedProduct(BaseModel):
    """共享商品（支持多商家竞价）"""
    __tablename__ = "shared_products"
    
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    
    # 基本信息
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # 商品图片
    image_urls = Column(JSON, default=list)
    
    # 价格
    original_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)  # 该商家的价格
    min_platform_price = Column(Float, nullable=True)  # 平台最低价
    
    # 库存
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    
    # 统计
    sales_count = Column(Integer, default=0)
    rating = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    
    # 扩展数据
    metadata_ = Column(JSON, default=dict)
    
    # 关系
    merchant = relationship("Merchant", back_populates="products")
    category = relationship("Category", back_populates="products")
    bids = relationship("Bid", back_populates="product", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SharedProduct {self.name}>"

    def __str__(self):
        return self.name


class Bid(BaseModel):
    """商家竞价"""
    __tablename__ = "bids"
    
    product_id = Column(Integer, ForeignKey("shared_products.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 竞价价格
    bid_price = Column(Float, nullable=False)
    status = Column(String(20), default="active")  # active, inactive
    
    # 其他信息
    bid_amount = Column(Float, nullable=True)  # 总竞价金额
    
    # 关系
    product = relationship("SharedProduct", back_populates="bids")
    merchant = relationship("Merchant")
    
    def __repr__(self):
        return f"<Bid product_id={self.product_id} price={self.bid_price}>"
