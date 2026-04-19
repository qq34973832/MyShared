from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageCreate(BaseModel):
    merchant_id: int
    content: str
    message_type: str = "text"
    context: Optional[str] = None  # pre-sale, after-sale


class ChatMessageResponse(BaseModel):
    id: int
    user_id: int
    merchant_id: int
    content: str
    message_type: str
    is_read: bool
    context: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatConversationResponse(BaseModel):
    merchant_id: int
    merchant_name: str
    last_message: Optional[ChatMessageResponse]
    unread_count: int
    created_at: datetime
