from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.category import Category
from app.schemas.merchant import (
    MerchantCreate, MerchantResponse, MerchantUpdate, MerchantDetailResponse,
    CategoryCreate, CategoryResponse, CategoryUpdate
)
from app.dependencies.auth import get_current_user
from app.dependencies.role import require_merchant

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.post("/register", response_model=MerchantResponse)
def register_merchant(
    merchant_in: MerchantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家注册并自动创建店铺"""
    # 检查是否已注册
    existing = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant already registered")
    
    # 检查店铺名称是否重复
    existing_shop = db.query(Merchant).filter(
        Merchant.shop_name == merchant_in.shop_name
    ).first()
    if existing_shop:
        raise HTTPException(status_code=400, detail="Shop name already exists")
    
    # 创建商家和店铺
    merchant = Merchant(
        user_id=current_user.id,
        shop_name=merchant_in.shop_name,
        shop_description=merchant_in.shop_description,
        shop_logo_url=merchant_in.shop_logo_url,
        contact_phone=merchant_in.contact_phone,
        contact_email=merchant_in.contact_email,
        address=merchant_in.address
    )
    
    # 更新用户角色
    current_user.role = UserRole.MERCHANT
    
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    
    return merchant


@router.get("/me", response_model=MerchantDetailResponse)
def get_my_merchant(
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取当前商家的店铺信息"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant_info


@router.put("/me", response_model=MerchantResponse)
def update_my_merchant(
    merchant_in: MerchantUpdate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新当前商家的店铺信息"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    # 更新字段
    if merchant_in.shop_name:
        # 检查新名称是否已被占用
        existing = db.query(Merchant).filter(
            Merchant.shop_name == merchant_in.shop_name,
            Merchant.id != merchant_info.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Shop name already exists")
        merchant_info.shop_name = merchant_in.shop_name
    
    if merchant_in.shop_description:
        merchant_info.shop_description = merchant_in.shop_description
    if merchant_in.shop_logo_url:
        merchant_info.shop_logo_url = merchant_in.shop_logo_url
    if merchant_in.contact_phone:
        merchant_info.contact_phone = merchant_in.contact_phone
    if merchant_in.contact_email:
        merchant_info.contact_email = merchant_in.contact_email
    if merchant_in.address:
        merchant_info.address = merchant_in.address
    
    db.commit()
    db.refresh(merchant_info)
    return merchant_info


@router.get("/{merchant_id}", response_model=MerchantDetailResponse)
def get_merchant(
    merchant_id: int,
    db: Session = Depends(get_db)
):
    """获取商家详情"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建分类"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    category = Category(
        merchant_id=merchant_info.id,
        name=category_in.name,
        slug=category_in.slug,
        description=category_in.description,
        parent_id=category_in.parent_id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    merchant: User = Depends(require_merchant),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return db.query(Category).filter(
        Category.merchant_id == merchant_info.id
    ).offset(skip).limit(limit).all()


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新分类"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.merchant_id == merchant_info.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 更新字段
    if category_in.name:
        category.name = category_in.name
    if category_in.slug:
        category.slug = category_in.slug
    if category_in.description:
        category.description = category_in.description
    if category_in.parent_id is not None:
        category.parent_id = category_in.parent_id
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """删除分类"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.merchant_id == merchant_info.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
