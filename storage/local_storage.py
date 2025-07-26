#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地存储服务实现
当 Mem0 API 不可用时的备选方案
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from schemas.common import Metadata, RetriveResult
from schemas.privacy import PrivacyLevel
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class LocalStorageService:
    """本地存储服务
    
    使用本地文件系统和向量相似度搜索作为 Mem0 的备选方案
    """
    
    def __init__(self, storage_path: str = "./local_memories.json"):
        """初始化本地存储服务
        
        参数:
            storage_path: 本地存储文件路径
        """
        self.storage_path = storage_path
        self.DEFAULT_USER_ID = "adventureX"
        
        # 初始化句子转换器用于语义搜索
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"警告: 无法加载句子转换器，将使用简单文本匹配: {e}")
            self.encoder = None
        
        # 确保存储文件存在
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """确保存储文件存在"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({"memories": []}, f, ensure_ascii=False, indent=2)
    
    def _load_memories(self) -> Dict[str, Any]:
        """加载记忆数据
        
        返回:
            Dict: 包含所有记忆的字典
        """
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载记忆文件失败: {e}")
            return {"memories": []}
    
    def _save_memories(self, data: Dict[str, Any]):
        """保存记忆数据
        
        参数:
            data: 要保存的记忆数据
        """
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆文件失败: {e}")
    
    def add(self, text: str, metadata: Metadata) -> str:
        """添加记忆
        
        参数:
            text: 记忆内容
            metadata: 元数据
            
        返回:
            str: 操作结果消息
        """
        try:
            data = self._load_memories()
            
            # 创建新的记忆条目
            memory_entry = {
                "id": str(uuid.uuid4()),
                "content": text,
                "metadata": {
                    "privacy_level": metadata.privacy_level.value,
                    "source": metadata.source
                },
                "timestamp": datetime.now().isoformat(),
                "user_id": self.DEFAULT_USER_ID
            }
            
            # 如果有编码器，计算向量
            if self.encoder:
                try:
                    embedding = self.encoder.encode([text])[0].tolist()
                    memory_entry["embedding"] = embedding
                except Exception as e:
                    print(f"计算向量失败: {e}")
            
            data["memories"].append(memory_entry)
            self._save_memories(data)
            
            return "ad-context记忆成功"
            
        except Exception as e:
            return f"ad-context记忆失败: {str(e)}"
    
    def search(self, query_text: str, top_k: int = 5, metadata_filter: Optional[Metadata] = None) -> List[RetriveResult]:
        """搜索记忆
        
        参数:
            query_text: 查询文本
            top_k: 返回结果数量
            metadata_filter: 元数据过滤器
            
        返回:
            List[RetriveResult]: 搜索结果列表
        """
        try:
            data = self._load_memories()
            memories = data.get("memories", [])
            
            if not memories:
                return []
            
            # 应用元数据过滤
            if metadata_filter:
                filtered_memories = []
                for memory in memories:
                    memory_metadata = memory.get("metadata", {})
                    if memory_metadata.get("privacy_level") == metadata_filter.privacy_level.value:
                        filtered_memories.append(memory)
                memories = filtered_memories
            
            results = []
            
            if self.encoder and memories:
                # 使用向量相似度搜索
                try:
                    query_embedding = self.encoder.encode([query_text])[0]
                    
                    for memory in memories:
                        if "embedding" in memory:
                            memory_embedding = np.array(memory["embedding"])
                            similarity = cosine_similarity([query_embedding], [memory_embedding])[0][0]
                            
                            result = RetriveResult(
                                context=memory["content"],
                                metadata=Metadata(
                                    privacy_level=PrivacyLevel(memory["metadata"]["privacy_level"]),
                                    source=memory["metadata"]["source"]
                                ),
                                score=float(similarity)
                            )
                            results.append(result)
                        else:
                            # 如果没有向量，使用简单文本匹配
                            score = self._simple_text_similarity(query_text, memory["content"])
                            result = RetriveResult(
                                context=memory["content"],
                                metadata=Metadata(
                                    privacy_level=PrivacyLevel(memory["metadata"]["privacy_level"]),
                                    source=memory["metadata"]["source"]
                                ),
                                score=score
                            )
                            results.append(result)
                            
                except Exception as e:
                    print(f"向量搜索失败，使用文本匹配: {e}")
                    # 降级到简单文本匹配
                    for memory in memories:
                        score = self._simple_text_similarity(query_text, memory["content"])
                        result = RetriveResult(
                            context=memory["content"],
                            metadata=Metadata(
                                privacy_level=PrivacyLevel(memory["metadata"]["privacy_level"]),
                                source=memory["metadata"]["source"]
                            ),
                            score=score
                        )
                        results.append(result)
            else:
                # 使用简单文本匹配
                for memory in memories:
                    score = self._simple_text_similarity(query_text, memory["content"])
                    result = RetriveResult(
                        context=memory["content"],
                        metadata=Metadata(
                            privacy_level=PrivacyLevel(memory["metadata"]["privacy_level"]),
                            source=memory["metadata"]["source"]
                        ),
                        score=score
                    )
                    results.append(result)
            
            # 按相似度排序并返回前 top_k 个结果
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"搜索记忆失败: {str(e)}")
            return []
    
    def _simple_text_similarity(self, query: str, text: str) -> float:
        """简单的文本相似度计算
        
        参数:
            query: 查询文本
            text: 目标文本
            
        返回:
            float: 相似度分数 (0-1)
        """
        query_lower = query.lower()
        text_lower = text.lower()
        
        # 简单的关键词匹配
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        
        if not query_words:
            return 0.0
        
        # 计算交集比例
        intersection = query_words.intersection(text_words)
        similarity = len(intersection) / len(query_words)
        
        # 如果查询文本是目标文本的子字符串，给予更高分数
        if query_lower in text_lower:
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def list(self, limit: int = 100, filters: Optional[Metadata] = None) -> List[Dict[str, Any]]:
        """列出记忆
        
        参数:
            limit: 返回结果数量限制
            filters: 过滤器
            
        返回:
            List[Dict]: 记忆列表
        """
        try:
            data = self._load_memories()
            memories = data.get("memories", [])
            
            # 应用过滤器
            if filters:
                filtered_memories = []
                for memory in memories:
                    memory_metadata = memory.get("metadata", {})
                    if memory_metadata.get("privacy_level") == filters.privacy_level.value:
                        filtered_memories.append(memory)
                memories = filtered_memories
            
            return memories[:limit]
            
        except Exception as e:
            print(f"列出记忆失败: {str(e)}")
            return []
    
    def delete(self, memory_id: str) -> Dict[str, Any]:
        """删除记忆
        
        参数:
            memory_id: 记忆ID
            
        返回:
            Dict: 操作结果
        """
        try:
            data = self._load_memories()
            memories = data.get("memories", [])
            
            # 查找并删除指定ID的记忆
            original_count = len(memories)
            memories = [m for m in memories if m.get("id") != memory_id]
            
            if len(memories) < original_count:
                data["memories"] = memories
                self._save_memories(data)
                return {"message": "记忆删除成功", "deleted": True}
            else:
                return {"message": "未找到指定记忆", "deleted": False}
                
        except Exception as e:
            return {"message": f"删除记忆失败: {str(e)}", "deleted": False}