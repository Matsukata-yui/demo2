import asyncio
import json
import time
from collections import defaultdict

class SSEUtils:
    def __init__(self):
        self.clients = set()
        self.message_queue = asyncio.Queue()
        self.running = False
    
    async def register_client(self, client):
        """注册SSE客户端"""
        self.clients.add(client)
        try:
            # 发送欢迎消息
            await client.send({
                "event": "welcome",
                "data": json.dumps({"message": "Connected to SSE server", "timestamp": time.time()})
            })
            
            # 保持连接
            while True:
                await asyncio.sleep(30)
                await client.send({"event": "ping", "data": json.dumps({"timestamp": time.time()})})
        finally:
            self.clients.remove(client)
    
    async def broadcast(self, event, data):
        """向所有客户端广播消息"""
        message = {
            "event": event,
            "data": json.dumps(data),
            "timestamp": time.time()
        }
        
        disconnected_clients = []
        for client in self.clients:
            try:
                await client.send(message)
            except Exception:
                disconnected_clients.append(client)
        
        # 清理断开连接的客户端
        for client in disconnected_clients:
            self.clients.remove(client)
    
    async def start(self):
        """启动SSE服务"""
        self.running = True
        while self.running:
            try:
                # 处理消息队列
                if not self.message_queue.empty():
                    event, data = await self.message_queue.get()
                    await self.broadcast(event, data)
                await asyncio.sleep(0.1)
            except Exception:
                await asyncio.sleep(1)
    
    async def stop(self):
        """停止SSE服务"""
        self.running = False
        await self.broadcast("server_shutdown", {"message": "SSE server is shutting down"})
        self.clients.clear()

class WebSocketUtils:
    def __init__(self):
        self.clients = defaultdict(set)
        self.running = False
    
    def register_client(self, client, client_id=None):
        """注册WebSocket客户端"""
        client_id = client_id or id(client)
        self.clients[client_id].add(client)
    
    def unregister_client(self, client, client_id=None):
        """注销WebSocket客户端"""
        client_id = client_id or id(client)
        if client_id in self.clients:
            self.clients[client_id].remove(client)
            if not self.clients[client_id]:
                del self.clients[client_id]
    
    async def send_to_client(self, client_id, message):
        """向指定客户端发送消息"""
        if client_id in self.clients:
            disconnected_clients = []
            for client in self.clients[client_id]:
                try:
                    await client.send(json.dumps(message))
                except Exception:
                    disconnected_clients.append(client)
            
            # 清理断开连接的客户端
            for client in disconnected_clients:
                self.unregister_client(client, client_id)
    
    async def broadcast(self, message, exclude_client_id=None):
        """向所有客户端广播消息"""
        disconnected_clients = []
        
        for client_id, clients in self.clients.items():
            if exclude_client_id and client_id == exclude_client_id:
                continue
            
            for client in clients:
                try:
                    await client.send(json.dumps(message))
                except Exception:
                    disconnected_clients.append((client, client_id))
        
        # 清理断开连接的客户端
        for client, client_id in disconnected_clients:
            self.unregister_client(client, client_id)

class SSEManager:
    def __init__(self):
        self.messages = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def add_message(self, channel, message):
        """添加消息到指定通道"""
        async with self.lock:
            self.messages[channel].append(message)
    
    def get_messages(self, channel):
        """获取并清空指定通道的消息"""
        if channel in self.messages:
            messages = self.messages[channel].copy()
            self.messages[channel].clear()
            return messages
        return []
    
    def clear_channel(self, channel):
        """清空指定通道的消息"""
        if channel in self.messages:
            self.messages[channel].clear()
    
    def clear_all(self):
        """清空所有通道的消息"""
        self.messages.clear()

# 创建全局实例
sse_utils = SSEUtils()
ws_utils = WebSocketUtils()
sse_manager = SSEManager()