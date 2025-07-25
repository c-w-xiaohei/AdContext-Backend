from schemas.common import ContextFragment, RetriveResult
# 导入所有需要的服务
from storage.service import StorageService
from services.privacy import PrivacyService
from services.filter import FilterService
from services.authorization import AuthorizationService
from typing import List

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
        # authorization_service: AuthorizationService,
    ):
        """通过依赖注入初始化所有需要的服务实例"""
        self.storage = storage_service
        self.privacy = privacy_service
        self.filter = filter_service
        self.auth = authorization_service

    async def query(self, text) -> None:
        """
        处理上下文的入库流程。

        Args:
            mcp_request: 从AI Talk的MCP Call中传入的请求。
        """
        res = self.storage.search(text)
        # 根据score阈值筛选res列表中的对象
        
        threshold = 0.7  # 可以根据实际需求调整阈值
        filtered_res: List[RetriveResult] = [item for item in res if getattr(item, "score", 0) >= threshold]
        
        
        # 将filtered_res拼接为字符串
        filtered_text = "\n".join([getattr(item, "content", "") for item in filtered_res])
        self.filter.filter_for_storage(filtered_text)
        
        
        level = self.privacy.classify(filtered_text)
        
        
        return filtered_text

    async def input(self, text) -> str:
        """
        处理上下文的出库/查询流程。

        Args:
            mcp_request: 从AI Talk的MCP Call中传入的请求。

        Returns:
            一个字符串，作为最终的上下文返回给AI。
        """
        self.filter.filter_for_storage(text)
        level = self.privacy.check(text)
        self.storage.add(text,level)
        
        
context_core = ContextCore(
    StorageService(),
    PrivacyService(),
    FilterService(),
)
