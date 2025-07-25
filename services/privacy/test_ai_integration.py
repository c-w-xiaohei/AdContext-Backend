"""
隐私分级模块AI集成测试

测试硅基流动Qwen模型的集成效果
"""

from privacy_classifier import PrivacyClassifier, PrivacyLevel
import time

def test_ai_classification():
    """测试AI分类功能"""
    print("🚀 开始测试隐私分级AI模型集成...")
    
    # 初始化分类器
    classifier = PrivacyClassifier()
    
    # 测试用例
    test_cases = [
        {
            "name": "1级测试 - 公开信息",
            "text": "今天天气很好，我们公司发布了新的开源项目。",
            "expected_level": 1
        },
        {
            "name": "3级测试 - 员工信息",
            "text": "张三(zhang.san@company.com)是我们的产品经理，负责新功能开发。",
            "expected_level": 3
        },
        {
            "name": "5级测试 - 身份证信息", 
            "text": "用户身份证号：110101199001011234，请妥善保管。",
            "expected_level": 5
        }
    ]
    
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试案例 {i}】{case['name']}")
        print(f"📝 文本内容: {case['text']}")
        print(f"🎯 预期级别: {case['expected_level']}级")
        
        try:
            # 调用AI进行分类
            print("⏳ 正在调用AI模型进行分析...")
            start_time = time.time()
            
            privacy_label = classifier.classify(case['text'])
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 显示结果
            print(f"✅ 分析完成 (耗时: {response_time:.2f}秒)")
            print(f"📊 分类结果:")
            print(f"   级别: {privacy_label.level.value}级")
            print(f"   置信度: {privacy_label.confidence:.2f}")
            print(f"   分级理由: {privacy_label.reasoning}")
            print(f"   风险指标: {privacy_label.risk_indicators}")
            if privacy_label.compliance_notes:
                print(f"   合规注释: {privacy_label.compliance_notes}")
            
            # 判断准确性
            if privacy_label.level.value == case['expected_level']:
                print("🎉 分类结果符合预期！")
            else:
                print(f"⚠️  分类结果与预期不符 (预期: {case['expected_level']}级)")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
        
        print("-" * 60)
        
        # 避免API调用过于频繁
        if i < len(test_cases):
            print("⏱️  等待1秒后继续下一个测试...")
            time.sleep(1)

def test_error_handling():
    """测试错误处理"""
    print("\n🛡️ 测试错误处理能力...")
    
    # 使用无效的API密钥进行测试
    invalid_classifier = PrivacyClassifier(api_key="invalid_key")
    
    try:
        result = invalid_classifier.classify("测试文本")
        print("❌ 错误处理测试失败：应该抛出异常")
    except Exception as e:
        print(f"✅ 错误处理正常：{str(e)}")

def test_prompt_generation():
    """测试提示词生成功能"""
    print("\n📝 测试提示词生成功能...")
    
    classifier = PrivacyClassifier()
    test_text = "这是一个测试文本"
    
    prompt = classifier.get_classification_prompt(test_text)
    
    print(f"✅ 提示词生成成功")
    print(f"📏 提示词长度: {len(prompt)} 字符")
    print(f"🔍 包含测试文本: {'测试文本' in prompt}")
    print(f"📋 包含分级标准: {'隐私分级标准' in prompt}")

if __name__ == "__main__":
    print("🔒 隐私分级模块 - AI集成测试")
    print("=" * 80)
    
    # 测试提示词生成（不需要API调用）
    test_prompt_generation()
    
    # 测试实际AI分类（需要API调用）
    print("\n" + "=" * 80)
    choice = input("是否进行AI模型测试？这将调用真实的API (y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是']:
        test_ai_classification()
        test_error_handling()
        print("\n🎉 所有测试完成！")
    else:
        print("📋 跳过AI模型测试")
    
    print("=" * 80) 