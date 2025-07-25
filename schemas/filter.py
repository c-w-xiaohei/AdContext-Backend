from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContextItem:
    """单个上下文项数据结构"""
    content: str                    # 上下文内容
    relevance_score: float = 0.0    # 相关性评分 (0.0-1.0)
    original_index: int = -1        # 原始索引位置
    

@dataclass
class FilteredResult:
    """筛选结果数据结构"""
    filtered_contexts: str          # 最终整理后的上下文字符串
    original_count: int             # 原始上下文数量
    filtered_count: int             # 筛选后数量
    avg_relevance_score: float      # 平均相关性分数
    processing_time: float = 0.0    # 处理耗时（秒）


@dataclass 
class ScoringResult:
    """评分结果数据结构（内部使用）"""
    scored_contexts: List[ContextItem]  # 评分后的上下文列表
    filtered_contexts: List[ContextItem]  # 筛选后的上下文列表
    success: bool = True                # 处理是否成功
    error_message: Optional[str] = None # 错误信息 