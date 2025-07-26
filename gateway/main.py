from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
from .prompt import CUSTOM_INSTRUCTIONS

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


# @mcp.tool(
#     description="""列出 AD-Context 中存储的所有记忆。此工具提供记忆的完整列表，支持分页和过滤功能。
    
#     功能特性：
#     - 获取所有已存储的记忆列表
#     - 支持结果数量限制
#     - 支持元数据过滤
#     - 返回完整的记忆信息和元数据
    
#     适用场景：
#     - 查看所有存储的记忆概览
#     - 管理和审查记忆内容
#     - 分析记忆存储模式
#     - 进行记忆内容的批量操作准备
#     - 检查特定来源或隐私级别的记忆
    
#     返回信息包含：
#     - 记忆的完整内容
#     - 创建时间和更新时间
#     - 元数据信息（隐私级别、来源等）
#     - 记忆的唯一标识符
#     - 记忆的分类和标签信息
    
#     过滤选项：
#     - 按隐私级别过滤
#     - 按来源类型过滤
#     - 按创建时间范围过滤
#     - 按内容类型过滤
#     """
# )
# async def list_memories(limit: int = 100) -> str:
#     """列出 AD-Context 中的所有记忆
    
#     获取已存储记忆的完整列表，包含详细的元数据信息。
    
#     参数：
#         limit: 返回结果的最大数量，默认为100
    
#     返回：
#         str: JSON格式的记忆列表，包含内容、元数据和标识符信息
#     """
#     try:
#         storage_service = StorageService()
#         memories = storage_service.list(limit=limit)
        
#         return json.dumps(memories, indent=2, ensure_ascii=False)
#     except Exception as e:
#         return f"Error listing memories: {str(e)}"


# @mcp.tool(
#     description="""从 AD-Context 中删除指定的记忆。此工具允许永久删除不再需要的记忆内容。
    
#     功能特性：
#     - 根据记忆ID精确删除
#     - 永久性删除操作
#     - 返回删除操作结果
#     - 支持删除确认
    
#     使用场景：
#     - 删除过时或错误的记忆
#     - 清理不再相关的信息
#     - 管理存储空间
#     - 维护记忆数据的准确性
#     - 遵守数据保护和隐私要求
    
#     注意事项：
#     - 删除操作不可逆转
#     - 需要提供准确的记忆ID
#     - 删除后相关的搜索结果将不再包含该记忆
#     - 建议在删除前先通过list_memories确认要删除的内容
    
#     安全考虑：
#     - 确保有删除权限
#     - 验证记忆ID的正确性
#     - 考虑删除对其他相关记忆的影响
#     """
# )
# async def delete_memory(memory_id: str) -> str:
#     """从 AD-Context 中删除指定记忆
    
#     根据记忆ID永久删除指定的记忆内容。
    
#     参数：
#         memory_id: 要删除的记忆的唯一标识符
    
#     返回：
#         str: JSON格式的删除操作结果
#     """
#     try:
#         storage_service = StorageService()
#         result = storage_service.delete(memory_id)
        
#         return json.dumps(result, indent=2, ensure_ascii=False)
#     except Exception as e:
#         return f"Error deleting memory: {str(e)}"


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建一个可以通过 SSE 服务提供的 MCP 服务器的 Starlette 应用程序"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        """处理 SSE 连接"""
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='运行基于 SSE 的 MCP 服务器')
    parser.add_argument('--host', default='0.0.0.0', help='绑定的主机地址')
    parser.add_argument('--port', type=int, default=1234, help='监听的端口')
    args = parser.parse_args()

    # 将 SSE 请求处理绑定到 MCP 服务器
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)