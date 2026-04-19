import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对密码进行哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解析 JWT 令牌"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.InvalidTokenError:
        return None


class Permission:
    """权限常量"""
    
    # 用户权限
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_BAN = "user:ban"
    
    # 商家权限
    MERCHANT_READ = "merchant:read"
    MERCHANT_CREATE = "merchant:create"
    MERCHANT_UPDATE = "merchant:update"
    MERCHANT_DELETE = "merchant:delete"
    
    # 商品权限
    PRODUCT_READ = "product:read"
    PRODUCT_CREATE = "product:create"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    
    # 广告权限
    AD_READ = "ad:read"
    AD_CREATE = "ad:create"
    AD_UPDATE = "ad:update"
    AD_DELETE = "ad:delete"


class Role:
    """角色常量"""
    
    ADMIN = "admin"
    MERCHANT = "merchant"
    CONSUMER = "consumer"
    GUEST = "guest"
