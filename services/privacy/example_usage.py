"""
隐私分级模块使用示例

该文件展示了如何使用隐私分级模块来评估不同类型文本的隐私敏感度。
"""

import json
from privacy_classifier import PrivacyClassifier, PrivacyLevel, PrivacyLabel


def example_usage():
    """隐私分级模块使用示例"""
    
    # 初始化隐私分类器
    classifier = PrivacyClassifier()
    
    # 测试用例：不同敏感度级别的文本示例
    test_cases = [
        {
            "name": "1级 - 公开信息",
            "text": "我们公司发布了新的开源项目，欢迎大家访问GitHub仓库查看代码。",
            "expected_level": 1
        },
        {
            "name": "2级 - 内部日常",
            "text": "下周三团队例会讨论Q1的OKR进展，会议室在3楼会议室A。",
            "expected_level": 2
        },
        {
            "name": "3级 - 受限敏感",
            "text": "张三(zhang.san@company.com)负责新产品的UI设计，预计下个月完成原型。",
            "expected_level": 3
        },
        {
            "name": "4级 - 机密信息",
            "text": "我们的核心算法使用了专有的深度学习模型，参数配置如下：learning_rate=0.001, batch_size=64",
            "expected_level": 4
        },
        {
            "name": "5级 - 极端敏感",
            "text": "用户身份证号：110101199001018080，银行卡号：6228482188888888888",
            "expected_level": 5
        }
    ]
    
    print("=" * 80)
    print("隐私分级模块测试示例")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试案例 {i}】{case['name']}")
        print(f"文本内容：{case['text']}")
        print(f"预期级别：{case['expected_level']}级")
        
        # 获取分类提示词
        prompt = classifier.get_classification_prompt(case['text'])
        
        print("\n生成的分类提示词：")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 40)
        
        # 模拟AI返回的分类结果
        mock_result = {
            "privacy_level": case['expected_level'],
            "confidence": 0.95,
            "reasoning": f"该文本包含{case['name']}类型的信息，符合{case['expected_level']}级分类标准。",
            "risk_indicators": ["测试风险指标1", "测试风险指标2"],
            "compliance_notes": "测试合规注释" if case['expected_level'] >= 4 else None
        }
        
        # 解析分类结果
        privacy_label = classifier.parse_classification_result(mock_result)
        
        print(f"\n分类结果：")
        print(f"  级别：{privacy_label.level.value}级")
        print(f"  置信度：{privacy_label.confidence:.2f}")
        print(f"  分级理由：{privacy_label.reasoning}")
        print(f"  风险指标：{privacy_label.risk_indicators}")
        print(f"  合规注释：{privacy_label.compliance_notes}")
        
        print("\n" + "=" * 80)


def demonstrate_json_format():
    """演示JSON格式的输入输出"""
    
    print("\n【JSON格式示例】")
    print("=" * 50)
    
    # 示例：模拟AI返回的完整JSON响应
    sample_ai_response = {
        "privacy_level": 4,
        "confidence": 0.92,
        "reasoning": "该文本包含公司核心算法的技术细节和参数配置，属于公司核心竞争信息。泄露将可能导致重大商业风险，符合机密/合规管控级别的判定标准。",
        "risk_indicators": [
            "包含算法技术细节",
            "暴露核心参数配置",
            "可能影响商业竞争优势"
        ],
        "compliance_notes": "建议按照公司信息安全管理制度进行严格保护，限制访问权限，并进行审计日志记录。"
    }
    
    print("AI返回的JSON响应示例：")
    print(json.dumps(sample_ai_response, ensure_ascii=False, indent=2))
    
    # 解析为PrivacyLabel对象
    classifier = PrivacyClassifier()
    privacy_label = classifier.parse_classification_result(sample_ai_response)
    
    print(f"\n解析后的PrivacyLabel对象：")
    print(f"  级别：{privacy_label.level}")
    print(f"  置信度：{privacy_label.confidence}")
    print(f"  分级理由：{privacy_label.reasoning}")
    print(f"  风险指标：{privacy_label.risk_indicators}")
    print(f"  合规注释：{privacy_label.compliance_notes}")


def demonstrate_edge_cases():
    """演示边界情况处理"""
    
    print("\n【边界情况处理示例】")
    print("=" * 50)
    
    classifier = PrivacyClassifier()
    
    edge_cases = [
        {
            "name": "空文本",
            "text": "",
            "description": "处理空输入"
        },
        {
            "name": "混合敏感度",
            "text": "今天的会议讨论了新产品发布计划，张经理的身份证号是110101199001018080，需要用于合同签署。",
            "description": "包含多种敏感度信息，应选择最高级别"
        },
        {
            "name": "模糊边界",
            "text": "公司员工李四在技术部门工作，负责数据库维护。",
            "description": "边界模糊的情况"
        }
    ]
    
    for case in edge_cases:
        print(f"\n【{case['name']}】")
        print(f"描述：{case['description']}")
        print(f"文本：{case['text']}")
        
        prompt = classifier.get_classification_prompt(case['text'])
        print(f"提示词长度：{len(prompt)} 字符")
        print("提示词片段：", prompt[:200] + "...")


if __name__ == "__main__":
    # 运行示例
    example_usage()
    demonstrate_json_format()
    demonstrate_edge_cases()
    
    print("\n" + "=" * 80)
    print("隐私分级模块示例运行完成！")
    print("=" * 80) 