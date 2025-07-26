#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mem0 API 连接测试脚本
用于验证 Mem0 API 密钥是否有效以及服务是否可用
"""

import os
from mem0 import MemoryClient
import asyncio

def test_mem0_connection():
    """测试 Mem0 API 连接
    
    返回:
        bool: 连接是否成功
    """
    try:
        # 从环境变量获取 API 密钥
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            print("❌ 未找到 MEM0_API_KEY 环境变量")
            return False
            
        print(f"🔑 使用 API 密钥: {api_key[:10]}...{api_key[-4:]}")
        
        # 初始化 Mem0 客户端
        client = MemoryClient()
        print("✅ Mem0 客户端初始化成功")
        
        # 测试添加记忆
        print("🔄 测试添加记忆...")
        test_message = [{"role": "user", "content": "这是一个测试记忆，用于验证 API 连接"}]
        
        result = client.add(
            test_message,
            user_id="test_user",
            output_format="v1.1"
        )
        
        print(f"✅ 记忆添加成功: {result}")
        
        # 测试搜索记忆
        print("🔄 测试搜索记忆...")
        search_results = client.search(
            "测试记忆",
            user_id="test_user",
            version="v1",
            top_k=1
        )
        
        print(f"✅ 记忆搜索成功: 找到 {len(search_results) if search_results else 0} 个结果")
        
        return True
        
    except Exception as e:
        print(f"❌ Mem0 API 连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试 Mem0 API 连接")
    print("=" * 50)
    
    success = test_mem0_connection()
    
    print("=" * 50)
    if success:
        print("🎉 Mem0 API 连接测试通过！")
    else:
        print("💥 Mem0 API 连接测试失败！")
        print("\n可能的解决方案:")
        print("1. 检查 MEM0_API_KEY 是否正确")
        print("2. 检查网络连接")
        print("3. 检查 Mem0 服务状态")
        print("4. 尝试重新生成 API 密钥")

if __name__ == "__main__":
    main()