"""
FilterService使用示例

展示如何使用上下文筛选和整理功能
"""

from .filter_service import FilterService
from .models import FilteredResult
import time


def example_basic_usage():
    """基础使用示例"""
    print("🔍 FilterService基础使用示例")
    print("=" * 50)
    
    # 初始化FilterService
    filter_service = FilterService()
    
    # 模拟用户问题
    user_question = "张三的工作内容是什么？"
    
    # 模拟候选上下文（来自存储层的检索结果）
    candidate_contexts = [
        "张三是公司的产品经理，负责新产品的规划和设计。",
        "李四在技术部门工作，主要做后端开发。",
        "张三昨天参加了产品评审会议，讨论了新功能的实现方案。",
        "今天天气很好，适合出门。",
        "张三的邮箱是zhang.san@company.com，他经常回复邮件很及时。",
        "公司食堂今天的菜单有红烧肉和青菜。",
        "张三负责的产品在市场上表现很好，用户反馈积极。"
    ]
    
    print(f"📝 用户问题: {user_question}")
    print(f"📊 候选上下文数量: {len(candidate_contexts)}")
    print("\n原始候选上下文:")
    for i, context in enumerate(candidate_contexts, 1):
        print(f"  {i}. {context}")
    
    print("\n⏳ 正在进行上下文筛选和整理...")
    
    # 执行筛选
    result = filter_service.filter_contexts(user_question, candidate_contexts)
    
    # 显示结果
    print(f"\n✅ 筛选完成！")
    print(f"📄 整理后的上下文:")
    print(f"「{result.filtered_contexts}」")
    
    # 显示统计信息
    stats = filter_service.get_statistics(result)
    print(f"\n📈 筛选统计:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")


def example_empty_contexts():
    """空上下文处理示例"""
    print("\n🔍 空上下文处理示例")
    print("=" * 50)
    
    filter_service = FilterService()
    user_question = "什么是人工智能？"
    candidate_contexts = []
    
    print(f"📝 用户问题: {user_question}")
    print(f"📊 候选上下文数量: {len(candidate_contexts)}")
    
    result = filter_service.filter_contexts(user_question, candidate_contexts)
    
    print(f"✅ 处理结果:")
    print(f"  • 筛选后上下文: '{result.filtered_contexts}'")
    print(f"  • 处理耗时: {result.processing_time:.3f}秒")


def example_low_relevance_contexts():
    """低相关性上下文筛选示例"""
    print("\n🔍 低相关性上下文筛选示例")
    print("=" * 50)
    
    filter_service = FilterService()
    user_question = "如何使用Python进行数据分析？"
    
    # 包含一些不相关的上下文
    candidate_contexts = [
        "Python是一种编程语言，广泛用于数据分析。",
        "今天的天气预报显示会下雨。",
        "pandas和numpy是Python数据分析的重要库。",
        "我昨天吃了一顿很好的晚餐。",
        "使用matplotlib可以进行数据可视化。",
        "汽车需要定期保养以确保安全。",
        "Jupyter Notebook是数据分析的常用工具。"
    ]
    
    print(f"📝 用户问题: {user_question}")
    print(f"📊 候选上下文数量: {len(candidate_contexts)}")
    
    result = filter_service.filter_contexts(user_question, candidate_contexts)
    
    print(f"\n✅ 筛选结果:")
    print(f"📄 整理后的上下文:")
    print(f"「{result.filtered_contexts}」")
    
    stats = filter_service.get_statistics(result)
    print(f"\n📈 筛选效果:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")


def example_custom_threshold():
    """自定义相关性阈值示例"""
    print("\n🔍 自定义相关性阈值示例")
    print("=" * 50)
    
    # 使用更严格的阈值
    filter_service = FilterService(relevance_threshold=0.7)
    user_question = "张三的联系方式是什么？"
    
    candidate_contexts = [
        "张三是产品经理。",  # 低相关性
        "张三的邮箱是zhang.san@company.com。",  # 高相关性
        "张三的手机号是13812345678。",  # 高相关性
        "张三昨天开会了。",  # 低相关性
        "张三的办公室在3楼。"  # 中等相关性
    ]
    
    print(f"📝 用户问题: {user_question}")
    print(f"🎯 相关性阈值: {filter_service.relevance_threshold}")
    print(f"📊 候选上下文数量: {len(candidate_contexts)}")
    
    result = filter_service.filter_contexts(user_question, candidate_contexts)
    
    print(f"\n✅ 高阈值筛选结果:")
    print(f"📄 整理后的上下文:")
    print(f"「{result.filtered_contexts}」")
    
    stats = filter_service.get_statistics(result)
    print(f"\n📈 筛选统计:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")


def example_performance_test():
    """性能测试示例"""
    print("\n🔍 性能测试示例")
    print("=" * 50)
    
    filter_service = FilterService()
    user_question = "公司的发展历程是怎样的？"
    
    # 生成大量上下文进行性能测试
    candidate_contexts = [
        "公司成立于2020年，专注于AI技术研发。",
        "2021年公司获得了第一轮融资。",
        "2022年公司推出了第一款产品。",
        "今天吃什么好呢？",
        "2023年公司员工规模扩大到100人。",
        "明天的会议改到下午了。",
        "公司在2024年开始国际化布局。",
        "这首歌很好听。",
        "公司的核心价值观是创新、合作、诚信。",
        "周末打算去哪里玩？",
        "公司总部位于北京海淀区。",
        "天气预报说明天会下雪。",
        "公司的技术团队非常优秀。",
        "我需要买一些日用品。",
        "公司与多家知名企业建立了合作关系。"
    ]
    
    print(f"📝 用户问题: {user_question}")
    print(f"📊 候选上下文数量: {len(candidate_contexts)}")
    
    # 测试多次以获得平均性能
    total_time = 0
    test_runs = 3
    
    print(f"\n⏱️ 进行{test_runs}次测试...")
    
    for i in range(test_runs):
        start_time = time.time()
        result = filter_service.filter_contexts(user_question, candidate_contexts)
        end_time = time.time()
        
        run_time = end_time - start_time
        total_time += run_time
        
        print(f"  第{i+1}次: {run_time:.2f}秒 (筛选出{result.filtered_count}个上下文)")
    
    avg_time = total_time / test_runs
    print(f"\n📊 性能统计:")
    print(f"  • 平均处理时间: {avg_time:.2f}秒")
    print(f"  • 最终整理结果: 「{result.filtered_contexts[:100]}...」")


if __name__ == "__main__":
    print("🔧 FilterService功能演示")
    print("=" * 80)
    
    try:
        # 基础使用示例
        example_basic_usage()
        
        # 空上下文处理
        example_empty_contexts()
        
        # 低相关性筛选
        example_low_relevance_contexts()
        
        # 自定义阈值
        example_custom_threshold()
        
        # 性能测试
        example_performance_test()
        
        print("\n🎉 所有示例演示完成！")
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {str(e)}")
        print("请检查API配置是否正确。")
    
    print("=" * 80) 