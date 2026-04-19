from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ChatMessage(BaseModel):
    """聊天消息"""
    __tablename__ = "chat_messages"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 消息内容
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, file
    
    # 附件
    attachment_url = Column(String(500), nullable=True)
    
    # 状态
    is_read = Column(Boolean, default=False)
    
    # 场景
    context = Column(String(50), nullable=True)  # pre-sale, after-sale, general
    
    # 关系
    user = relationship("User", back_populates="chat_messages")
    merchant = relationship("Merchant")

    def __repr__(self):
        return f"<ChatMessage user_id={self.user_id} merchant_id={self.merchant_id}>"
