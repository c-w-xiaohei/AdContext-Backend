"""
Filter层提示词模板

包含上下文相关性评分和整理的提示词
"""

# 上下文相关性评分提示词
# 用于对候选上下文进行相关性评分和筛选
CONTEXT_SCORING_PROMPT = """你是一个专业的上下文相关性评估专家，负责评估记忆片段与用户问题的相关性。

## 任务说明
用户提出了一个问题，系统检索出了一些相关的记忆片段。你需要：
1. 为每个记忆片段评估其与用户问题的相关性，给出0.0-1.0的分数
2. 移除相关性分数低于0.3的片段
3. 按分数从高到低重新排列剩余片段

## 评分标准
- **1.0分**: 完全匹配用户问题，直接包含答案或关键信息
- **0.8-0.9分**: 高度相关，包含重要的相关信息
- **0.6-0.7分**: 中等相关，包含部分相关信息
- **0.4-0.5分**: 低度相关，仅有间接关联
- **0.1-0.3分**: 几乎无关，应被移除
- **0.0分**: 完全无关，必须移除

## 输出格式
你必须以JSON格式返回结果：

```json
{{
    "scored_contexts": [
        {{
            "content": "记忆片段内容",
            "relevance_score": 0.85,
            "original_index": 0
        }},
        ...
    ],
    "summary": "简要说明评分依据"
}}
```

## 注意事项
- 严格按照JSON格式输出
- 只保留相关性分数≥0.3的片段
- 按分数降序排列
- 分数保留2位小数

现在开始评估：

**用户问题**: {user_question}

**候选记忆片段**:
{candidate_contexts}

请进行相关性评分和筛选："""


# 上下文整理提示词
# 用于将筛选后的上下文整理成连贯的描述
CONTEXT_INTEGRATION_PROMPT = """你是一个专业的信息归纳总结专家，负责将多个相关的记忆片段进行深度整理和归纳。

## 核心任务
将提供的记忆片段进行智能归纳总结，输出比原始内容更加精简、逻辑清晰的结果。

## 处理原则
1. **信息提取**: 识别并提取所有关键信息点
2. **去重合并**: 合并重复或相似的信息，避免冗余
3. **逻辑重构**: 按照时间、类型、重要性等维度重新组织信息
4. **精简表达**: 用更简洁的语言表达相同的含义
5. **结构化输出**: 采用合理的段落结构，提高可读性

## 归纳策略
- **人物信息**: 合并职务、联系方式、特点等
- **事件信息**: 按时间顺序或因果关系整理
- **技术信息**: 按功能分类，突出核心要点
- **描述信息**: 提取核心特征，去除冗余修饰

## 输出要求
- 比原始片段更加精简（减少20-40%的字数）
- 逻辑结构更加清晰
- 信息密度更高
- 保持事实准确性
- 不添加推测内容
- 不包含"根据记忆片段"等元信息

## 示例对比
**原始片段（冗余）**:
"张三是公司的产品经理。张三负责新产品的规划。张三昨天开会了。张三的邮箱是xxx。"

**归纳结果（精简）**:
"张三是产品经理，负责新产品规划，邮箱为xxx。"

以下是需要归纳整理的记忆片段：
{filtered_contexts}

请进行深度归纳总结："""


# 获取上下文评分消息
def get_context_scoring_message(user_question: str, candidate_contexts: list) -> str:
    """
    生成上下文评分提示词
    
    Args:
        user_question (str): 用户问题
        candidate_contexts (list): 候选上下文列表
    
    Returns:
        str: 格式化的评分提示词
    """
    # 格式化候选上下文
    formatted_contexts = ""
    for i, context in enumerate(candidate_contexts):
        formatted_contexts += f"[{i}] {context}\n\n"
    
    return CONTEXT_SCORING_PROMPT.format(
        user_question=user_question,
        candidate_contexts=formatted_contexts.strip()
    )


# 获取上下文整理消息
def get_context_integration_message(filtered_contexts: list) -> str:
    """
    生成上下文整理提示词
    
    Args:
        filtered_contexts (list): 筛选后的上下文列表
    
    Returns:
        str: 格式化的整理提示词
    """
    # 格式化筛选后的上下文
    formatted_contexts = ""
    for i, context_item in enumerate(filtered_contexts, 1):
        formatted_contexts += f"{i}. {context_item.content}\n\n"
    
    return CONTEXT_INTEGRATION_PROMPT.format(
        filtered_contexts=formatted_contexts.strip()
    ) 