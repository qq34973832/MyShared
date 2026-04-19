from sqlalchemy.orm import Session
from app.models.user import User
from app.models.subscription import Subscription
from typing import List
import json


class NotificationService:
    """通知和推送服务"""
    
    @staticmethod
    def notify_merchant_new_subscribers(db: Session, merchant_id: int):
        """通知商家有新的订阅者"""
        pass
    
    @staticmethod
    def notify_subscribers_new_product(db: Session, merchant_id: int, product_name: str):
        """通知订阅者有新商品"""
        subscriptions = db.query(Subscription).filter(
            Subscription.merchant_id == merchant_id,
            Subscription.subscription_type == "merchant",
            Subscription.is_active == True
        ).all()
        
        # 批量发送通知（实际应用中可调用 WebSocket 或推送服务）
        for sub in subscriptions:
            consumer = sub.consumer
            # TODO: 发送推送通知
            pass
    
    @staticmethod
    def notify_subscribers_price_drop(db: Session, product_id: int, old_price: float, new_price: float):
        """通知订阅者商品降价"""
        pass
    
    @staticmethod
    def notify_comment_reply(db: Session, comment_id: int, reply_content: str):
        """通知用户评论有回复"""
        pass
    
    @staticmethod
    def notify_chat_message(db: Session, user_id: int, merchant_id: int, message: str):
        """通知用户有新聊天消息（通过 WebSocket）"""
        pass
    
    @staticmethod
    def send_email_notification(email: str, subject: str, content: str):
        """发送邮件通知"""
        # TODO: 集成邮件服务（如 SendGrid、AWS SES）
        pass
    
    @staticmethod
    def send_sms_notification(phone: str, message: str):
        """发送短信通知"""
        # TODO: 集成短信服务（如阿里云、腾讯云）
        pass
