import os
import json
import time
import requests
from typing import List, Optional
from schemas.filter import ContextItem, FilteredResult, ScoringResult
from schemas.common import RetriveResult
from .prompts import get_context_scoring_message, get_context_integration_message


class FilterService:
    """上下文质量与相关性筛选服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: str = "gemini-2.5-flash-lite",
                 relevance_threshold: float = 0.3):
        """
        初始化FilterService
        
        Args:
            api_key (str, optional): AI模型API密钥. 如果未提供，将从环境变量 AIHUBMIX_API_KEY 读取.
            model_name (str): 使用的模型名称
            relevance_threshold (float): 相关性分数阈值，低于此值的上下文将被移除
        """
        resolved_api_key = api_key or os.environ.get("AIHUBMIX_API_KEY")
        if not resolved_api_key:
            raise ValueError("AiHubMix API Key not provided. Please pass it as an argument or set the AIHUBMIX_API_KEY environment variable.")
            
        self.api_key = resolved_api_key
        self.model_name = model_name
        self.relevance_threshold = relevance_threshold
        self.api_url = "https://aihubmix.com/v1/chat/completions"
    
    def filter_contexts(self, user_talk: str, candidate_contexts: List[str]) -> FilteredResult:
        """
        对候选上下文进行二次筛选和整理
        
        Args:
            user_talk (str): 用户问题/对话
            candidate_contexts (List[str]): 候选上下文列表
        
        Returns:
            FilteredResult: 筛选和整理后的结果
        """
        start_time = time.time()
        
        if not candidate_contexts:
            return FilteredResult(
                filtered_contexts="",
                original_count=0,
                filtered_count=0,
                avg_relevance_score=0.0,
                processing_time=time.time() - start_time
            )
        
        try:
            # 第一步：使用LLM对上下文进行相关性评分
            scoring_result = self._score_contexts(user_talk, candidate_contexts)
            
            if not scoring_result.success:
                # 如果评分失败，返回所有原始上下文
                return FilteredResult(
                    filtered_contexts="\n\n".join(candidate_contexts),
                    original_count=len(candidate_contexts),
                    filtered_count=len(candidate_contexts),
                    avg_relevance_score=0.5,  # 默认中等相关性
                    processing_time=time.time() - start_time
                )
            
            # 第二步：使用LLM将筛选后的上下文整理成连贯文本
            if scoring_result.filtered_contexts:
                integrated_context = self._integrate_contexts(scoring_result.filtered_contexts)
                avg_score = sum(ctx.relevance_score for ctx in scoring_result.filtered_contexts) / len(scoring_result.filtered_contexts)
            else:
                integrated_context = ""
                avg_score = 0.0
            
            return FilteredResult(
                filtered_contexts=integrated_context,
                original_count=len(candidate_contexts),
                filtered_count=len(scoring_result.filtered_contexts),
                avg_relevance_score=avg_score,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            # 异常情况下返回原始上下文
            return FilteredResult(
                filtered_contexts="\n\n".join(candidate_contexts),
                original_count=len(candidate_contexts),
                filtered_count=len(candidate_contexts),
                avg_relevance_score=0.5,
                processing_time=time.time() - start_time
            )
    
    def _score_contexts(self, user_question: str, candidate_contexts: List[str]) -> ScoringResult:
        """
        使用LLM对上下文进行相关性评分
        
        Args:
            user_question (str): 用户问题
            candidate_contexts (List[str]): 候选上下文列表
        
        Returns:
            ScoringResult: 评分结果
        """
        try:
            # 生成评分提示词
            prompt = get_context_scoring_message(user_question, candidate_contexts)
            
            # 调用AI模型
            ai_response = self._call_ai(prompt)
            
            # 解析AI响应
            scored_contexts = []
            for item in ai_response.get("scored_contexts", []):
                context_item = ContextItem(
                    content=item.get("content", ""),
                    relevance_score=float(item.get("relevance_score", 0.0)),
                    original_index=int(item.get("original_index", -1))
                )
                scored_contexts.append(context_item)
            
            # 筛选高相关性的上下文（≥阈值）
            filtered_contexts = [
                ctx for ctx in scored_contexts 
                if ctx.relevance_score >= self.relevance_threshold
            ]
            
            # 按相关性分数降序排列
            filtered_contexts.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return ScoringResult(
                scored_contexts=scored_contexts,
                filtered_contexts=filtered_contexts,
                success=True
            )
            
        except Exception as e:
            return ScoringResult(
                scored_contexts=[],
                filtered_contexts=[],
                success=False,
                error_message=str(e)
            )
    
    def _integrate_contexts(self, filtered_contexts: List[ContextItem]) -> str:
        """
        使用LLM将筛选后的上下文进行归纳总结
        
        Args:
            filtered_contexts (List[ContextItem]): 筛选后的上下文列表
        
        Returns:
            str: 归纳总结后的精简文本
        """
        if not filtered_contexts:
            return ""
        
        # 如果只有一个上下文，进行轻度优化
        if len(filtered_contexts) == 1:
            return self._optimize_single_context(filtered_contexts[0].content)
        
        try:
            # 生成归纳总结提示词
            prompt = get_context_integration_message(filtered_contexts)
            
            # 调用AI模型进行归纳总结
            ai_response = self._call_ai(prompt)
            
            # 处理AI响应
            integrated_text = self._extract_integrated_content(ai_response)
            
            # 验证归纳结果质量
            if self._validate_integration_quality(integrated_text, filtered_contexts):
                return integrated_text
            else:
                # 质量不达标时，使用改进的简单合并
                return self._smart_concatenate_contexts(filtered_contexts)
            
        except Exception as e:
            # 异常情况下使用改进的简单合并
            return self._smart_concatenate_contexts(filtered_contexts)
    
    def _optimize_single_context(self, content: str) -> str:
        """
        对单个上下文进行轻度优化
        
        Args:
            content (str): 单个上下文内容
            
        Returns:
            str: 优化后的内容
        """
        # 移除多余的空白字符
        content = " ".join(content.split())
        
        # 基本的句子合并（简单去重）
        sentences = [s.strip() for s in content.split('。') if s.strip()]
        unique_sentences = []
        for sentence in sentences:
            if not any(sentence in existing for existing in unique_sentences):
                unique_sentences.append(sentence)
        
        return "。".join(unique_sentences) + ("。" if unique_sentences else "")
    
    def _extract_integrated_content(self, ai_response) -> str:
        """
        从AI响应中提取归纳总结的内容
        
        Args:
            ai_response: AI模型的响应
            
        Returns:
            str: 提取的内容
        """
        if isinstance(ai_response, str):
            return ai_response.strip()
        
        if isinstance(ai_response, dict):
            # 尝试多个可能的键名
            for key in ["integrated_context", "summary", "result", "content"]:
                if key in ai_response:
                    return ai_response[key].strip()
            
            # 如果都没有，返回字典的第一个值
            if ai_response:
                return str(list(ai_response.values())[0]).strip()
        
        return ""
    
    def _validate_integration_quality(self, integrated_text: str, original_contexts: List[ContextItem]) -> bool:
        """
        验证归纳总结的质量
        
        Args:
            integrated_text (str): 归纳总结的文本
            original_contexts (List[ContextItem]): 原始上下文列表
            
        Returns:
            bool: 质量是否达标
        """
        if not integrated_text.strip():
            return False
        
        # 计算原始内容总长度
        original_length = sum(len(ctx.content) for ctx in original_contexts)
        integrated_length = len(integrated_text)
        
        # 检查压缩比例（应该在20%-80%之间）
        compression_ratio = integrated_length / original_length if original_length > 0 else 0
        if compression_ratio < 0.2 or compression_ratio > 0.8:
            return False
        
        # 检查是否包含基本的句子结构
        if not any(punct in integrated_text for punct in ['。', '.', '；', ';']):
            return False
        
        return True
    
    def _smart_concatenate_contexts(self, filtered_contexts: List[ContextItem]) -> str:
        """
        智能拼接上下文（备用方案）
        
        Args:
            filtered_contexts (List[ContextItem]): 筛选后的上下文列表
            
        Returns:
            str: 智能拼接的结果
        """
        if not filtered_contexts:
            return ""
        
        contents = [ctx.content.strip() for ctx in filtered_contexts if ctx.content.strip()]
        
        # 基本去重：移除完全重复的内容
        unique_contents = []
        for content in contents:
            if content not in unique_contents:
                unique_contents.append(content)
        
        # 智能连接：根据内容特点选择连接符
        if len(unique_contents) == 1:
            return unique_contents[0]
        
        # 检查是否都是完整句子（以句号结尾）
        all_complete_sentences = all(content.endswith(('。', '.')) for content in unique_contents)
        
        if all_complete_sentences:
            # 完整句子用空格连接
            return " ".join(unique_contents)
        else:
            # 不完整句子用句号连接
            result = "。".join(content.rstrip('。.') for content in unique_contents)
            return result + "。" if result else ""
    
    def _call_ai(self, prompt: str):
        """
        调用AI模型
        
        Args:
            prompt (str): 发送给AI的提示词
            
        Returns:
            AI返回的结果
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 根据提示词类型调整参数
        is_integration_task = "归纳总结" in prompt or "深度整理" in prompt
        
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1 if not is_integration_task else 0.2,  # 归纳总结时略微增加创造性
            "max_tokens": 2000 if not is_integration_task else 1500   # 归纳总结时减少token，鼓励精简
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_content = result['choices'][0]['message']['content']
            
            # 尝试解析JSON格式的响应
            try:
                ai_content = ai_content.strip()
                if ai_content.startswith('```json'):
                    ai_content = ai_content[7:]
                if ai_content.endswith('```'):
                    ai_content = ai_content[:-3]
                ai_content = ai_content.strip()
                
                return json.loads(ai_content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接返回字符串
                return ai_content.strip()
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API调用失败: {str(e)}")
    
    def filter_retrieved_context(self, user_talk: str, context: List[RetriveResult]) -> str:
        """
        兼容旧接口：对从数据库检索出的上下文进行筛选和整理
        
        Args:
            user_talk (str): 用户当前的最新提问
            context (List[RetriveResult]): 从StorageService初步检索出的候选上下文片段
        
        Returns:
            str: 经过过滤和重新排序后的、更相关的上下文片段
        """
        # 将RetriveResult转换为字符串列表
        candidate_contexts = [item.context for item in context if hasattr(item, 'context') and item.context]
        
        # 如果没有有效的上下文，返回空字符串
        if not candidate_contexts:
            return ""
        
        # 调用新的filter_contexts方法
        result = self.filter_contexts(user_talk, candidate_contexts)
        
        # 返回筛选后的上下文字符串
        return result.filtered_contexts

    def filter_for_storage(self, data_to_store: str) -> str:
        """
        兼容旧接口：在数据存储之前进行过滤和预处理
        
        Args:
            data_to_store (str): 从外部接口接收到的原始数据片段，待过滤
        
        Returns:
            str: 经过过滤和处理后的数据片段，可用于存储
        """
        # 简单的存储前过滤逻辑
        if not data_to_store or not data_to_store.strip():
            return ""
        
        # 基本的文本清理
        cleaned_text = " ".join(data_to_store.strip().split())
        
        # 移除过短的内容（少于10个字符的内容可能没有价值）
        if len(cleaned_text) < 10:
            return ""
        
        return cleaned_text

    def get_statistics(self, result: FilteredResult) -> dict:
        """
        获取筛选统计信息
        
        Args:
            result (FilteredResult): 筛选结果
        
        Returns:
            dict: 统计信息
        """
        if result.original_count == 0:
            filter_rate = 0.0
        else:
            filter_rate = (result.original_count - result.filtered_count) / result.original_count
        
        return {
            "原始上下文数量": result.original_count,
            "筛选后数量": result.filtered_count,
            "过滤率": f"{filter_rate:.1%}",
            "平均相关性分数": f"{result.avg_relevance_score:.2f}",
            "处理耗时": f"{result.processing_time:.2f}秒"
        } 