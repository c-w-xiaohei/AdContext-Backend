from schemas.common import Metadata, RetriveResult, ListResult
from schemas.privacy import PrivacyLevel  
from typing import List, Dict, Any, Optional
from storage.db import client
from mem0 import MemoryClient
import os
from services.websocket import WebSocketManager
from schemas.websocket import OperationResultPayload
import uuid

class StorageService:
    """
    存储服务层
    职责：作为mem0库的直接封装，提供干净、类型化的数据访问接口。
    """
    def __init__(self,websocket_manager:WebSocketManager):
        """初始化存储服务"""
        self.storage = MemoryClient()
        self.websocket = websocket_manager
        self.DEFAULT_USER_ID = "adventureX"
        self.api_key = os.getenv("MEM0_API_KEY")

    async def add(self, text: str , metadata: Metadata,privacy_brief:Optional[str] = None) -> str:
        """
        向mem0中添加一个上下文片段。

        Args:
            text: 需要存储的上下文片段。
            metadata: 元数据对象，包含隐私级别和来源信息。

        Returns:
            str: 存入mem0后返回的操作结果消息。
        """
        try:
            
            is_privacy:bool = metadata.privacy_level.value >= 3
            if is_privacy:
                messages = [{"role": "user", "content": privacy_brief}]
            else:
                 messages = [{"role": "user", "content": text}]
            
            # 将 Metadata 对象转换为字典格式
            
            metadata_dict = {
                "privacy_level": metadata.privacy_level.value,  # 获取枚举的值
                "source": metadata.source
            }
            
            
            if is_privacy:
                # 隐私流
                 # 1. 生成一个唯一的请求ID
                request_id = str(uuid.uuid4())

                # 2. 向前端发送上链请求
                await self.websocket.send_json({
                    "type": "REQUEST_ONCHAIN_STORAGE",
                    "requestId": request_id,
                    "payload": {
                        # 将需要加密的完整数据发给前端
                        "dataToStore": text 
                    }
                })

                # 3. 异步等待前端的响应
                print(f"[后端] 等待前端响应请求: {request_id}")
                response: OperationResultPayload = await self.websocket.wait_for_response(request_id)

                # 4. 处理前端返回的结果
                if response and response.get("success"):
                    blockchain_data_id = request_id
                    
                    metadata_dict["blockchain_data_id"] = blockchain_data_id
                    
                    self.storage.add(
                        messages, 
                        user_id=self.DEFAULT_USER_ID, 
                        output_format="v1.1", 
                        metadata=metadata_dict, # 传递字典而不是对象
                        infer = True
                    )
                messages = [{"role": "user", "content": privacy_brief}]
                    
            else:
                result = self.storage.add(
                    messages, 
                    user_id=self.DEFAULT_USER_ID, 
                    output_format="v1.1", 
                    metadata=metadata_dict, # 传递字典而不是对象
                    infer = True
                )
            
            msg = "ad-context记忆成功"
            return msg
        except Exception as e:
            return f"ad-context记忆失败: {str(e)}"

    def search(self, query_text: str, top_k: int = 5,metadata_filter: Optional[Metadata] = None,) -> List[Dict[str, Any]]:
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
        try:
            # 准备查询参数
            kwargs = {
                'user_id': self.DEFAULT_USER_ID,
                'top_k': top_k
            }
            
            # 如果有过滤器，添加到参数中
            if metadata_filter:
                kwargs['filters'] = metadata_filter
            
            # 调用mem0客户端的search方法
            results = self.storage.search(query_text, version="v1", **kwargs)
            
            # 检查results是否为None或空
            if results is None:
                return []
                
            if not isinstance(results, list):
                return []
            
            # 转换为RetriveResult格式
            retrieve_results = []
            for result in results:
                # 添加空值检查
                if result is None:
                    continue
                    
                # 确保result是字典类型
                if not isinstance(result, dict):
                    continue
                    
                # 安全地获取metadata，确保它是字典类型
                metadata_dict = result.get('metadata') or {}
                if not isinstance(metadata_dict, dict):
                    metadata_dict = {}
                    
                # 根据实际的result结构创建RetriveResult对象
                retrieve_result = RetriveResult(
                    context=result.get('memory', ''),
                    metadata=Metadata(
                        privacy_level=PrivacyLevel(metadata_dict.get('privacy_level', 'LEVEL_1_PUBLIC')),  # 使用 PrivacyLevel 枚举
                        source=metadata_dict.get('source', 'unknown')
                    ),
                    score=result.get('score', 0.0)
                )
                retrieve_results.append(retrieve_result)
            
            return retrieve_results
            
        except Exception as e:
            print(f"Error searching memories: {str(e)}")
            return []

    def list(self, limit: int = 100, filters: Optional[Metadata] = None) -> List[Dict[str, Any]]:
        """
        列出所有记忆或根据过滤器列出。

        Args:
            limit: 返回结果的最大数量。
            filters: 应用于列表的额外过滤器。

        Returns:
            记忆列表。
        """
        try:
            # 准备查询参数
            kwargs = {
                'user_id': self.DEFAULT_USER_ID,
            }
            
            # 如果有过滤器，添加到参数中
            if filters:
                kwargs['filters'] = filters.dict()
            
            # 调用mem0客户端的get_all方法
            memories = self.storage.get_all(version="v1", **kwargs)
            return memories
          
            
        except Exception as e:
            print(f"Error listing memories: {str(e)}")
            return []
            
    def delete(self,memory_id)-> Dict[str, Any]:
        return self.storage.delete(memory_id)
