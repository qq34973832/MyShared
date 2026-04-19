from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class Comment(BaseModel):
    """评论"""
    __tablename__ = "comments"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("shared_products.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 评论内容
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    
    # 图片
    image_urls = Column(String, nullable=True)  # JSON string of URLs
    
    # 统计
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    # 状态
    is_verified_purchase = Column(Integer, default=0)  # 是否为已验证购买
    
    # 关系
    user = relationship("User", back_populates="comments")
    product = relationship("SharedProduct", back_populates="comments")
    merchant = relationship("Merchant")

    def __repr__(self):
        return f"<Comment user_id={self.user_id} rating={self.rating}>"
