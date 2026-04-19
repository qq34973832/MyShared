from app.core.redis import redis_client
from typing import Any, Optional
import json


class Cache:
    """缓存工具类"""
    
    @staticmethod
    def get(key: str):
        """获取缓存"""
        value = redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    @staticmethod
    def set(key: str, value: Any, ex: int = 3600):
        """设置缓存"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        redis_client.set(key, value, ex=ex)
    
    @staticmethod
    def delete(key: str):
        """删除缓存"""
        redis_client.delete(key)
    
    @staticmethod
    def delete_pattern(pattern: str):
        """删除匹配模式的缓存"""
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    
    @staticmethod
    def exists(key: str) -> bool:
        """检查缓存是否存在"""
        return redis_client.exists(key) > 0
    
    @staticmethod
    def incr(key: str, amount: int = 1) -> int:
        """自增"""
        return redis_client.incrby(key, amount)
    
    @staticmethod
    def expire(key: str, seconds: int):
        """设置过期时间"""
        redis_client.expire(key, seconds)


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
