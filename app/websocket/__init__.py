from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
from datetime import datetime
from app.core.redis import redis_client


class ChatConnectionManager:
    """WebSocket 连接管理器（基础版）"""
    
    def __init__(self):
        # user_id -> {merchant_id -> WebSocket}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, user_id: int, merchant_id: int, websocket: WebSocket):
        """建立连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][merchant_id] = websocket
        
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "merchant_id": merchant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, user_id: int, merchant_id: int):
        """断开连接"""
        if user_id in self.active_connections:
            if merchant_id in self.active_connections[user_id]:
                del self.active_connections[user_id][merchant_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, user_id: int, merchant_id: int, message: dict):
        """发送个人消息"""
        try:
            if user_id in self.active_connections:
                if merchant_id in self.active_connections[user_id]:
                    websocket = self.active_connections[user_id][merchant_id]
                    await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def broadcast_to_merchant(self, merchant_id: int, message: dict):
        """广播消息给商家的所有连接用户"""
        disconnected_users = []
        for user_id, merchants in self.active_connections.items():
            if merchant_id in merchants:
                try:
                    await merchants[merchant_id].send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to merchant: {e}")
                    disconnected_users.append((user_id, merchant_id))
        
        for user_id, merc_id in disconnected_users:
            self.disconnect(user_id, merc_id)
    
    async def broadcast_to_user(self, user_id: int, message: dict):
        """广播消息给用户的所有连接"""
        disconnected_merchants = []
        if user_id in self.active_connections:
            for merchant_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to user: {e}")
                    disconnected_merchants.append(merchant_id)
        
        for merchant_id in disconnected_merchants:
            self.disconnect(user_id, merchant_id)
    
    async def broadcast_to_all(self, message: dict):
        """广播消息给所有连接"""
        disconnected = []
        for user_id, merchants in self.active_connections.items():
            for merchant_id, websocket in merchants.items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to all: {e}")
                    disconnected.append((user_id, merchant_id))
        
        for user_id, merchant_id in disconnected:
            self.disconnect(user_id, merchant_id)
    
    async def handle_message(self, user_id: int, merchant_id: int, message: dict):
        """处理消息"""
        message_type = message.get("type")
        
        if message_type == "chat":
            await self._handle_chat_message(user_id, merchant_id, message)
        elif message_type == "ping":
            await self.send_personal_message(user_id, merchant_id, {"type": "pong"})
    
    async def _handle_chat_message(self, user_id: int, merchant_id: int, message: dict):
        """处理聊天消息"""
        from app.core.db import SessionLocal
        from app.models.chat_message import ChatMessage
        
        db = SessionLocal()
        try:
            chat_msg = ChatMessage(
                user_id=user_id,
                merchant_id=merchant_id,
                content=message.get("content"),
                message_type="text",
                context=message.get("context")
            )
            db.add(chat_msg)
            db.commit()
            
            response = {
                "type": "chat",
                "user_id": user_id,
                "merchant_id": merchant_id,
                "content": message.get("content"),
                "timestamp": chat_msg.created_at.isoformat(),
                "message_id": chat_msg.id
            }
            
            await self.send_personal_message(user_id, merchant_id, response)
            await self.broadcast_to_merchant(merchant_id, response)
            
            # 在 Redis 中记录消息
            msg_key = f"chat:messages:{merchant_id}"
            redis_client.lpush(msg_key, json.dumps(response))
            redis_client.ltrim(msg_key, 0, 99)
        
        except Exception as e:
            print(f"Error handling chat message: {e}")
        finally:
            db.close()
    
    def get_active_connections_count(self) -> int:
        """获取活跃连接数"""
        return sum(len(merchants) for merchants in self.active_connections.values())
    
    def get_user_connections(self, user_id: int) -> int:
        """获取用户的活跃连接数"""
        return len(self.active_connections.get(user_id, {}))
    
    def get_merchant_connections(self, merchant_id: int) -> int:
        """获取商家的活跃连接数"""
        count = 0
        for merchants in self.active_connections.values():
            if merchant_id in merchants:
                count += 1
        return count


# 全局连接管理器实例
manager = ChatConnectionManager()
