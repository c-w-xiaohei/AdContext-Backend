# websocket_service.py
import asyncio
from typing import Dict, Any
from starlette.websockets import WebSocket

class WebSocketManager:
    def __init__(self):
        # 我们只假设有一个前端连接，对于Hackathon来说足够了
        self.active_connection: WebSocket | None = None
        # 用于存储请求和未来的响应
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection = websocket
        print("前端已通过WebSocket连接！")

    def disconnect(self):
        self.active_connection = None
        print("前端WebSocket连接已断开。")

    async def send_json(self, data: dict):
        if self.active_connection:
            await self.active_connection.send_json(data)
        else:
            print("错误：没有活跃的前端连接。")

    async def wait_for_response(self, request_id: str, timeout: int = 60) -> Any:
        """
        异步等待前端对特定请求ID的响应。
        """
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[request_id] = future
        try:
            # 等待future被设置结果，带有超时
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            print(f"等待对请求 {request_id} 的响应超时。")
            return None
        finally:
            # 清理
            del self.pending_requests[request_id]

    def resolve_request(self, request_id: str, data: Any):
        """
        当从前端收到响应时，用数据解析对应的future。
        """
        if request_id in self.pending_requests:
            self.pending_requests[request_id].set_result(data)

# 创建一个全局实例
websocket_manager = WebSocketManager()