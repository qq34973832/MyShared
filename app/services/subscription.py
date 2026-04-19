from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.consumer import ConsumerProfile
from typing import Optional


class SubscriptionService:
    """订阅服务"""
    
    @staticmethod
    def subscribe(
        db: Session,
        consumer_id: int,
        subscription_type: str,
        merchant_id: Optional[int] = None,
        category_id: Optional[int] = None,
        product_id: Optional[int] = None
    ) -> Subscription:
        """创建订阅"""
        # 检查是否已存在
        existing = db.query(Subscription).filter(
            Subscription.consumer_id == consumer_id,
            Subscription.subscription_type == subscription_type,
            Subscription.merchant_id == merchant_id,
            Subscription.category_id == category_id,
            Subscription.product_id == product_id,
        ).first()
        
        if existing and existing.is_active:
            return existing
        
        # 创建新订阅
        subscription = Subscription(
            consumer_id=consumer_id,
            subscription_type=subscription_type,
            merchant_id=merchant_id,
            category_id=category_id,
            product_id=product_id,
            is_active=True
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
    
    @staticmethod
    def unsubscribe(db: Session, subscription_id: int) -> bool:
        """取消订阅"""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if subscription:
            subscription.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_consumer_subscriptions(db: Session, consumer_id: int) -> list:
        """获取消费者的所有订阅"""
        return db.query(Subscription).filter(
            Subscription.consumer_id == consumer_id,
            Subscription.is_active == True
        ).all()
    
    @staticmethod
    def get_subscribed_consumers(db: Session, merchant_id: int) -> list:
        """获取订阅该商家的消费者"""
        return db.query(Subscription).filter(
            Subscription.merchant_id == merchant_id,
            Subscription.subscription_type == "merchant",
            Subscription.is_active == True
        ).all()
