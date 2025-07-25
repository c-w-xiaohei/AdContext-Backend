from schemas.common import Metadata, RetriveResult, ListResult
from typing import List, Dict, Any, Optional
from storage.db import client

class StorageService:
    """
    存储服务层
    职责：作为mem0库的直接封装，提供干净、类型化的数据访问接口。
    """
    def __init__(self):
        pass
        
    def add(self, context: str,metadata: Metadata) -> str:
        """
        向mem0中添加一个上下文片段。

        Args:
            context: 需要存储的上下文片段。

        Returns:
            存入mem0后返回的唯一ID。
        """
        client.add([{"role": "user", "content": context}],metadata=metadata)

    def search(
        self, 
        query_text: str, 
        top_k: int = 5,
        metadata_filter: Optional[Metadata] = None,    ) -> List[RetriveResult]:
        """
        在mem0中进行搜索。

        Args:
            query_text: 用于语义搜索的查询文本。
            top_k: 返回最相似结果的数量。
            metadata_filter: 用于元数据过滤的Metadata对象, e.g., 
                             {"privacy_level": "PUBLIC", "timestamp": {"gt": 123456}}.

        Returns:
            匹配到的上下文片段对象列表。
        """
        return client.search(query_text, top_k, metadata_filter)
        
    def list(self,
            limit: int = 100,
            filters: Optional[Metadata] = None,
            ) -> List[ListResult]:
            """
            列出所有记忆或根据过滤器列出。

            输入参数：
            - limit (int): 返回结果的最大数量。
            - filters (Optional[Metadata]): 应用于列表的额外过滤器。

            输出：
            - List[ListResult]: 记忆列表。
            """
            pass
