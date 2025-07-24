
from schemas.common import ContextFragment
# 导入所有需要的服务
from storage.service import StorageService
from services.privacy import PrivacyService
from services.filter import FilterService
from services.authorization import AuthorizationService

class ContextCore:
    """
    Context核心业务逻辑编排器
    职责：作为项目的大脑，协调所有内部服务以完成一次完整的上下文处理流程。
    """
    def __init__(
        self,
        storage_service: StorageService,
        privacy_service: PrivacyService,
        filter_service: FilterService,
        authorization_service: AuthorizationService,
    ):
        """通过依赖注入初始化所有需要的服务实例"""
        self.storage = storage_service
        self.privacy = privacy_service
        self.filter = filter_service
        self.auth = authorization_service

    async def add_context_from_talk(self, mcp_request) -> None:
        """
        处理上下文的入库流程。

        Args:
            mcp_request: 从AI Talk的MCP Call中传入的请求。
        """
        pass

    async def get_context_for_talk(self, mcp_request) -> str:
        """
        处理上下文的出库/查询流程。

        Args:
            mcp_request: 从AI Talk的MCP Call中传入的请求。

        Returns:
            一个字符串，作为最终的上下文返回给AI。
        """
        pass
