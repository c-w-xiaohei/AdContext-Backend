
FastMCP Cloud is here! Join the beta.
FastMCP 云服务已上线！加入测试版。

FastMCP home pageFastMCP

Search the docs...  搜索文档...
⌘K
jlowin/fastmcp
15,255

Documentation
  文档
SDK Reference
  SDK 参考
Documentation
  文档
What's New
  新功能
Community
  社区
Get Started  开始使用
Welcome!  欢迎！
Installation  安装
Quickstart  快速入门
Servers  服务器
Essentials  基础
Overview  概述
Running the Server  运行服务器
Core Components  核心组件
Advanced Features  高级功能
Authentication  认证
Clients  客户端
Essentials  基础
Core Operations  核心操作
Advanced Features  高级功能
Authentication
Integrations
Anthropic API
ChatGPT
NEW
Claude Code
NEW
Claude Desktop
Cursor
NEW
Eunomia Auth
NEW
FastAPI
Gemini SDK
MCP JSON
NEW
OpenAI API
NEW
OpenAPI
Permit.io Permissions
NEW
Starlette / ASGI
Patterns
Tool Transformation
Decorating Methods
HTTP Requests
Testing
CLI
Contrib Modules
Tutorials
What is MCP?
Creating an MCP Server
Connect LLMs to REST APIs
Essentials  基础
Running Your FastMCP Server
运行您的 FastMCP 服务器
Learn how to run and deploy your FastMCP server using various transport protocols like STDIO, Streamable HTTP, and SSE.
学习如何使用 STDIO、Streamable HTTP 和 SSE 等多种传输协议来运行和部署你的 FastMCP 服务器。

FastMCP servers can be run in different ways depending on your application’s needs, from local command-line tools to persistent web services. This guide covers the primary methods for running your server, focusing on the available transport protocols: STDIO, Streamable HTTP, and SSE.
FastMCP 服务器可以根据你的应用需求以不同的方式运行，从本地命令行工具到持久的 Web 服务。本指南涵盖了运行服务器的主要方法，重点介绍了可用的传输协议：STDIO、Streamable HTTP 和 SSE。
​
The run() Method   run() 方法
FastMCP servers can be run directly from Python by calling the run() method on a FastMCP instance.
FastMCP 服务器可以直接通过在 run() 实例上调用 FastMCP 方法来运行。
For maximum compatibility, it’s best practice to place the run() call within an if __name__ == "__main__": block. This ensures the server starts only when the script is executed directly, not when imported as a module.
为了最大兼容性，最佳实践是将 run() 调用放在 if __name__ == "__main__": 块内。这确保服务器仅在脚本直接执行时启动，而不是作为模块导入时。
my_server.py

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
You can now run this MCP server by executing python my_server.py.
现在可以通过执行 python my_server.py 来运行这个 MCP 服务器。
MCP servers can be run with a variety of different transport options, depending on your application’s requirements. The run() method can take a transport argument and other transport-specific keyword arguments to configure how the server operates.
MCP 服务器可以根据应用程序的需求使用多种不同的传输选项来运行。 run() 方法可以接受 transport 参数和其他传输特定的关键字参数来配置服务器的运行方式。
​
The FastMCP CLI  FastMCP 命令行界面
FastMCP also provides a command-line interface for running servers without modifying the source code. After installing FastMCP, you can run your server directly from the command line:
FastMCP 还提供了一个命令行界面，用于在不修改源代码的情况下运行服务器。安装 FastMCP 后，您可以直接从命令行运行您的服务器：

Copy  复制
fastmcp run server.py
Important: When using fastmcp run, it ignores the if __name__ == "__main__" block entirely. Instead, it looks for a FastMCP object named mcp, server, or app and calls its run() method directly with the transport options you specify.
重要提示：在使用 fastmcp run 时，它会完全忽略 if __name__ == "__main__" 块。相反，它会查找名为 mcp 、 server 或 app 的 FastMCP 对象，并直接使用您指定的传输选项调用其 run() 方法。
This means you can use fastmcp run to override the transport specified in your code, which is particularly useful for testing or changing deployment methods without modifying the code.
这意味着您可以使用 fastmcp run 来覆盖代码中指定的传输方式，这对于测试或更改部署方法而不修改代码特别有用。
You can specify transport options and other configuration:
您可以指定传输选项和其他配置：

Copy  复制
fastmcp run server.py --transport sse --port 9000
​
Dependency Management with CLI
使用 CLI 进行依赖管理
When using the FastMCP CLI, you can pass additional options to configure how uv runs your server:
在使用 FastMCP CLI 时，您可以传递额外的选项来配置 uv 如何运行您的服务器：

Copy  复制
# Run with a specific Python version
fastmcp run server.py --python 3.11

# Run with additional packages
fastmcp run server.py --with pandas --with numpy

# Run with dependencies from a requirements file
fastmcp run server.py --with-requirements requirements.txt

# Combine multiple options
fastmcp run server.py --python 3.10 --with httpx --transport http

# Run within a specific project directory
fastmcp run server.py --project /path/to/project
When using --python, --with, --project, or --with-requirements, the server runs via uv run subprocess instead of using your local environment. The uv command will manage dependencies based on your project configuration.
在使用 --python 、 --with 、 --project 或 --with-requirements 时，服务器将通过 uv run 子进程运行，而不是使用您的本地环境。 uv 命令将根据您的项目配置管理依赖项。
The --python option is particularly useful when you need to run a server with a specific Python version that differs from your system’s default. This addresses common compatibility issues where servers require a particular Python version to function correctly.
--python 选项在你需要运行一个与系统默认版本不同的特定 Python 版本的服务器时特别有用。这解决了常见的兼容性问题，即服务器需要特定的 Python 版本才能正常运行。
For development and testing, you can use the dev command to run your server with the MCP Inspector:
在开发和测试中，你可以使用 dev 命令通过 MCP 检查器运行你的服务器：

Copy  复制
fastmcp dev server.py
The dev command also supports the same dependency management options:
dev 命令也支持相同的依赖管理选项：

Copy  复制
# Dev server with specific Python version and packages
fastmcp dev server.py --python 3.11 --with pandas
See the CLI documentation for detailed information about all available commands and options.
请参阅 CLI 文档，以获取有关所有可用命令和选项的详细信息。
​
Passing Arguments to Servers
将参数传递给服务器
When servers accept command line arguments (using argparse, click, or other libraries), you can pass them after --:
当服务器接受命令行参数（使用 argparse、click 或其他库）时，您可以在 -- 之后传递它们：

Copy  复制
fastmcp run config_server.py -- --config config.json
fastmcp run database_server.py -- --database-path /tmp/db.sqlite --debug
This is useful for servers that need configuration files, database paths, API keys, or other runtime options.
这对于需要配置文件、数据库路径、API 密钥或其他运行时选项的服务器很有用。
​
Transport Options  传输选项
Below is a comparison of available transport options to help you choose the right one for your needs:
以下是可用传输选项的比较，以帮助您为您的需求选择正确的选项：
Transport  传输	Use Cases  用例	Recommendation  建议
STDIO	Local tools, command-line scripts, and integrations with clients like Claude Desktop
本地工具、命令行脚本以及与类似 Claude Desktop 的客户端集成	Best for local tools and when clients manage server processes
适用于本地工具和客户端管理服务器进程的情况
Streamable HTTP  可流式传输的 HTTP	Web-based deployments, microservices, exposing MCP over a network
基于网络的部署、微服务、通过网络暴露 MCP	Recommended choice for web-based deployments
基于 Web 的部署的推荐选择
SSE	Existing web-based deployments that rely on SSE
依赖 SSE 的现有基于 Web 的部署	Deprecated - prefer Streamable HTTP for new projects
已弃用 - 新项目请优先使用 Streamable HTTP
​
STDIO
The STDIO transport is the default and most widely compatible option for local MCP server execution. It is ideal for local tools, command-line integrations, and clients like Claude Desktop. However, it has the disadvantage of having to run the MCP code locally, which can introduce security concerns with third-party servers.
STDIO 传输是本地 MCP 服务器执行时的默认且最广泛兼容的选项。它非常适合本地工具、命令行集成以及像 Claude 桌面这样的客户端。然而，它的缺点是需要本地运行 MCP 代码，这可能会引入与第三方服务器相关的安全问题。
STDIO is the default transport, so you don’t need to specify it when calling run(). However, you can specify it explicitly to make your intent clear:
stdio 是默认的传输方式，所以在调用 run() 时无需指定。不过，你也可以明确指定它，以便清楚地表达你的意图：

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP()

if __name__ == "__main__":
    mcp.run(transport="stdio")
When using Stdio transport, you will typically not run the server yourself as a separate process. Rather, your clients will spin up a new server process for each session. As such, no additional configuration is required.
在使用 Stdio 传输时，通常不会将服务器作为单独进程自行运行。相反，您的客户端将为每个会话启动一个新的服务器进程。因此，无需进行额外配置。
​
Streamable HTTP  可流式传输的 HTTP
New in version: 2.3.0
Streamable HTTP is a modern, efficient transport for exposing your MCP server via HTTP. It is the recommended transport for web-based deployments.
Streamable HTTP 是一种现代、高效的传输方式，用于通过 HTTP 暴露您的 MCP 服务器。它是基于 Web 部署的推荐传输方式。
To run a server using Streamable HTTP, you can use the run() method with the transport argument set to "http". This will start a Uvicorn server on the default host (127.0.0.1), port (8000), and path (/mcp/).
要使用 Streamable HTTP 运行服务器，您可以使用 run() 方法，并将 transport 参数设置为 "http" 。这将启动一个 Uvicorn 服务器，在默认主机（ 127.0.0.1 ）、端口（ 8000 ）和路径（ /mcp/ ）上运行。

server.py

client.py

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP()

if __name__ == "__main__":
    mcp.run(transport="http")
For backward compatibility, wherever "http" is accepted as a transport name, you can also pass "streamable-http" as a fully supported alias. This is particularly useful when upgrading from FastMCP 1.x in the official Python SDK and FastMCP <= 2.9, where "streamable-http" was the standard name.
为了向后兼容，在所有接受 "http" 作为传输名称的地方，你也可以传递 "streamable-http" 作为完全支持的别名。这在从官方 Python SDK 和 FastMCP <= 2.9 升级到 FastMCP 1.x 时特别有用，当时 "streamable-http" 是标准名称。
To customize the host, port, path, or log level, provide appropriate keyword arguments to the run() method.
要自定义主机、端口、路径或日志级别，请向 run() 方法提供适当的命名关键字参数。

server.py

client.py

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP()

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=4200,
        path="/my-custom-path",
        log_level="debug",
    )
​
SSE
The SSE transport is deprecated and may be removed in a future version. New applications should use Streamable HTTP transport instead.
SSE 传输方式已弃用，未来版本中可能会被移除。新应用应使用流式 HTTP 传输方式替代。
Server-Sent Events (SSE) is an HTTP-based protocol for server-to-client streaming. While FastMCP still supports SSE, it is deprecated and Streamable HTTP is preferred for new projects.
服务器端事件（SSE）是一种基于 HTTP 的服务器到客户端流协议。虽然 FastMCP 仍然支持 SSE，但它已过时，新项目应优先使用可流式传输 HTTP。
To run a server using SSE, you can use the run() method with the transport argument set to "sse". This will start a Uvicorn server on the default host (127.0.0.1), port (8000), and with default SSE path (/sse/) and message path (/messages/).
要使用 SSE 运行服务器，可以使用 run() 方法，并将 transport 参数设置为 "sse" 。这将启动一个 Uvicorn 服务器，在默认主机（ 127.0.0.1 ）、端口（ 8000 ）以及默认 SSE 路径（ /sse/ ）和消息路径（ /messages/ ）上运行。

server.py

client.py

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP()

if __name__ == "__main__":
    mcp.run(transport="sse")
Notice that the client in the above example uses an explicit SSETransport to connect to the server. FastMCP will attempt to infer the appropriate transport from the provided configuration, but HTTP URLs are assumed to be Streamable HTTP (as of FastMCP 2.3.0).
请注意，上述示例中的客户端使用显式的 SSETransport 连接到服务器。FastMCP 将尝试从提供的配置中推断适当的传输方式，但自 FastMCP 2.3.0 起，HTTP URL 假定为可流式传输的 HTTP。
To customize the host, port, or log level, provide appropriate keyword arguments to the run() method. You can also adjust the SSE path (which clients should connect to) and the message POST endpoint (which clients use to send subsequent messages).
要自定义主机、端口或日志级别，请向 run() 方法提供适当的命名参数。您还可以调整 SSE 路径（客户端应连接的路径）和消息 POST 端点（客户端用于发送后续消息的端点）。

server.py
  

client.py
  

Copy  复制
from fastmcp import FastMCP

mcp = FastMCP()

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=4200,
        log_level="debug",
        path="/my-custom-sse-path",
    )
​
Async Usage  
FastMCP provides both synchronous and asynchronous APIs for running your server. The run() method seen in previous examples is a synchronous method that internally uses anyio.run() to run the asynchronous server. For applications that are already running in an async context, FastMCP provides the run_async() method.  

Copy  复制
from fastmcp import FastMCP
import asyncio

mcp = FastMCP(name="MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

async def main():
    # Use run_async() in async contexts
    await mcp.run_async(transport="http")

if __name__ == "__main__":
    asyncio.run(main())
The run() method cannot be called from inside an async function because it already creates its own async event loop internally. If you attempt to call run() from inside an async function, you’ll get an error about the event loop already running.  
Always use run_async() inside async functions and run() in synchronous contexts.  
Both run() and run_async() accept the same transport arguments, so all the examples above apply to both methods.  
​
Custom Routes  
You can also add custom web routes to your FastMCP server, which will be exposed alongside the MCP endpoint. To do so, use the @custom_route decorator. Note that this is less flexible than using a full ASGI framework, but can be useful for adding simple endpoints like health checks to your standalone server.  

Copy  复制
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

mcp = FastMCP("MyServer")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    mcp.run()
Overview  概述
Tools  工具
bluesky
github
x
Powered by Mintlify  由 Mintlify 提供技术支持

