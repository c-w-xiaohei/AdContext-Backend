import os
from datetime import datetime
from typing import Optional, List
import json
import requests

from schemas.privacy import PrivacyLevel, PrivacyLabel


# 隐私分级评估提示词
# 用于分析上下文片段并为其分配准确的隐私敏感度级别
# 基于1-5级分级标准，其中5级为最敏感信息
PRIVACY_CLASSIFICATION_PROMPT = f"""你是一个专业的隐私数据分类专家，负责评估文本内容的隐私敏感度级别。你的任务是分析给定的上下文片段，并为其分配准确的隐私级别（1-5级）。

## 隐私分级标准：

**1级 - 公开可检索 (Non-Sensitive)**
- 判定标准：已在互联网上公开发布；法规无任何保护要求；泄露基本无风险
- 示例：公司官网文章、博客、开源 README、公开招聘信息

**2级 - 内部日常 (Low)**
- 判定标准：未公开，但不含可识别个人/商业关键；泄露仅带来轻微不便或品牌喧声
- 示例：例行会议议程、团队 OKR 概览、个人兴趣偏好（爱喝拿铁）

**3级 - 受限敏感 (Moderate)**
- 判定标准：间接识别个人（姓名+职位+公司电邮）；一般商业机密（产品路线图、成本结构）；法规要求"合理保护"
- 示例：员工花名册（无身份证号）、未发布功能设计文档、财务预算概览

**4级 - 机密/合规管控 (Confidential)**
- 判定标准：公司核心竞争信息：源代码、算法细节、技术价格；法规要求备案或严格披露义务（上市前财务报表、并购清单）；泄露将导致重大商业/法律风险
- 示例：专利草稿、年度财务预测表、关键算法参数

**5级 - 极端敏感/关键凭证 (Critical)**
- 判定标准：直接识别或不可逆危害：身份证号、银行卡号、CVV、健康/基因数据；任一可造成账号接管、资金损失、重大安全事故的凭证；受 GDPR《特殊类别数据》、HIPAA、PCI-DSS 等强监管
- 示例：私钥/助记词、生产数据库 root 密码、生物特征模板、MRI 影像、完整客户信用卡记录

## 分析指导原则：

1. **精确识别**：仔细分析文本中的每个关键信息点
2. **风险评估**：考虑信息泄露可能造成的实际影响
3. **合规考量**：评估是否涉及法规保护要求
4. **上下文理解**：结合具体场景判断敏感度
5. **保守原则**：在不确定时倾向于选择更高的安全级别

## 输出要求：

你必须以JSON格式返回分析结果，包含以下字段：

```json
{{
    "privacy_level": <1-5的整数>,
    "confidence": <0.0-1.0的浮点数，表示分类置信度>,
    "brief": "<在不泄露隐私的前提下，对这段隐私信息进行总结归纳，这段归纳必须是一个断言，具有以下接口：xxxx是一条隐私数据>",
    "risk_indicators": ["<风险指标1>", "<风险指标2>", "..."],
    "compliance_notes": "<如适用，说明相关的法规要求>"
}}
```

## 特殊注意事项：

- 今天的日期是 {datetime.now().strftime("%Y-%m-%d")}
- 严格按照5级分类标准进行评估
- 如果文本包含多种敏感度的信息，选择最高敏感度级别
- 考虑信息组合可能产生的敏感度提升
- 对于模糊情况，提供详细的brief说明判断依据

请分析以下上下文片段：
"""


# 获取隐私分类消息的函数
# 用于格式化隐私分类请求，将上下文片段组合成完整的提示词
# 参数说明：
# - context_fragment: 需要分析的上下文片段
# - additional_context: 额外的上下文信息（可选）
def get_privacy_classification_message(context_fragment: str, additional_context: Optional[str] = None):
    """
    获取隐私分类分析消息
    
    Args:
        context_fragment (str): 需要分析的上下文片段
        additional_context (str, optional): 额外的上下文信息
    
    Returns:
        str: 格式化的隐私分类提示词
    """
    message = f"""{PRIVACY_CLASSIFICATION_PROMPT}

**待分析的上下文片段：**
```
{context_fragment}
```
"""
    
    if additional_context:
        message += f"""
**额外上下文信息：**
```
{additional_context}
```
"""
    
    message += """
请根据上述分级标准，对该上下文片段进行隐私敏感度分析，并以JSON格式返回结果。

注意：除了JSON格式之外不要返回任何其他内容。
"""
    
    return message


class PrivacyClassifier:
    """隐私分级分类器"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model_name: str = "gemini-2.5-flash-lite"):
        """
        初始化隐私分类器
        
        Args:
            api_key (str, optional): AiHubMix API密钥. 如果未提供，将从环境变量 AIHUBMIX_API_KEY 读取.
            model_name (str): 使用的模型名称，默认为gemini-2.5-flash-lite
        """
        self.classification_prompt = PRIVACY_CLASSIFICATION_PROMPT
        
        resolved_api_key = api_key or os.environ.get("AIHUBMIX_API_KEY")
        if not resolved_api_key:
            raise ValueError("AiHubMix API Key not provided. Please pass it as an argument or set the AIHUBMIX_API_KEY environment variable.")
            
        self.api_key = resolved_api_key
        self.model_name = model_name
        self.api_url = "https://aihubmix.com/v1/chat/completions"
    
    def get_classification_prompt(self, context_fragment: str, additional_context: Optional[str] = None) -> str:
        """
        获取隐私分类提示词
        
        Args:
            context_fragment (str): 需要分析的上下文片段
            additional_context (str, optional): 额外的上下文信息
        
        Returns:
            str: 格式化的隐私分类提示词
        """
        return get_privacy_classification_message(context_fragment, additional_context)
    
    def parse_classification_result(self, result: dict) -> PrivacyLabel:
        """
        解析分类结果为PrivacyLabel对象
        
        Args:
            result (dict): AI返回的分类结果JSON
        
        Returns:
            PrivacyLabel: 解析后的隐私标签对象
        """
        privacy_level = PrivacyLevel(result.get("privacy_level", 1))
        confidence = float(result.get("confidence", 0.0))
        brief = result.get("brief", "")
        risk_indicators = result.get("risk_indicators", [])
        compliance_notes = result.get("compliance_notes")
        
        return PrivacyLabel(
            level=privacy_level,
            confidence=confidence,
            brief=brief,
            risk_indicators=risk_indicators,
            compliance_notes=compliance_notes
        )
    
    def _call_ai(self, prompt: str) -> dict:
        """
        调用AiHubMix的Gemini模型
        
        Args:
            prompt (str): 发送给AI的提示词
            
        Returns:
            dict: AI返回的结果字典
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # 降低随机性，提高分类一致性
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_content = result['choices'][0]['message']['content']
            
            # 尝试解析AI返回的JSON
            try:
                # 清理可能的markdown格式
                ai_content = ai_content.strip()
                if ai_content.startswith('```json'):
                    ai_content = ai_content[7:]
                if ai_content.endswith('```'):
                    ai_content = ai_content[:-3]
                ai_content = ai_content.strip()
                
                return json.loads(ai_content)
            except json.JSONDecodeError:
                # 如果解析失败，返回默认结果
                return {
                    "privacy_level": 1,
                    "confidence": 0.0,
                    "brief": f"AI返回格式解析失败: {ai_content}",
                    "risk_indicators": ["解析错误"],
                    "compliance_notes": None
                }
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def classify(self, context_fragment: str, additional_context: Optional[str] = None) -> PrivacyLabel:
        """
        直接对文本进行隐私分级分析
        
        Args:
            context_fragment (str): 需要分析的上下文片段
            additional_context (str, optional): 额外的上下文信息
            
        Returns:
            PrivacyLabel: 隐私分级结果
            
        Raises:
            Exception: AI调用失败时抛出异常
        """
        # 生成提示词
        prompt = self.get_classification_prompt(context_fragment, additional_context)
        
        # 调用AI模型
        ai_result = self._call_ai(prompt)
        
        # 解析并返回结果
        return self.parse_classification_result(ai_result)
 