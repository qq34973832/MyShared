import hmac
import hashlib
import json
from typing import Union


def sign_webhook(payload: dict, secret: str) -> str:
    """生成 Webhook 签名"""
    # 将 payload 转换为 JSON 字符串
    if isinstance(payload, dict):
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    else:
        payload_str = str(payload)
    
    # 使用 HMAC-SHA256 签名
    signature = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_webhook_signature(payload: dict, signature: str, secret: str) -> bool:
    """验证 Webhook 签名"""
    expected_signature = sign_webhook(payload, secret)
    return hmac.compare_digest(signature, expected_signature)
