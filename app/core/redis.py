import redis
from app.core.config import get_settings

settings = get_settings()

# 创建 Redis 客户端
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis():
    """获取 Redis 客户端"""
    return redis_client


def redis_set(key: str, value: str, ex: int = None):
    """设置 Redis 值"""
    redis_client.set(key, value, ex=ex)


def redis_get(key: str):
    """获取 Redis 值"""
    return redis_client.get(key)


def redis_delete(key: str):
    """删除 Redis 值"""
    redis_client.delete(key)


def redis_incr(key: str):
    """自增"""
    return redis_client.incr(key)


def redis_expire(key: str, seconds: int):
    """设置过期时间"""
    redis_client.expire(key, seconds)
