from fastmcp import FastMCP  # 修正导入语句
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
from gateway.prompt import CUSTOM_INSTRUCTIONS  # 修改为绝对导入

from storage.service import StorageService

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("AD-Context")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "trae_user"

# 更新项目自定义指令
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""将用户记忆添加到 AD-Context 中。此工具存储用户的个人信息、偏好、习惯、学习与知识偏好、认知模式与沟通风格、历史互动与核心记忆。
    
    功能特性：
    - 支持语义索引和检索
    - 自动推理和提取关键信息
    - 支持隐私级别控制
    - 支持元数据标记
    
    存储每个记忆时，您应包括：
    - 个人信息（姓名、年龄、性别、地区、职业、教育背景等）
    - 偏好（色彩偏好、设计风格、时尚/穿衣风格、音乐品味、阅读偏好等）
    - 习惯（作息规律、生活习惯、工作习惯、运动习惯等）
    - 学习与知识偏好（学习方式、特别感兴趣的知识主题、技能水平等）
    - 认知模式与沟通风格（思维模式、沟通风格、决策方式、问题解决方法等）
    - 历史互动与核心记忆（关键对话与共识、重要事件、里程碑等）
    - 目标与计划（短期目标、长期规划、项目计划等）
    
    该记忆将被索引以进行语义搜索，并可稍后使用自然语言查询进行检索。
    支持的隐私级别：LEVEL_1_PUBLIC（公开）、LEVEL_2_INTERNAL（内部）、LEVEL_3_CONFIDENTIAL（机密）、LEVEL_4_RESTRICTED（限制）、LEVEL_5_TOP_SECRET（绝密）。
    """
)
async def add_memory(text: str) -> str:
    """向 AD-Context 添加新的记忆
    
    此工具使用 StorageService 来存储用户记忆，支持自动推理和元数据管理。
    
    参数：
        text: 要存储在记忆中的内容，包括个人信息、偏好、习惯、学习与知识偏好、认知模式与沟通风格、历史互动与核心记忆。
    
    返回：
        str: 操作结果消息，包含成功或失败信息。
    """
    try:
        from schemas.common import Metadata
        from schemas.privacy import PrivacyLevel
        
        # 创建默认的元数据
        metadata = Metadata(
            privacy_level=PrivacyLevel.LEVEL_1_PUBLIC,
            source="user_input"
        )
        
        result = StorageService().add(text, metadata)
        return result
    except Exception as e:
        return f"Error adding memory: {str(e)}"


@mcp.tool(
    description="""使用语义搜索在 AD-Context 中搜索已存储的记忆。此工具能够根据查询文本找到最相关的记忆片段。
    
    功能特性：
    - 基于语义理解的智能搜索
    - 支持自然语言查询
    - 可配置返回结果数量
    - 支持元数据过滤
    - 返回相关性评分
    
    适用场景：
    - 查找特定的个人信息或偏好
    - 搜索相关的历史对话或事件
    - 检索特定主题的知识和经验
    - 查找相似的习惯或行为模式
    - 搜索特定时间段或来源的记忆
    
    搜索支持：
    - 模糊匹配和语义理解
    - 多关键词组合查询
    - 上下文相关性分析
    - 同义词和相关概念匹配
    
    返回结果包含：
    - 匹配的记忆内容
    - 相关性评分
    - 元数据信息（隐私级别、来源等）
    - 创建时间等附加信息
    """
)
async def search_memory(query_text: str, top_k: int = 5) -> str:
    """在 AD-Context 中搜索记忆
    
    使用语义搜索技术在已存储的记忆中查找与查询最相关的内容，
    并通过AI过滤器筛选出最有用的信息。
    
    参数：
        query_text: 搜索查询文本，支持自然语言描述
        top_k: 返回最相似结果的数量，默认为5
    
    返回：
        str: JSON格式的搜索结果，包含过滤后的相关内容和原始匹配结果
    """
    try:
        # <time>:search_start - 开始搜索记忆
        print(f"<time>:search_start - 开始搜索记忆，查询: {query_text}")
        
        storage_service = StorageService()
        results = storage_service.search(query_text, top_k=top_k)
        
        # <time>:search_complete - 搜索完成
        print(f"<time>:search_complete - 搜索完成，找到 {len(results)} 个结果")
        
        # 转换为JSON格式
        formatted_results = []
        candidate_contexts = []  # 用于过滤的候选上下文
        
        for result in results:
            formatted_result = {
                "content": result.context,
                "score": result.score,
                "metadata": {
                    "privacy_level": result.metadata.privacy_level.value,
                    "source": result.metadata.source
                }
            }
            formatted_results.append(formatted_result)
            candidate_contexts.append(result.context)
        
        # <time>:filter_start - 开始过滤搜索结果
        print("<time>:filter_start - 开始使用FilterService过滤搜索结果")
        
        # 使用FilterService过滤搜索结果
        filtered_content = ""
        if candidate_contexts:
            try:
                from services.filter.filter_service import FilterService
                filter_service = FilterService()
                filtered_content = filter_service.filter_contexts(query_text, candidate_contexts)
                
                # <time>:filter_complete - 过滤完成
                print(f"<time>:filter_complete - 过滤完成，过滤后内容长度: {len(filtered_content)}")
                
            except Exception as filter_error:
                # <time>:filter_error - 过滤过程出错
                print(f"<time>:filter_error - 过滤过程出错: {str(filter_error)}")
                # 如果过滤失败，继续返回原始结果
                pass
        
        # 构建最终响应
        response_data = {
            "filtered_summary": filtered_content,  # AI过滤后的摘要
            "raw_results": formatted_results,      # 原始搜索结果
            "query": query_text,
            "total_found": len(results),
            "has_filtered_content": bool(filtered_content)
        }
        
        # <time>:response_ready - 响应准备完成
        print("<time>:response_ready - 搜索和过滤完成，准备返回结果")
        
        return json.dumps(response_data, indent=2, ensure_ascii=False)
        
    except Exception as e:
        # <time>:search_error - 搜索过程出错
        print(f"<time>:search_error - 搜索过程出错: {str(e)}")
        return f"Error searching memories: {str(e)}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='运行基于 Streamable HTTP 的 MCP 服务器')
    parser.add_argument('--host', default='127.0.0.1', help='绑定的主机地址')  # 改为默认本地地址
    parser.add_argument('--port', type=int, default=1234, help='监听的端口')
    parser.add_argument('--log-level', default='info', help='日志级别')
    args = parser.parse_args()

    # 使用 Streamable HTTP 传输运行服务器
    # 根据 FastMCP 文档，正确的参数格式
    mcp.run(
        transport="streamable-http",  # 或者使用 "http" 作为别名
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )