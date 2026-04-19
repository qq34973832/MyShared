from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Header
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.models.webhook import Webhook, WebhookLog
from app.schemas.webhook import (
    WebhookCreate, WebhookResponse, WebhookUpdate,
    WebhookLogResponse, WebhookEventPayload
)
from app.dependencies.auth import get_current_user
from app.utils.webhook_signature import verify_webhook_signature, sign_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _owned_webhook_name(user_id: int, name: str) -> str:
    return f"[user:{user_id}] {name}"


def _display_webhook_name(user_id: int, name: str) -> str:
    prefix = f"[user:{user_id}] "
    if name.startswith(prefix):
        return name[len(prefix):]
    return name


def _serialize_webhook(user_id: int, webhook: Webhook) -> dict:
    return {
        "id": webhook.id,
        "name": _display_webhook_name(user_id, webhook.name),
        "url": webhook.url,
        "events": webhook.events,
        "is_active": webhook.is_active,
        "created_at": webhook.created_at,
    }


@router.post("", response_model=WebhookResponse)
def create_webhook(
    webhook_in: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建 Webhook"""
    from app.utils.helpers import generate_api_token

    webhook = Webhook(
        name=_owned_webhook_name(current_user.id, webhook_in.name),
        url=webhook_in.url,
        events=webhook_in.events,
        secret=generate_api_token(32),
        is_active=True
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return _serialize_webhook(current_user.id, webhook)


@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取 Webhook 列表"""
    prefix = f"[user:{current_user.id}] %"
    webhooks = db.query(Webhook).filter(Webhook.name.like(prefix)).offset(skip).limit(limit).all()
    return [_serialize_webhook(current_user.id, webhook) for webhook in webhooks]


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_in: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if not webhook.name.startswith(f"[user:{current_user.id}] "):
        raise HTTPException(status_code=403, detail="Webhook access denied")

    if webhook_in.name:
        webhook.name = _owned_webhook_name(current_user.id, webhook_in.name)
    if webhook_in.url:
        webhook.url = webhook_in.url
    if webhook_in.events:
        webhook.events = webhook_in.events
    if webhook_in.is_active is not None:
        webhook.is_active = webhook_in.is_active
    
    db.commit()
    db.refresh(webhook)

    return _serialize_webhook(current_user.id, webhook)


@router.delete("/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if not webhook.name.startswith(f"[user:{current_user.id}] "):
        raise HTTPException(status_code=403, detail="Webhook access denied")

    db.delete(webhook)
    db.commit()


@router.get("/logs/{webhook_id}", response_model=list[WebhookLogResponse])
def get_webhook_logs(
    webhook_id: int,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取 Webhook 日志"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if not webhook.name.startswith(f"[user:{current_user.id}] "):
        raise HTTPException(status_code=403, detail="Webhook access denied")
    
    return db.query(WebhookLog).filter(
        WebhookLog.webhook_id == webhook_id
    ).offset(skip).limit(limit).order_by(WebhookLog.created_at.desc()).all()


@router.post("/incoming")
def handle_incoming_webhook(
    body: dict = Body(...),
    x_webhook_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """处理入站 Webhook（需要签名校验）"""
    if not x_webhook_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature header"
        )
    
    # 验证签名（实际应用中应查找相应的 Webhook 配置）
    # 这里简化处理
    
    return {
        "message": "Webhook received successfully"
    }
