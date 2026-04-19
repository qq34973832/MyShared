import secrets
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_api_token(length: int = 32) -> str:
    """生成 API Token"""
    characters = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(characters) for _ in range(length))


def mask_token(token: str, show_chars: int = 4) -> str:
    """隐藏 Token（只显示最后几个字符）"""
    if len(token) <= show_chars:
        return "*" * len(token)
    return "*" * (len(token) - show_chars) + token[-show_chars:]


def get_expiration_date(days: int) -> datetime:
    """计算过期日期"""
    return datetime.utcnow() + timedelta(days=days)


def is_token_expired(expires_at: Optional[datetime]) -> bool:
    """检查 Token 是否过期"""
    if not expires_at:
        return False
    return datetime.utcnow() > expires_at


def paginate(skip: int = 0, limit: int = 20) -> tuple:
    """分页参数"""
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 20
    return skip, limit
