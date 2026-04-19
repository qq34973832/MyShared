from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    rating: int  # 1-5
    title: Optional[str] = None
    content: str
    image_urls: Optional[str] = None


class CommentCreate(CommentBase):
    product_id: int


class CommentUpdate(BaseModel):
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None


class CommentResponse(CommentBase):
    id: int
    user_id: int
    product_id: int
    merchant_id: int
    is_verified_purchase: bool
    helpful_count: int
    unhelpful_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
