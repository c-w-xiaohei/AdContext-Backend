#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastMCP 服务器测试脚本

测试运行在 http://127.0.0.1:1234/mcp/ 的 AD-Context MCP 服务器
包含初始化、添加记忆和搜索记忆功能的完整测试
"""

import asyncio
import json
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPServerTester:
    """MCP 服务器测试类"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234/mcp/"):
        """初始化测试器
        
        参数:
            base_url: MCP 服务器的基础 URL
        """
        self.base_url = base_url
        self.transport = StreamableHttpTransport(url=base_url)
        self.client = Client(transport=self.transport)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
    
    async def test_list_tools(self) -> bool:
        """测试获取工具列表
        
        返回:
            bool: 获取是否成功
        """
        print("🔄 测试获取工具列表...")
        
        try:
            tools = await self.client.list_tools()
            print(f"✅ 获取到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description[:80]}...")
            return True
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return False
    
    async def test_add_memory(self, memory_text: str) -> bool:
        """测试添加记忆功能
        
        参数:
            memory_text: 要添加的记忆内容
            
        返回:
            bool: 添加是否成功
        """
        print(f"🔄 测试添加记忆: {memory_text[:50]}...")
        
        try:
            result = await self.client.call_tool(
                "add_memory",
                arguments={"text": memory_text}
            )
            print(f"✅ 记忆添加成功: {result.content[0].text if result.content else 'No content'}")
            return True
        except Exception as e:
            print(f"❌ 添加记忆失败: {e}")
            return False
    
    async def test_search_memory(self, query: str, top_k: int = 3) -> bool:
        """测试搜索记忆功能
        
        参数:
            query: 搜索查询
            top_k: 返回结果数量
            
        返回:
            bool: 搜索是否成功
        """
        print(f"🔄 测试搜索记忆: {query}")
        
        try:
            result = await self.client.call_tool(
                "search_memory",
                arguments={"query_text": query, "top_k": top_k}
            )
            
            content = result.content[0].text if result.content else ''
            
            try:
                # 尝试解析 JSON 响应
                search_results = json.loads(content)
                print(f"✅ 搜索成功，找到 {search_results.get('total_found', 0)} 个结果")
                
                if search_results.get('has_filtered_content'):
                    print(f"   过滤后摘要: {search_results.get('filtered_summary', '')[:100]}...")
                
                for i, result in enumerate(search_results.get('raw_results', [])[:2]):
                    print(f"   结果 {i+1}: {result.get('content', '')[:80]}... (评分: {result.get('score', 0):.3f})")
                
                return True
            except json.JSONDecodeError:
                print(f"✅ 搜索完成: {content[:200]}...")
                return True
                
        except Exception as e:
            print(f"❌ 搜索记忆失败: {e}")
            return False
    
    async def run_full_test(self) -> None:
        """运行完整的测试套件"""
        print("🚀 开始 FastMCP 服务器完整测试")
        print(f"📍 服务器地址: {self.base_url}")
        print("=" * 60)
        
        try:
            async with self.client:
                print("✅ 连接成功")
                
                # 测试工具列表
                await self.test_list_tools()
                await asyncio.sleep(0.5)
                
                # 测试添加记忆
                test_memories = [
                    "我叫张三，是一名软件工程师，喜欢使用 Python 和 JavaScript 开发应用。我对人工智能和机器学习特别感兴趣。",
                    "我的工作习惯是早上9点开始工作，喜欢在安静的环境中编程。我偏好使用 VS Code 作为开发工具。",
                    "我最近在学习 FastMCP 框架，希望能够构建更好的 AI 助手应用。我的目标是成为全栈 AI 开发者。"
                ]
                
                for memory in test_memories:
                    if await self.test_add_memory(memory):
                        await asyncio.sleep(1)  # 给服务器一些时间处理
                    else:
                        print("❌ 添加记忆失败，跳过后续测试")
                        break
                
                await asyncio.sleep(1)
                
                # 测试搜索记忆
                test_queries = [
                    "张三的职业是什么？",
                    "他喜欢使用什么编程语言？",
                    "他的工作习惯如何？",
                    "他在学习什么技术？"
                ]
                
                for query in test_queries:
                    await self.test_search_memory(query)
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return
        
        print("=" * 60)
        print("🎉 测试完成！")
    
async def main():
    """主函数"""
    print("FastMCP 服务器测试工具")
    print("确保服务器正在运行在 http://127.0.0.1:1234/mcp/")
    print()
    
    # 创建测试器并运行测试
    tester = MCPServerTester()
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())