from schemas.common import Metadata

class StorageService:
    """
    存储服务层
    职责：作为mem0库的直接封装，提供干净、类型化的数据访问接口。
    """
    def __init__(self, mem0_instance):
        """初始化时需要传入一个配置好的mem0.Memory实例"""
        self.memory = mem0_instance
        
    def add(self, context: str,metadata: Metadata) -> str:
        """
        向mem0中添加一个上下文片段。

        Args:
            context: 需要存储的上下文片段。

        Returns:
            存入mem0后返回的唯一ID。
        """
        pass

    def search(
        self, 
        query_text: str, 
        metadata_filter: Metadata | None = None, 
        top_k: int = 5
    ) -> str:
        """
        在mem0中进行搜索。

        Args:
            query_text: 用于语义搜索的查询文本。
            metadata_filter: 用于元数据过滤的Metadata对象, e.g., 
                             {"privacy_level": "PUBLIC", "timestamp": {"gt": 123456}}.
            top_k: 返回最相似结果的数量。

        Returns:
            匹配到的上下文片段对象列表。
        """
        pass
