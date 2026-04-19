import fnmatch
import json
import time
from typing import Any, Optional

from redis.exceptions import RedisError

from app.core.redis import redis_client


class Cache:
    """缓存工具类"""

    redis_client = redis_client
    _memory_store: dict[str, tuple[Any, Optional[float]]] = {}

    @classmethod
    def _memory_get(cls, key: str):
        item = cls._memory_store.get(key)
        if not item:
            return None

        value, expires_at = item
        if expires_at and expires_at <= time.time():
            cls._memory_store.pop(key, None)
            return None
        return value

    @classmethod
    def _memory_set(cls, key: str, value: Any, ex: Optional[int] = None):
        expires_at = time.time() + ex if ex else None
        if not isinstance(value, str):
            value = str(value)
        cls._memory_store[key] = (value, expires_at)

    @classmethod
    def keys(cls, pattern: str) -> list[str]:
        try:
            return cls.redis_client.keys(pattern)
        except RedisError:
            return [
                key
                for key in list(cls._memory_store)
                if cls._memory_get(key) is not None and fnmatch.fnmatch(key, pattern)
            ]

    @staticmethod
    def get(key: str):
        """获取缓存"""
        try:
            value = Cache.redis_client.get(key)
        except RedisError:
            value = Cache._memory_get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    @staticmethod
    def set(key: str, value: Any, ex: int = 3600):
        """设置缓存"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        try:
            Cache.redis_client.set(key, value, ex=ex)
        except RedisError:
            Cache._memory_set(key, value, ex=ex)

    @staticmethod
    def delete(key: str):
        """删除缓存"""
        try:
            Cache.redis_client.delete(key)
        except RedisError:
            Cache._memory_store.pop(key, None)

    @staticmethod
    def delete_pattern(pattern: str):
        """删除匹配模式的缓存"""
        keys = Cache.keys(pattern)
        if keys:
            try:
                Cache.redis_client.delete(*keys)
            except RedisError:
                for key in keys:
                    Cache._memory_store.pop(key, None)

    @staticmethod
    def exists(key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return Cache.redis_client.exists(key) > 0
        except RedisError:
            return Cache._memory_get(key) is not None

    @staticmethod
    def incr(key: str, amount: int = 1) -> int:
        """自增"""
        try:
            return Cache.redis_client.incrby(key, amount)
        except RedisError:
            value = int(Cache._memory_get(key) or 0) + amount
            Cache._memory_set(key, str(value))
            return value

    @staticmethod
    def expire(key: str, seconds: int):
        """设置过期时间"""
        try:
            Cache.redis_client.expire(key, seconds)
        except RedisError:
            value = Cache._memory_get(key)
            if value is not None:
                Cache._memory_set(key, value, ex=seconds)


# 缓存键前缀
class CacheKey:
    """缓存键定义"""
    
    # 用户
    USER_PREFIX = "user:"
    USER_ID = "user:id:{}"
    USER_EMAIL = "user:email:{}"
    USER_TOKEN = "user:token:{}"
    
    # 消费者
    CONSUMER_PREFIX = "consumer:"
    CONSUMER_ID = "consumer:id:{}"
    
    # 商家
    MERCHANT_PREFIX = "merchant:"
    MERCHANT_ID = "merchant:id:{}"
    MERCHANT_PRODUCTS = "merchant:products:{}"
    
    # 商品
    PRODUCT_PREFIX = "product:"
    PRODUCT_ID = "product:id:{}"
    PRODUCT_BIDDING = "product:bidding:{}"
    PRODUCT_MIN_PRICE = "product:min_price:{}"
    
    # 广告
    AD_PREFIX = "ad:"
    AD_POOL = "ad:pool:{}"
    AD_STATS = "ad:stats:{}"
    AD_EXPOSURE = "ad:exposure:{}"
    AD_CLICK = "ad:click:{}"
    
    # 订阅
    SUBSCRIPTION_PREFIX = "subscription:"
    SUBSCRIPTION_USER = "subscription:user:{}"
