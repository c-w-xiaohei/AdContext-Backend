from fastmcp import FastMCP
from core.service import context_core

mcp = FastMCP("Demo 🚀")

@mcp.tool(description="当你需要查找和当前对话相关的背景知识或历史信息时，使用此工具。输入你想要查询的关键词或问题，它会从知识库中检索最相关的上下文片段，帮助你更准确地理解和回答用户的问题。")
def query(text: str) -> str:
    """
    检索与输入文本相关的上下文片段，帮助AI更好地理解和回答问题。
    """
    return context_core.query(text)

@mcp.tool(description="当对话中出现了需要长期记住的关键信息时，使用此工具将其存入知识库。例如，用户的偏好、重要的事实或对话的总结。这样，在未来的对话中，这些信息就可以通过“query”工具被检索到。")
def input(text: str) -> str:
    """
    将用户输入的文本作为新的上下文片段存储，便于后续检索和利用。
    """
    return context_core.input(text)
    
    


if __name__ == "__main__":
    mcp.run()