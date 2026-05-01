from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Query, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.db import get_db, SessionLocal
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.dependencies.auth import get_current_user
from app.dependencies.role import require_merchant
from app.websocket import manager
from app.models.merchant import Merchant

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/ws/{merchant_id}")
async def websocket_endpoint(websocket: WebSocket, merchant_id: int, token: str = None):
    """WebSocket 聊天连接"""
    db = SessionLocal()
    try:
        # 如果提供了 token，则验证用户
        user_id = 0  # 默认匿名
        if token:
            from app.core.security import decode_token
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub", 0)
        
        await manager.connect(user_id, merchant_id, websocket)
        
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(user_id, merchant_id, data)
    
    except WebSocketDisconnect:
        manager.disconnect(user_id, merchant_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id, merchant_id)
    finally:
        db.close()


@router.post("/messages", response_model=ChatMessageResponse)
def send_chat_message(
    message_in: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送聊天消息"""
    message = ChatMessage(
        user_id=current_user.id,
        merchant_id=message_in.merchant_id,
        content=message_in.content,
        message_type=message_in.message_type,
        context=message_in.context,
        sender_role="user"
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


@router.get("/messages/{merchant_id}", response_model=list[ChatMessageResponse])
def get_chat_messages(
    merchant_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取与商家的聊天记录"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.merchant_id == merchant_id
    ).order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()

    for message in messages:
        if message.sender_role == "merchant" and not message.is_read:
            message.is_read = True
    db.commit()
    
    return messages


@router.get("/merchant/conversations")
def get_merchant_conversations(
    merchant_user: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """获取商户侧会话列表（按用户聚合）"""
    merchant = db.query(Merchant).filter(Merchant.user_id == merchant_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.merchant_id == merchant.id)
        .order_by(ChatMessage.created_at.desc())
        .all()
    )

    conversations = []
    seen_user_ids = set()
    for msg in messages:
        if msg.user_id in seen_user_ids:
            continue
        seen_user_ids.add(msg.user_id)
        user = db.query(User).filter(User.id == msg.user_id).first()
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.merchant_id == merchant.id,
            ChatMessage.user_id == msg.user_id,
            ChatMessage.is_read == False
        ).count()
        conversations.append({
            "user_id": msg.user_id,
            "username": user.username if user else f"User#{msg.user_id}",
            "last_message": msg.content,
            "last_message_at": msg.created_at,
            "unread_count": unread_count,
        })

    return conversations


@router.get("/merchant/messages/{user_id}", response_model=list[ChatMessageResponse])
def get_messages_for_merchant(
    user_id: int,
    merchant_user: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """商户查看与某个用户的聊天记录"""
    merchant = db.query(Merchant).filter(Merchant.user_id == merchant_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.merchant_id == merchant.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    for message in messages:
        if message.sender_role == "user" and not message.is_read:
            message.is_read = True
    db.commit()
    return messages


@router.post("/merchant/messages/{user_id}", response_model=ChatMessageResponse)
def send_message_as_merchant(
    user_id: int,
    message_in: ChatMessageCreate,
    merchant_user: User = Depends(require_merchant),
    db: Session = Depends(get_db)
):
    """商户向用户回复消息"""
    merchant = db.query(Merchant).filter(Merchant.user_id == merchant_user.id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    message = ChatMessage(
        user_id=user_id,
        merchant_id=merchant.id,
        content=message_in.content,
        message_type=message_in.message_type,
        context=message_in.context,
        sender_role="merchant",
        is_read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.put("/messages/{message_id}/read", status_code=204)
def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记消息为已读"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
