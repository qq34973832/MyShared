from app.tasks import celery_app
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
import requests
import json
from datetime import datetime


@celery_app.task
def send_webhook_event(webhook_id: int, event: str, payload: dict):
    """发送出站 Webhook"""
    db = SessionLocal()
    try:
        from app.models.webhook import Webhook, WebhookLog
        from app.utils.webhook_signature import sign_webhook
        
        webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook or not webhook.is_active:
            return
        
        # 检查事件是否在列表中
        if event not in webhook.events:
            return
        
        # 创建签名
        signature = sign_webhook(payload, webhook.secret)
        
        # 发送请求
        headers = {
            "X-Webhook-Signature": signature,
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(
                webhook.url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 记录日志
            log = WebhookLog(
                webhook_id=webhook_id,
                event=event,
                payload=payload,
                status_code=response.status_code,
                response_body=response.text[:500],
                is_success=response.status_code == 200,
            )
            db.add(log)
            db.commit()
            
        except requests.Timeout:
            log = WebhookLog(
                webhook_id=webhook_id,
                event=event,
                payload=payload,
                is_success=False,
                error_message="Request timeout"
            )
            db.add(log)
            db.commit()
        except Exception as e:
            log = WebhookLog(
                webhook_id=webhook_id,
                event=event,
                payload=payload,
                is_success=False,
                error_message=str(e)[:500]
            )
            db.add(log)
            db.commit()
    finally:
        db.close()


@celery_app.task
def retry_failed_webhooks():
    """重试失败的 Webhook"""
    db = SessionLocal()
    try:
        from app.models.webhook import WebhookLog
        
        # 获取失败且重试次数少于3的日志
        failed_logs = db.query(WebhookLog).filter(
            WebhookLog.is_success == False,
            WebhookLog.retry_count < 3
        ).limit(100).all()
        
        for log in failed_logs:
            # 重试发送
            send_webhook_event.delay(
                log.webhook_id,
                log.event,
                log.payload
            )
            log.retry_count += 1
            db.commit()
    finally:
        db.close()
