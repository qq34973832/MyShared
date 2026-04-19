from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MerchantBase(BaseModel):
    shop_name: str
    shop_description: Optional[str] = None
    shop_logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None


class MerchantCreate(MerchantBase):
    pass


class MerchantUpdate(BaseModel):
    shop_name: Optional[str] = None
    shop_description: Optional[str] = None
    shop_logo_url: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: int
    user_id: int
    is_verified: bool
    rating: float
    total_products: int
    total_reviews: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MerchantDetailResponse(MerchantResponse):
    business_license: Optional[str]
    settings: dict


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    merchant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
