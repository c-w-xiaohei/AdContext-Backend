from schemas.common import RetriveResult
# 导入所有需要的服务
from storage.service import StorageService
from services.privacy import PrivacyClassifier
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
        privacy_classifier: PrivacyClassifier,
        filter_service: FilterService,
        # authorization_service: AuthorizationService,
    ):
        """通过依赖注入初始化所有需要的服务实例"""
        self.storage = storage_service
        self.privacy = privacy_classifier
        self.filter = filter_service
        # self.auth = authorization_service

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
        
        filtered_text = self.filter.filter_retrieved_context(filtered_res)
        
        privacy_label = self.privacy.classify(filtered_text)
        level = privacy_label.level
        
        
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
        privacy_label = self.privacy.classify(text)
        level = privacy_label.level
        self.storage.add(text,level)
        
        
# 注意: 这是一个示例实例化。在生产环境中，您应该从安全的配置中加载服务，
# 例如，通过一个主应用工厂函数来初始化所有服务和依赖。
context_core = ContextCore(
    storage_service=StorageService(),
    # PrivacyClassifier现在需要API密钥。
    # 为了使应用可以启动，这里使用了一个占位符。
    # 在实际部署中，请务必通过环境变量或安全的配置管理来提供真实的密钥。
    privacy_classifier=PrivacyClassifier(api_key="YOUR_AIHUBMIX_API_KEY_HERE"),
    filter_service=FilterService(),
)
