from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SharedProductBase(BaseModel):
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    original_price: float
    current_price: float
    stock: int


class SharedProductCreate(SharedProductBase):
    image_urls: List[str] = []


class SharedProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    original_price: Optional[float] = None
    current_price: Optional[float] = None
    stock: Optional[int] = None
    image_urls: Optional[List[str]] = None


class SharedProductResponse(SharedProductBase):
    id: int
    merchant_id: int
    current_price: float
    min_platform_price: Optional[float]
    sales_count: int
    rating: float
    review_count: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BidCreate(BaseModel):
    product_id: int
    bid_price: float
    bid_amount: Optional[float] = None


class BidResponse(BaseModel):
    id: int
    product_id: int
    merchant_id: int
    bid_price: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BiddingResultResponse(BaseModel):
    product_id: int
    product_name: str
    min_platform_price: float
    winning_merchant_id: int
    bids: List[BidResponse]
