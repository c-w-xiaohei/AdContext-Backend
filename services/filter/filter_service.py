import os
import json
import time
from typing import List, Optional
from openai import OpenAI
from .prompts import get_context_integration_message

# 添加dotenv支持
try:
    from dotenv import load_dotenv
    # 加载当前目录的.env文件
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass  # 如果没有安装python-dotenv，忽略

class FilterService:
    """上下文质量与相关性筛选服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: Optional[str] = None,
                 api_url: Optional[str] = None,
                 relevance_threshold: float = 0.3):
        """
        初始化FilterService
        
        Args:
            api_key (str, optional): OpenAI API密钥. 如果未提供，将从环境变量 OPENAI_API_KEY 读取.
            model_name (str, optional): 使用的模型名称. 如果未提供，将从环境变量 OPENAI_MODEL_NAME 读取.
            api_url (str, optional): API服务地址. 如果未提供，将从环境变量 OPENAI_BASE_URL 读取.
            relevance_threshold (float): 相关性分数阈值，低于此值的上下文将被移除
        """
        resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_api_key:
            raise ValueError("OpenAI API Key not provided. Please pass it as an argument or set the OPENAI_API_KEY environment variable.")
            
        self.model_name = model_name or os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        self.relevance_threshold = relevance_threshold
        base_url = api_url or os.environ.get("OPENAI_BASE_URL")
        
        # 初始化OpenAI客户端
        if base_url:
            self.client = OpenAI(api_key=resolved_api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=resolved_api_key)
    
    def filter_contexts(self, user_talk: str, candidate_contexts: List[str]) -> str:
        """
        对候选上下文进行筛选和整理，返回相关内容或空字符串
        
        Args:
            user_talk (str): 用户问题/对话
            candidate_contexts (List[str]): 候选上下文列表
        
        Returns:
            str: 筛选整理后的相关内容，如果没有相关内容则返回空字符串
        """
        # 如果没有候选上下文，直接返回空字符串
        if not candidate_contexts:
            return ""
        
        try:
            # 创建临时对象来匹配函数期望的格式
            from types import SimpleNamespace
            context_objects = [SimpleNamespace(content=context) for context in candidate_contexts]
            prompt = f"""{get_context_integration_message(context_objects)}
            
用户问题: {user_talk}
            
请根据用户问题对以上记忆片段进行筛选和归纳总结："""
            
            # 调用AI模型
            ai_response = self._call_ai(prompt)
            
            # 处理AI响应
            if isinstance(ai_response, str):
                result = ai_response.strip()
            elif isinstance(ai_response, dict):
                # 尝试从字典中提取内容
                result = ai_response.get('content', ai_response.get('result', str(ai_response))).strip()
            else:
                result = str(ai_response).strip()
            
            # 如果结果为空或只包含无意义内容，返回空字符串
            if not result or result.lower() in ['无', '无相关内容', '没有相关内容', 'none', '']:
                return ""
            
            return result
            
        except Exception as e:
            # 异常情况下返回空字符串，避免程序崩溃
            print(f"筛选过程中出现错误: {str(e)}")
            return ""
    
    def _call_ai(self, prompt: str):
        """
        调用OpenAI模型
        
        Args:
            prompt (str): 发送给AI的提示词
            
        Returns:
            AI返回的结果
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        # 根据提示词类型调整参数
        is_integration_task = "归纳总结" in prompt or "深度整理" in prompt
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1 if not is_integration_task else 0.2,  # 归纳总结时略微增加创造性
                max_tokens=2000 if not is_integration_task else 1500   # 归纳总结时减少token，鼓励精简
            )
            
            ai_content = response.choices[0].message.content
            
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
                
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")