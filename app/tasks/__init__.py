from celery import Celery
from app.core.config import get_settings

settings = get_settings()

# 创建 Celery 应用
celery_app = Celery(
    "myshared",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
