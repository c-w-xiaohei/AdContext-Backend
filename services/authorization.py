import asyncio

class AuthorizationService:
    """
    用户授权服务
    职责：当访问敏感数据时，通过异步方式获取用户的明确许可。
    """
    async def request_approval(
        self, 
        sensitive_fragments: list[str]
    ) -> bool:
        """
        向用户桌面发送一个授权请求通知，并异步等待用户的决定。

        实现细节：
        1. 使用plyer库弹出原生桌面通知，按钮链接到本地Gateway的/authorize回调URL。
        2. 内部使用asyncio.Event或类似机制，使调用方可以await结果。
        3. Gateway的/authorize端点将设置此Event，解除等待。

        Args:
            sensitive_fragments: 需要用户授权才能访问的敏感上下文片段列表。
                                 将用于在通知中向用户展示请求内容。

        Returns:
            True 如果用户允许，False 如果用户拒绝或超时。
        """
        pass
