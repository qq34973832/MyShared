from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 数据库
    database_url: str
    redis_url: str

    # JWT 和安全
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 系统配置
    debug: bool = False
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    auto_seed_data: bool = True

    # Celery
    celery_broker_url: str
    celery_result_backend: str

    # CORS - 使用 Field 和默认工厂函数
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Webhook
    webhook_secret: str
    webhook_timeout: int = 30
    webhook_retry_max: int = 3

    # 广告配置
    ad_pool_cache_ttl: int = 3600
    bidding_update_interval: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """获取全局配置实例"""
    return Settings()
