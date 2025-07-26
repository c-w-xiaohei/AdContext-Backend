from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
import uuid
import asyncio
from typing import Dict, Optional
from .prompt import CUSTOM_INSTRUCTIONS

from storage.service import StorageService

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("AD-Context")

# Initialize mem0 client and set default user
# 添加错误处理的mem0初始化
try:
    mem0_client = MemoryClient()
    DEFAULT_USER_ID = "trae_user"
    # 更新项目自定义指令
    mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)
    print("Mem0客户端初始化成功")
except Exception as e:
    print(f"Mem0客户端初始化失败: {e}")
    print("服务器将在没有mem0功能的情况下启动")
    mem0_client = None
    DEFAULT_USER_ID = "trae_user"

# 会话管理
active_sessions: Dict[str, dict] = {}

# 支持的协议版本
SUPPORTED_PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]
DEFAULT_PROTOCOL_VERSION = "2025-06-18"

# 更新项目自定义指令
if mem0_client:
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
    集成隐私分类器自动评估记忆内容的隐私敏感度级别。
    
    参数：
        text: 要存储在记忆中的内容，包括个人信息、偏好、习惯、学习与知识偏好、认知模式与沟通风格、历史互动与核心记忆。
    
    返回：
        str: 操作结果消息，包含成功或失败信息以及隐私级别评估结果。
    """
    if mem0_client is None:
        return "错误：Mem0客户端未初始化，无法添加记忆"
    try:
        from schemas.common import Metadata
        from schemas.privacy import PrivacyLevel
        from services.privacy.privacy_classifier import SimplePrivacyClassifier
        
        # <time>:privacy_classification_start - 开始隐私级别分类
        print(f"<time>:privacy_classification_start - 开始对记忆内容进行隐私级别评估")
        
        # 使用隐私分类器评估内容的隐私级别
        privacy_classifier = SimplePrivacyClassifier()
        privacy_level_int = privacy_classifier.classify(text)
        
        # 将整数级别转换为对应的PrivacyLevel枚举
        privacy_level_mapping = {
            1: PrivacyLevel.LEVEL_1_PUBLIC,
            2: PrivacyLevel.LEVEL_2_INTERNAL,
            3: PrivacyLevel.LEVEL_3_RESTRICTED,
            4: PrivacyLevel.LEVEL_4_CONFIDENTIAL,
            5: PrivacyLevel.LEVEL_5_CRITICAL
        }
        
        privacy_level = privacy_level_mapping.get(privacy_level_int, PrivacyLevel.LEVEL_1_PUBLIC)
        
        # <time>:privacy_classification_complete - 隐私级别分类完成
        print(f"<time>:privacy_classification_complete - 隐私级别评估完成，级别: {privacy_level_int}")
        
        # 创建包含隐私级别的元数据
        metadata = Metadata(
            privacy_level=privacy_level,
            source="user_input"
        )
        
        # <time>:storage_start - 开始存储记忆
        print("<time>:storage_start - 开始存储记忆到数据库")
        
        result = StorageService().add(text, metadata)
        
        # <time>:storage_complete - 存储完成
        print("<time>:storage_complete - 记忆存储完成")
        
        # 返回包含隐私级别信息的结果
        privacy_labels = {
            1: "公开信息",
            2: "内部日常", 
            3: "受限敏感",
            4: "机密信息",
            5: "极端敏感"
        }
        
        privacy_description = f"{privacy_level_int}级 - {privacy_labels[privacy_level_int]}"
        
        return f"{result}\n隐私级别评估: {privacy_description}"
        
    except Exception as e:
        # <time>:add_memory_error - 添加记忆过程出错
        print(f"<time>:add_memory_error - 添加记忆过程出错: {str(e)}")
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


def create_streamable_http_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建支持Streamable HTTP传输的MCP服务器应用程序
    
    Streamable HTTP是MCP的现代传输格式，特点：
    - 单一的/mcp端点处理所有请求
    - 通过Mcp-Session-Id头部管理会话
    - 支持JSON和SSE响应格式
    - 更好的基础设施兼容性
    - 支持协议版本协商
    - 实现安全性检查
    
    参数：
        mcp_server: MCP服务器实例
        debug: 是否启用调试模式
    
    返回：
        Starlette: 配置好的Starlette应用程序
    """
    
    def validate_origin(request: Request) -> bool:
        """验证Origin头部以防止DNS重绑定攻击"""
        origin = request.headers.get("Origin")
        if not origin:
            return True  # 允许没有Origin的请求（如直接API调用）
        
        # 检查是否为本地主机
        allowed_origins = [
            "http://localhost",
            "https://localhost", 
            "http://127.0.0.1",
            "https://127.0.0.1"
        ]
        
        for allowed in allowed_origins:
            if origin.startswith(allowed):
                return True
                
        return False
    
    def get_protocol_version(request: Request) -> str:
        """获取并验证协议版本"""
        version = request.headers.get("MCP-Protocol-Version")
        if not version:
            return "2025-03-26"  # 向后兼容的默认版本
        
        if version in SUPPORTED_PROTOCOL_VERSIONS:
            return version
        
        return None  # 不支持的版本
    
    async def handle_mcp_request(request: Request) -> JSONResponse | StreamingResponse:
        """处理Streamable HTTP MCP请求
        
        根据请求头和内容类型决定返回JSON还是SSE流响应。
        支持会话管理和多种响应格式。
        
        参数：
            request: Starlette请求对象
            
        返回：
            JSONResponse | StreamingResponse: 根据请求类型返回相应格式的响应
        """
        # 安全性检查：验证Origin头部
        if not validate_origin(request):
            return JSONResponse(
                {"error": "Invalid origin"}, 
                status_code=403
            )
        
        # 协议版本检查
        protocol_version = get_protocol_version(request)
        if protocol_version is None:
            return JSONResponse(
                {"error": "Unsupported protocol version"}, 
                status_code=400
            )
        
        # 获取或创建会话ID
        session_id = request.headers.get("Mcp-Session-Id")
        
        # 处理会话管理
        if request.method == "DELETE":
            return await handle_session_deletion(request, session_id)
        
        # 对于非初始化请求，检查会话ID
        if session_id and session_id not in active_sessions:
            # 会话不存在或已过期
            return JSONResponse(
                {"error": "Session not found or expired"}, 
                status_code=404
            )
        
        # 检查是否请求SSE流
        accept_header = request.headers.get("Accept", "")
        wants_sse = "text/event-stream" in accept_header
        
        if request.method == "GET":
            if wants_sse:
                # 返回SSE流响应
                return await handle_sse_stream(request, session_id, mcp_server, protocol_version)
            else:
                return JSONResponse(
                    {"error": "Method not allowed"}, 
                    status_code=405
                )
        elif request.method == "POST":
            if wants_sse:
                # POST请求可能返回SSE流
                return await handle_post_with_sse(request, session_id, mcp_server, protocol_version)
            else:
                # 返回JSON响应
                return await handle_json_request(request, session_id, mcp_server, protocol_version)
        else:
            return JSONResponse(
                {"error": "Method not allowed"}, 
                status_code=405
            )
    
    async def handle_session_deletion(request: Request, session_id: str) -> JSONResponse:
        """处理会话删除请求"""
        if not session_id:
            return JSONResponse(
                {"error": "Session ID required"}, 
                status_code=400
            )
        
        if session_id in active_sessions:
            del active_sessions[session_id]
            return JSONResponse({"message": "Session terminated"}, status_code=200)
        else:
            return JSONResponse(
                {"error": "Session not found"}, 
                status_code=404
            )
    
    async def handle_json_request(request: Request, session_id: str, mcp_server: Server, protocol_version: str) -> JSONResponse:
        """处理JSON格式的MCP请求
        
        处理标准的JSON-RPC请求并返回JSON响应。
        
        参数：
            request: HTTP请求对象
            session_id: 会话标识符
            mcp_server: MCP服务器实例
            protocol_version: 协议版本
            
        返回：
            JSONResponse: JSON格式的响应
        """
        try:
            # 解析请求体
            body = await request.body()
            if not body:
                return JSONResponse(
                    {"error": "Empty request body"}, 
                    status_code=400,
                    headers={"Mcp-Session-Id": session_id} if session_id else {}
                )
            
            # 解析JSON-RPC消息
            try:
                message = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                return JSONResponse(
                    {"error": "Invalid JSON"}, 
                    status_code=400,
                    headers={"Mcp-Session-Id": session_id} if session_id else {}
                )
            
            # 处理MCP消息
            response_data, new_session_id = await process_mcp_message(mcp_server, message, session_id, protocol_version)
            
            # 构建响应头
            response_headers = {}
            if new_session_id:
                response_headers["Mcp-Session-Id"] = new_session_id
            elif session_id:
                response_headers["Mcp-Session-Id"] = session_id
            
            # 如果是通知消息（没有响应），返回202 Accepted
            if response_data is None:
                return JSONResponse(
                    {},
                    status_code=202,
                    headers=response_headers
                )
            
            return JSONResponse(
                response_data,
                headers=response_headers
            )
            
        except Exception as e:
            return JSONResponse(
                {"error": f"Internal server error: {str(e)}"}, 
                status_code=500,
                headers={"Mcp-Session-Id": session_id} if session_id else {}
            )
    
    async def handle_post_with_sse(request: Request, session_id: str, mcp_server: Server, protocol_version: str) -> StreamingResponse:
        """处理POST请求并返回SSE流"""
        try:
            body = await request.body()
            if not body:
                # 返回错误的SSE流
                async def error_stream():
                    yield f"data: {{\"error\": \"Empty request body\"}}

"
                return StreamingResponse(
                    error_stream(),
                    media_type="text/event-stream",
                    status_code=400
                )
            
            message = json.loads(body.decode('utf-8'))
            
            async def response_stream():
                try:
                    # 处理消息并获取响应
                    response_data, new_session_id = await process_mcp_message(mcp_server, message, session_id, protocol_version)
                    
                    # 发送响应
                    if response_data:
                        event_data = json.dumps(response_data, ensure_ascii=False)
                        yield f"data: {event_data}

"
                    
                except Exception as e:
                    error_data = json.dumps({
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }, ensure_ascii=False)
                    yield f"data: {error_data}

"
            
            headers = {
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
            
            if session_id:
                headers["Mcp-Session-Id"] = session_id
            
            return StreamingResponse(
                response_stream(),
                media_type="text/event-stream",
                headers=headers
            )
            
        except Exception as e:
            async def error_stream():
                yield f"data: {{\"error\": \"Internal server error: {str(e)}\"}}

"
            return StreamingResponse(
                error_stream(),
                media_type="text/event-stream",
                status_code=500
            )
    
    async def handle_sse_stream(request: Request, session_id: str, mcp_server: Server, protocol_version: str) -> StreamingResponse:
        """处理SSE流格式的MCP请求
        
        创建Server-Sent Events流来处理实时通信。
        
        参数：
            request: HTTP请求对象
            session_id: 会话标识符
            mcp_server: MCP服务器实例
            protocol_version: 协议版本
            
        返回：
            StreamingResponse: SSE流响应
        """
        # 检查Last-Event-ID头部以支持断线重连
        last_event_id = request.headers.get("Last-Event-ID")
        
        async def event_stream():
            """生成SSE事件流"""
            event_counter = 0
            try:
                # 如果有Last-Event-ID，尝试从该点恢复
                if last_event_id:
                    try:
                        event_counter = int(last_event_id) + 1
                    except ValueError:
                        event_counter = 0
                
                # 发送会话建立事件
                yield f"id: {event_counter}
data: {{\"type\": \"session_established\", \"session_id\": \"{session_id}\", \"protocol_version\": \"{protocol_version}\"}}

"
                event_counter += 1
                
                # 保持连接并处理消息
                while True:
                    # 心跳间隔
                    await asyncio.sleep(30)
                    yield f"id: {event_counter}
data: {{\"type\": \"heartbeat\", \"timestamp\": \"{asyncio.get_event_loop().time()}\"}}

"
                    event_counter += 1
                    
            except asyncio.CancelledError:
                # 客户端断开连接
                if session_id and session_id in active_sessions:
                    active_sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()
                raise
        
        # 更新或创建会话
        if session_id:
            if session_id in active_sessions:
                active_sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()
            else:
                active_sessions[session_id] = {
                    "created_at": asyncio.get_event_loop().time(),
                    "last_activity": asyncio.get_event_loop().time(),
                    "protocol_version": protocol_version
                }
        
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        if session_id:
            headers["Mcp-Session-Id"] = session_id
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers=headers
        )
    
    async def process_mcp_message(mcp_server: Server, message: dict, session_id: Optional[str], protocol_version: str) -> tuple[dict, Optional[str]]:
        """处理MCP消息并返回响应
        
        使用MCP服务器处理JSON-RPC消息。
        
        参数：
            mcp_server: MCP服务器实例
            message: JSON-RPC消息
            session_id: 当前会话ID
            protocol_version: 协议版本
            
        返回：
            tuple: (响应消息, 新会话ID)
        """
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params", {})
        
        try:
            # 处理初始化请求
            if method == "initialize":
                # 生成新的会话ID
                new_session_id = str(uuid.uuid4())
                
                # 返回服务器capabilities
                capabilities = {
                    "tools": {},  # 支持工具调用
                    "resources": {},  # 支持资源访问
                    "prompts": {},  # 支持提示模板
                    "logging": {}  # 支持日志记录
                }
                
                # 创建新会话
                active_sessions[new_session_id] = {
                    "created_at": asyncio.get_event_loop().time(),
                    "last_activity": asyncio.get_event_loop().time(),
                    "protocol_version": protocol_version
                }
                
                response = {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": protocol_version,
                        "capabilities": capabilities,
                        "serverInfo": {
                            "name": "AD-Context",
                            "version": "1.0.0"
                        }
                    }
                }
                
                return response, new_session_id
            
            # 处理初始化完成通知
            elif method == "notifications/initialized":
                # 这是一个通知，不需要响应
                return None, None
            
            # 处理工具列表请求
            elif method == "tools/list":
                tools = []
                for tool_name, tool_info in mcp_server._tools.items():
                    tools.append({
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "inputSchema": tool_info.get("inputSchema", {})
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {"tools": tools}
                }, None
            
            # 处理工具调用请求
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                if tool_name in mcp_server._tools:
                    # 调用对应的工具函数
                    tool_func = mcp_server._tools[tool_name]["func"]
                    try:
                        result = await tool_func(**tool_arguments)
                        return {
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": str(result)
                                    }
                                ]
                            }
                        }, None
                    except Exception as e:
                        return {
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "error": {
                                "code": -32603,
                                "message": f"Tool execution error: {str(e)}"
                            }
                        }, None
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": message_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }, None
            
            # 处理ping请求
            elif method == "ping":
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {}
                }, None
            
            # 未知方法
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }, None
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }, None
    
    async def get_session_info(request: Request) -> JSONResponse:
        """获取会话信息端点
        
        返回当前活跃会话的信息。
        
        参数：
            request: HTTP请求对象
            
        返回：
            JSONResponse: 会话信息
        """
        return JSONResponse({
            "active_sessions": len(active_sessions),
            "supported_versions": SUPPORTED_PROTOCOL_VERSIONS,
            "default_version": DEFAULT_PROTOCOL_VERSION,
            "sessions": {
                session_id: {
                    "created_at": info["created_at"],
                    "last_activity": info["last_activity"],
                    "protocol_version": info.get("protocol_version", "unknown")
                }
                for session_id, info in active_sessions.items()
            }
        })
    
    # 向后兼容性支持：检测旧版本客户端
    async def handle_legacy_sse(request: Request) -> StreamingResponse:
        """处理旧版本HTTP+SSE传输的兼容性"""
        async def legacy_stream():
            # 发送endpoint事件以指示这是旧版本传输
            yield f"data: {{\"type\": \"endpoint\", \"uri\": \"/mcp\"}}

"
            
            # 保持连接
            while True:
                await asyncio.sleep(30)
                yield f"data: {{\"type\": \"heartbeat\"}}

"
        
        return StreamingResponse(
            legacy_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    
    return Starlette(
        debug=debug,
        routes=[
            Route("/mcp", endpoint=handle_mcp_request, methods=["GET", "POST", "DELETE"]),
            Route("/sessions", endpoint=get_session_info, methods=["GET"]),
            # 向后兼容性路由
            Route("/sse", endpoint=handle_legacy_sse, methods=["GET"]),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='运行MCP服务器')
    parser.add_argument('--host', default='127.0.0.1', help='绑定的主机地址（默认localhost以提高安全性）')
    parser.add_argument('--port', type=int, default=1234, help='监听的端口')
    parser.add_argument('--transport', choices=['sse', 'streamable'], default='streamable', 
                       help='传输协议类型: sse (传统SSE) 或 streamable (现代Streamable HTTP)')
    args = parser.parse_args()

    # 安全性提醒
    if args.host == '0.0.0.0':
        print("警告：绑定到0.0.0.0可能存在安全风险，建议使用127.0.0.1")
    
    print(f"启动Streamable HTTP MCP服务器，监听 {args.host}:{args.port}")
    print(f"支持的协议版本: {', '.join(SUPPORTED_PROTOCOL_VERSIONS)}")
    print(f"默认协议版本: {DEFAULT_PROTOCOL_VERSION}")
    
    starlette_app = create_streamable_http_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)