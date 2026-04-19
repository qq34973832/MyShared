from app.tasks import celery_app
from app.core.redis import redis_client
from datetime import datetime, timedelta, timezone


@celery_app.task
def check_webhook_health():
    """定期检查 Webhook 心跳"""
    db_session = None
    try:
        from app.core.db import SessionLocal
        from app.models.webhook import Webhook, WebhookLog
        
        db_session = SessionLocal()
        
        webhooks = db_session.query(Webhook).filter(Webhook.is_active == True).all()
        
        for webhook in webhooks:
            # 检查最近的成功记录
            recent_success = db_session.query(WebhookLog).filter(
                WebhookLog.webhook_id == webhook.id,
                WebhookLog.is_success == True,
                WebhookLog.created_at > datetime.now(timezone.utc) - timedelta(hours=1)
            ).first()
            
            # 如果1小时内没有成功记录，标记为不健康
            health_key = f"webhook:health:{webhook.id}"
            if not recent_success:
                redis_client.setex(health_key, 3600, "unhealthy")
            else:
                redis_client.setex(health_key, 3600, "healthy")
    finally:
        if db_session:
            db_session.close()


@celery_app.task
def cleanup_old_webhook_logs():
    """清理旧的 Webhook 日志（保留30天）"""
    db_session = None
    try:
        from app.core.db import SessionLocal
        from app.models.webhook import WebhookLog
        
        db_session = SessionLocal()
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        db_session.query(WebhookLog).filter(
            WebhookLog.created_at < cutoff_date
        ).delete()
        db_session.commit()
    finally:
        if db_session:
            db_session.close()
