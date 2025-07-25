import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()
print('环境变量已加载')

api_key = os.getenv('MEM0_API_KEY')
print(f'MEM0_API_KEY: {api_key[:10] if api_key else "未设置"}...')

# 导入模块
from schemas.privacy import PrivacyLevel  
from schemas.common import Metadata, RetriveResult, ListResult
from storage.service import StorageService

def test_storage_service():
    """测试存储服务功能"""
    service = StorageService()
    print('StorageService实例已创建，可以开始测试')
    
    # 创建正确的元数据对象
    metadata = Metadata(
        privacy_level=PrivacyLevel.LEVEL_1_PUBLIC,  # 修正枚举值
        source="user"
    )
    
    # # 添加测试上下文
    # result1 = service.add("用户喜欢喝咖啡，特别是拿铁", metadata=metadata)
    # print(f"添加结果1: {result1}")

    # result2 = service.add("项目使用Python和FastAPI框架开发", metadata=metadata)
    # print(f"添加结果2: {result2}")

    # result3 = service.add("用户偏好深色主题界面", metadata=metadata)
    # print(f"添加结果3: {result3}")

    # 测试搜索功能
    print("\n=== 搜索测试 ===")
    search_results = service.search("咖啡")
    print(f"搜索'咖啡'的结果: {len(search_results)} 条")
    for i, result in enumerate(search_results):
        print(f"  {i+1}. {result}")

    # 测试列表功能
    print("\n=== 列表测试 ===")
    all_memories = service.list(limit=10)
    print(f"所有记忆: {len(all_memories)} 条")
    for i, memory in enumerate(all_memories):
        print(f"  {i+1}. {memory}")

    #测试删除功能
    print("\n测试删除功能")
    delete_result = service.delete(all_memories[0]['id'])
    print(f"删除结果: {delete_result}")


if __name__ == "__main__":
    test_storage_service()