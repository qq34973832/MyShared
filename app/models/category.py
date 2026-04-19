from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Category(BaseModel):
    """商品分类（支持无限层级）"""

    __tablename__ = "categories"

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)

    # 关系
    merchant = relationship("Merchant", back_populates="categories")
    parent = relationship(
        "Category",
        remote_side="Category.id",
        backref="children",
        foreign_keys="Category.parent_id",
    )
    products = relationship(
        "SharedProduct", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category {self.name}>"

    def __str__(self):
        return self.name
