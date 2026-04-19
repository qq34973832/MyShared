"""WebSocket 管理器 - 对连接管理器的高级包装"""

from app.websocket import manager as connection_manager


class WebSocketManager:
    """
    WebSocket 高级管理器
    提供便利方法和扩展功能
    """
    
    def __init__(self):
        self.manager = connection_manager
    
    async def notify_user_connected(self, user_id: int, merchant_id: int):
        """通知商家有用户连接"""
        message = {
            "type": "user_connected",
            "user_id": user_id,
            "merchant_id": merchant_id
        }
        await self.manager.broadcast_to_merchant(merchant_id, message)
    
    async def notify_user_disconnected(self, user_id: int, merchant_id: int):
        """通知商家用户断开连接"""
        message = {
            "type": "user_disconnected",
            "user_id": user_id,
            "merchant_id": merchant_id
        }
        await self.manager.broadcast_to_merchant(merchant_id, message)
    
    def get_connections_stats(self) -> dict:
        """获取连接统计信息"""
        return {
            "total_connections": self.manager.get_active_connections_count(),
            "active_users": len(self.manager.active_connections)
        }


# 全局 WebSocket 管理器
websocket_manager = WebSocketManager()
