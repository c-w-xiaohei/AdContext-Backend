#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastMCP 服务器测试脚本

测试运行在 http://127.0.0.1:8080/mcp/ 的 AD-Context MCP 服务器
包含初始化、添加记忆和搜索记忆功能的完整测试，以及隐私数据监测与区块链存储测试
"""

import asyncio
import json
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport
from schemas.privacy import PrivacyLevel
from schemas.common import Metadata


class MCPServerTester:
    """MCP 服务器测试类"""
    
    def __init__(self, base_url: str = "https://advx-1.zeabur.app/mcp/"):
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
                    if 'metadata' in result and 'privacy_level' in result['metadata']:
                        print(f"   隐私级别: {result['metadata']['privacy_level']}")
                    if 'blockchain_data_id' in result.get('metadata', {}):
                        print(f"   区块链数据ID: {result['metadata']['blockchain_data_id']}")
                
                return True
            except json.JSONDecodeError:
                print(f"✅ 搜索完成: {content[:200]}...")
                return True
                
        except Exception as e:
            print(f"❌ 搜索记忆失败: {e}")
            return False
            
    async def test_privacy_classification(self, text: str) -> bool:
        """测试隐私分类功能
        
        参数:
            text: 要分类的文本
            
        返回:
            bool: 分类是否成功
        """
        print(f"🔄 测试隐私分类: {text[:50]}...")
        
        try:
            # 这里假设有一个隐私分类的工具，如果没有，需要直接调用PrivacyClassifier
            # 这里使用add_memory的返回值来推断隐私级别
            result = await self.client.call_tool(
                "add_memory",
                arguments={"text": text}
            )
            
            print(f"✅ 隐私分类测试完成: {result.content[0].text if result.content else 'No content'}")
            return True
        except Exception as e:
            print(f"❌ 隐私分类测试失败: {e}")
            return False
            
    async def test_blockchain_storage(self, sensitive_text: str) -> bool:
        """测试区块链存储功能
        
        参数:
            sensitive_text: 敏感信息文本
            
        返回:
            bool: 存储是否成功
        """
        print(f"🔄 测试区块链存储: {sensitive_text[:50]}...")
        
        try:
            # 添加一条明显包含敏感信息的记忆
            result = await self.client.call_tool(
                "add_memory",
                arguments={"text": sensitive_text}
            )
            
            print(f"✅ 区块链存储测试添加完成: {result.content[0].text if result.content else 'No content'}")
            
            # 搜索这条记忆，检查是否被存储在区块链上
            search_result = await self.test_search_memory(sensitive_text[:30])
            
            return search_result
        except Exception as e:
            print(f"❌ 区块链存储测试失败: {e}")
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
                
                # 测试隐私数据监测与存储
                print("\n" + "=" * 60)
                print("🔒 开始隐私数据监测与存储测试")
                print("=" * 60)
                
                # 测试不同隐私级别的数据
                privacy_test_data = [
                    # 公开级别 (LEVEL_1_PUBLIC)
                    "我喜欢在周末去公园散步，这是一个公开的爱好。",
                    
                    # 内部级别 (LEVEL_2_INTERNAL)
                    "我们团队正在开发一个新的AI助手项目，项目代号为'星辰'。",
                    
                    # 机密级别 (LEVEL_3_CONFIDENTIAL)
                    "我的邮箱密码是abc123456，请不要告诉任何人。",
                    
                    # 限制级别 (LEVEL_4_RESTRICTED)
                    "我的银行卡号是6225880137751234，密码是123456。",
                    
                    # 绝密级别 (LEVEL_5_TOP_SECRET)
                    "公司服务器的root密码是R00t@2023!，数据库连接字符串是'postgres://admin:secret@db.example.com:5432/maindb'。"
                ]
                
                for i, test_data in enumerate(privacy_test_data):
                    print(f"\n测试数据 {i+1}：预期隐私级别 {i+1}")
                    await self.test_privacy_classification(test_data)
                    await asyncio.sleep(1)
                
                # 测试区块链存储
                print("\n" + "=" * 60)
                print("⛓️ 开始区块链存储测试")
                print("=" * 60)
                
                blockchain_test_data = [
                    "这是一条包含我的身份证号码330102199001011234的敏感信息，应该被存储到区块链上。",
                    "这是另一条包含银行信息的数据：我的招商银行账号是6225887654321098，密码是888666。"
                ]
                
                for test_data in blockchain_test_data:
                    await self.test_blockchain_storage(test_data)
                    await asyncio.sleep(1)
                    
                # 测试区块链数据检索
                print("\n" + "=" * 60)
                print("🔍 测试区块链数据检索")
                print("=" * 60)
                
                blockchain_queries = [
                    "我的身份证号码是什么？",
                    "我的银行账号信息"
                ]
                
                for query in blockchain_queries:
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
    print("确保服务器正在运行在 http://localhost:8080/mcp/")
    print()
    
    # 创建测试器并运行测试
    tester = MCPServerTester()
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())