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
from app.dependencies.role import require_merchant
from app.utils.webhook_signature import verify_webhook_signature, sign_webhook
from app.models.merchant import Merchant

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse)
def create_webhook(
    webhook_in: WebhookCreate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """创建 Webhook"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    from app.utils.helpers import generate_api_token
    
    webhook = Webhook(
        name=webhook_in.name,
        url=webhook_in.url,
        events=webhook_in.events,
        secret=generate_api_token(32),
        is_active=True
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    merchant: User = Depends(require_merchant),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取 Webhook 列表"""
    merchant_info = db.query(Merchant).filter(Merchant.user_id == merchant.id).first()
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    return db.query(Webhook).offset(skip).limit(limit).all()


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_in: WebhookUpdate,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """更新 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    if webhook_in.name:
        webhook.name = webhook_in.name
    if webhook_in.url:
        webhook.url = webhook_in.url
    if webhook_in.events:
        webhook.events = webhook_in.events
    if webhook_in.is_active is not None:
        webhook.is_active = webhook_in.is_active
    
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: int,
    merchant: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """删除 Webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()


@router.get("/logs/{webhook_id}", response_model=list[WebhookLogResponse])
def get_webhook_logs(
    webhook_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取 Webhook 日志"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
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
