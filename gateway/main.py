from fastmcp import FastMCP  # 修正导入语句
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
from gateway.prompt import CUSTOM_INSTRUCTIONS  # 修改为绝对导入
from gateway.blockchain import request_blockchain_data

from storage.service import StorageService
from services.privacy.privacy_classifier import PrivacyClassifier
# websocket
import json
from starlette.applications import Starlette
from starlette.routing import Mount, WebSocketRoute
from starlette.endpoints import WebSocketEndpoint
from services.websocket import websocket_manager
import uvicorn


load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("AD-Context")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "trae_user"

# 更新项目自定义指令
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""**核心指令：**
这是你与用户交互的记忆接口。在任何与用户的互动中，当你获取到关于用户的新信息，或当你判断一段有意义的对话已经结束且有记录价值时，你**必须**主动调用此工具，将关键信息和上下文进行结构化存储。

**执行目标：**
调用此工具的目的是为了在未来的对话中提供连贯、个性化且深刻的体验。你记录的信息将被用于语义索引和检索，让你能随时回忆起用户的偏好和历史。

**记录维度指引：**
当你执行记录时，应评估并捕获以下维度的信息（当信息在对话中出现时）：

*   **身份与背景 (Personal Info):** 用户的基本信息，如姓名、职业、地理位置等。
*   **个人偏好 (Preferences):** 审美、品味和选择倾向，如喜欢的颜色、音乐风格、阅读主题等。
*   **行为模式 (Habits):** 用户的常规行为，如作息、工作习惯、沟通节奏等。
*   **认知与学习 (Cognition & Learning):** 用户的思维方式、知识领域、学习偏好和技能水平。
*   **核心记忆 (Core Memories):** 对用户意义重大的事件、达成的关键共识、重要的历史互动。
*   **未来意图 (Goals & Plans):** 用户的短期目标、长期规划或特定愿景。
*   以及其他的值得记录的信息。
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
        privacy_label = PrivacyClassifier().classify(text)
        metadata = Metadata(
            privacy_level=privacy_label.level,
            source="user_input"
        )
        
        result = await StorageService(websocket_manager).add(text, metadata,privacy_label.brief)
        return result
    except Exception as e:
        return f"Error adding memory: {str(e)}"


@mcp.tool(
    description="""**核心指令：**
在你与用户进行任何对话之前或之中，当你需要回忆用户的历史信息、偏好或过往共识以构建上下文时，你**必须**主动调用此工具进行查询。

**战略目标：**
你的首要目标是**主动**利用用户的历史记忆，让每一次对话都具有连续性和深度。通过检索过去的信息，你能够更好地理解用户的当前意图，提供高度个性化的回应，从而极大地提升用户的对话体验。这不仅仅是被动查找，更是**主动构建情境**的关键步骤。

**调用时机指引 (Invocation Triggers):**
在以下情况，你应该优先考虑调用此工具：

*   **对话启动时 (Conversation Grounding):** 在开启新话题前，快速检索相关背景，确保对话建立在已知共识之上。
*   **个性化需求 (Personalization):** 当用户请求建议、推荐或寻求个性化方案时，检索其相关偏好与习惯。
*   **信息确认与关联 (Contextual Linking):** 当用户提及一个可能与历史信息相关的关键词（如项目、人物、地点、观点）时，立即查询以建立联系。
*   **理解深层意图 (Deepening Understanding):** 当用户表达模糊或复杂的需求时，检索过往的沟通模式和目标，以更准确地把握其意图。

**操作要点与能力 (Operational Points & Capabilities):**
*   **以自然语言查询：** 直接用对话的方式进行提问。工具的语义理解能力会匹配最相关的记忆，你无需构造复杂的关键词。
*   **信赖语义匹配：** 工具能够理解上下文、同义词和相关概念。你可以放心进行模糊或宽泛的查询。
*   **利用相关性评分：** 返回结果会包含相关性分数，利用这个分数来判断检索到的记忆与当前对话的贴合程度。
*   **按需使用元数据：** 当需要更精确的查找时（例如特定时间段或主题），可利用元数据进行过滤。
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
        
        storage_service = StorageService(websocket_manager)
        results = storage_service.search(query_text, top_k=top_k)
        
        # <time>:search_complete - 搜索完成
        print(f"<time>:search_complete - 搜索完成，找到 {len(results)} 个结果")
        
        # 获取并更新区块链数据
        for result in results:
            if result.metadata and result.metadata.blockchain_data_id:
                print(f"<time>:blockchain_fetch_start - 开始为ID {result.metadata.blockchain_data_id} 获取区块链数据")
                try:
                    blockchain_context = await request_blockchain_data(result.metadata.blockchain_data_id)
                    if blockchain_context:
                        result.context = blockchain_context
                    print(f"<time>:blockchain_fetch_complete - ID {result.metadata.blockchain_data_id} 的区块链数据获取完成")
                except Exception as e:
                    print(f"<time>:blockchain_fetch_error - 获取ID {result.metadata.blockchain_data_id} 的区块链数据时出错: {e}")
        
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
    
class ContextWSEndpoint(WebSocketEndpoint):
    async def on_connect(self, websocket):
        await websocket_manager.connect(websocket)

    async def on_receive(self, websocket, data):
        # 监听来自前端的响应
        response = json.loads(data)
        request_id = response.get("requestId")
        if request_id:
            # 解析等待中的请求
            websocket_manager.resolve_request(request_id, response.get("payload"))

    async def on_disconnect(self, websocket, close_code):
        websocket_manager.disconnect()

# 添加健康检查和根路径重定向端点
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """健康检查端点
    
    返回:
        PlainTextResponse: 服务器状态信息
    """
    from starlette.responses import PlainTextResponse
    return PlainTextResponse("OK")

@mcp.custom_route("/", methods=["GET"])
async def root_redirect(request):
    """根路径重定向到MCP端点信息
    
    返回:
        JSONResponse: MCP服务器信息
    """
    from starlette.responses import JSONResponse
    return JSONResponse({
        "name": "AD-Context MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp/",
        "health_endpoint": "/health",
        "status": "running"
    })

def create_starlette_app() -> Starlette:
    
    # 获取 FastMCP 的 ASGI 应用，并将其路径设置为根 ("/")
    # 这样 FastMCP 应用本身就不关心它的挂载点了
    mcp_asgi_app = mcp.http_app(transport="streamable-http", path="/")

    return Starlette(routes=[
            # 添加WebSocket路由
            WebSocketRoute("/ws", endpoint=ContextWSEndpoint),
            # 将 FastMCP 应用挂载到 /mcp 路径
            Mount("/mcp", app=mcp_asgi_app),
        ],
        # 关键修复：将 mcp 应用的生命周期管理传递给主应用
        lifespan=mcp_asgi_app.lifespan
    )
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='运行MCP和WebSocket服务器')
    parser.add_argument('--host', default='0.0.0.0', help='绑定的主机地址')  # 改为默认本地地址
    parser.add_argument('--port', type=int, default=8080, help='监听的端口')
    parser.add_argument('--log-level', default='info', help='日志级别')
    args = parser.parse_args()
    
    # 不再直接运行mcp服务器，而是将其集成到Starlette应用中
    # mcp.run(
    #     transport="streamable-http",  # 或者使用 "http" 作为别名
    #     host=args.host,
    #     port=args.port,
    #     log_level=args.log_level
    # )
    
    starlette_app = create_starlette_app()
    uvicorn.run(starlette_app, host=args.host, port=args.port, log_level=args.log_level)
