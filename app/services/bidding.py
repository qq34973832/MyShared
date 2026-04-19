from sqlalchemy.orm import Session
from app.models.shared_product import SharedProduct, Bid
from app.core.cache import Cache, CacheKey


class BiddingService:
    """竞价服务"""
    
    @staticmethod
    def place_bid(db: Session, product_id: int, merchant_id: int, bid_price: float) -> Bid:
        """商家出价"""
        # 创建竞价记录
        bid = Bid(
            product_id=product_id,
            merchant_id=merchant_id,
            bid_price=bid_price,
            status="active"
        )
        db.add(bid)
        db.commit()
        db.refresh(bid)
        
        # 更新平台最低价
        BiddingService.update_min_price(db, product_id)
        
        # 清除缓存
        Cache.delete(CacheKey.PRODUCT_MIN_PRICE.format(product_id))
        Cache.delete(CacheKey.PRODUCT_BIDDING.format(product_id))
        
        return bid
    
    @staticmethod
    def update_min_price(db: Session, product_id: int):
        """更新平台最低价"""
        # 获取该商品的所有有效竞价
        product = db.query(SharedProduct).filter(SharedProduct.id == product_id).first()
        if not product:
            return
        
        bids = db.query(Bid).filter(
            Bid.product_id == product_id,
            Bid.status == "active"
        ).all()
        
        if bids:
            # 找最低价
            min_price = min([bid.bid_price for bid in bids])
            product.min_platform_price = min_price
            db.commit()
    
    @staticmethod
    def get_bids_for_product(db: Session, product_id: int) -> list:
        """获取商品的所有竞价"""
        cache_key = CacheKey.PRODUCT_BIDDING.format(product_id)
        
        # 尝试从缓存获取
        bids = Cache.get(cache_key)
        if bids:
            return bids
        
        # 从数据库查询
        bids = db.query(Bid).filter(
            Bid.product_id == product_id,
            Bid.status == "active"
        ).order_by(Bid.bid_price).all()
        
        # 缓存结果
        Cache.set(cache_key, [
            {
                "merchant_id": b.merchant_id,
                "bid_price": b.bid_price,
                "status": b.status
            } for b in bids
        ], ex=300)
        
        return bids
    
    @staticmethod
    def get_winning_price(db: Session, product_id: int) -> float:
        """获取赢价（平台最低价）"""
        product = db.query(SharedProduct).filter(SharedProduct.id == product_id).first()
        return product.min_platform_price if product else None
