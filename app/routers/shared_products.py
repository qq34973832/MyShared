from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.shared_product import SharedProduct, Bid
from app.models.merchant import Merchant
from app.schemas.shared_product import (
    SharedProductCreate, SharedProductResponse, SharedProductUpdate,
    BidCreate, BidResponse, BiddingResultResponse
)
from app.dependencies.auth import get_current_user
from app.dependencies.role import require_merchant
from app.services.bidding import BiddingService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[SharedProductResponse])
def list_products(
    category_id: int = Query(None, description="按分类筛选"),
    merchant_id: int = Query(None, description="按商户筛选"),
    keyword: str = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """公开的商品列表（支持按分类、商户、关键词筛选）"""
    q = db.query(SharedProduct).filter(SharedProduct.is_available == True)
    if category_id is not None:
        q = q.filter(SharedProduct.category_id == category_id)
    if merchant_id is not None:
        q = q.filter(SharedProduct.merchant_id == merchant_id)
    if keyword:
        q = q.filter(SharedProduct.name.contains(keyword))
    return q.order_by(SharedProduct.id.desc()).offset(skip).limit(limit).all()


@router.get("/my", response_model=list[SharedProductResponse])
def list_my_products(
    merchant: User = Depends(require_merchant),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """当前商户的商品列表"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return (
        db.query(SharedProduct)
        .filter(SharedProduct.merchant_id == merchant_info.id)
        .order_by(SharedProduct.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("", response_model=SharedProductResponse)
def create_product(
    product_in: SharedProductCreate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建商品"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    product = SharedProduct(
        merchant_id=merchant_info.id,
        category_id=product_in.category_id,
        name=product_in.name,
        sku=product_in.sku,
        description=product_in.description,
        original_price=product_in.original_price,
        current_price=product_in.current_price,
        stock=product_in.stock,
        image_urls=product_in.image_urls
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    merchant_info.total_products += 1
    db.commit()
    
    return product


@router.get("/{product_id}", response_model=SharedProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    product = db.query(SharedProduct).filter(SharedProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=SharedProductResponse)
def update_product(
    product_id: int,
    product_in: SharedProductUpdate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新商品"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    product = db.query(SharedProduct).filter(
        SharedProduct.id == product_id,
        SharedProduct.merchant_id == merchant_info.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product_in.name:
        product.name = product_in.name
    if product_in.description:
        product.description = product_in.description
    if product_in.current_price:
        product.current_price = product_in.current_price
    if product_in.stock is not None:
        product.stock = product_in.stock
    
    db.commit()
    db.refresh(product)
    return product


@router.post("/bids", response_model=BidResponse)
def place_bid(
    bid_in: BidCreate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """商家出价"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    product = db.query(SharedProduct).filter(
        SharedProduct.id == bid_in.product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    bid = BiddingService.place_bid(
        db,
        bid_in.product_id,
        merchant_info.id,
        bid_in.bid_price
    )
    
    return bid


@router.get("/bids/my", response_model=list[BidResponse])
def list_my_bids(
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db),
):
    """获取当前商户的所有出价记录"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return (
        db.query(Bid)
        .filter(Bid.merchant_id == merchant_info.id)
        .order_by(Bid.id.desc())
        .all()
    )


@router.get("/bids/{product_id}", response_model=BiddingResultResponse)
def get_bidding_result(product_id: int, db: Session = Depends(get_db)):
    """获取商品的竞价结果"""
    product = db.query(SharedProduct).filter(SharedProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    bids = BiddingService.get_bids_for_product(db, product_id)
    min_price = BiddingService.get_winning_price(db, product_id)
    
    return {
        "product_id": product.id,
        "product_name": product.name,
        "min_platform_price": min_price or product.current_price,
        "winning_merchant_id": bids[0].merchant_id if bids else product.merchant_id,
        "bids": [
            {
                "id": b.id,
                "product_id": b.product_id,
                "merchant_id": b.merchant_id,
                "bid_price": b.bid_price,
                "status": b.status,
                "created_at": b.created_at
            } for b in bids
        ]
    }
