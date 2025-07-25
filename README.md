# AdContext-Backend
## storage usage
### 测试添加功能
```
from dotenv import load_dotenv
import os
load_dotenv()
print('环境变量已加载')
api_key = os.getenv('MEM0_API_KEY')
print(f'MEM0_API_KEY: {api_key[:10] if api_key else "未设置"}...')
from storage.service import StorageService
service = StorageService()
print('StorageService实例已创建，可以开始测试')
```

```
import asyncio

# 添加第一个测试上下文
result1 = asyncio.run(service.add("用户喜欢喝咖啡，特别是拿铁"))
print(f"添加结果1: {result1}")

# 添加第二个测试上下文
result2 = asyncio.run(service.add("项目使用Python和FastAPI框架开发"))
print(f"添加结果2: {result2}")

# 添加第三个测试上下文
result3 = asyncio.run(service.add("用户偏好深色主题界面"))
print(f"添加结果3: {result3}")
```
```
# 搜索咖啡相关内容
print("\n=== 搜索'咖啡'相关内容 ===")
coffee_results = service.search("咖啡", top_k=3)
print(f"找到 {len(coffee_results)} 个结果:")
for i, result in enumerate(coffee_results, 1):
    print(f"{i}. 内容: {result.context}")
    print(f"   分数: {result.score:.3f}")
    print(f"   隐私级别: {result.metadata.privacy_level}")
    print(f"   来源: {result.metadata.source}")
    print()

# 搜索Python相关内容
print("\n=== 搜索'Python'相关内容 ===")
python_results = service.search("Python", top_k=3)
print(f"找到 {len(python_results)} 个结果:")
for i, result in enumerate(python_results, 1):
    print(f"{i}. 内容: {result.context}")
    print(f"   分数: {result.score:.3f}")
    print()
```

```
# 列出所有记忆
print("\n=== 列出所有记忆 ===")
all_memories = service.list(limit=10)
print(f"总共有 {len(all_memories)} 条记忆:")
for i, memory in enumerate(all_memories, 1):
    print(f"{i}. {memory.context}")
    print(f"   隐私级别: {memory.metadata.privacy_level}")
    print(f"   来源: {memory.metadata.source}")
    print()
```