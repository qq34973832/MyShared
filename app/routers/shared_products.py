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
