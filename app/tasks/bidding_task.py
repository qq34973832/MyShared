from app.tasks import celery_app
from sqlalchemy.orm import Session
from app.core.db import SessionLocal


@celery_app.task
def update_product_bidding():
    """定期更新商品竞价和最低价"""
    db = SessionLocal()
    try:
        from app.models.shared_product import SharedProduct
        from app.services.bidding import BiddingService
        
        # 获取所有有竞价的商品
        products = db.query(SharedProduct).filter(
            SharedProduct.bids.any()
        ).all()
        
        for product in products:
            BiddingService.update_min_price(db, product.id)
    finally:
        db.close()


@celery_app.task
def cleanup_expired_bids():
    """清理过期的竞价"""
    db = SessionLocal()
    try:
        from app.models.shared_product import Bid
        from datetime import timedelta
        from datetime import datetime, timezone
        
        # 清理一周前的非活跃竞价
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        db.query(Bid).filter(
            Bid.status == "inactive",
            Bid.updated_at < cutoff
        ).delete()
        db.commit()
    finally:
        db.close()
