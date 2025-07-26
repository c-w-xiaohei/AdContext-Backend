# 隐私分级模块

## 概述

隐私分级模块是一个基于AI的智能隐私数据分类系统，能够自动评估文本内容的隐私敏感度级别。该模块采用1-5级分级标准，帮助系统识别和区分用户数据的敏感程度，确保数据得到适当的保护。

## 特性

- 🔍 **智能分析**：基于AI的文本内容隐私敏感度评估
- 📊 **精确分级**：1-5级精确隐私敏感度分类
- 🛡️ **合规保护**：支持GDPR、HIPAA、PCI-DSS等法规要求
- 📝 **详细报告**：提供分级理由、风险指标和合规建议
- 🔧 **易于集成**：简单的API接口，易于集成到现有系统

## 隐私分级标准

### 1级 - 公开可检索 (Non-Sensitive)
- **判定标准**：已在互联网上公开发布；法规无任何保护要求；泄露基本无风险
- **示例**：公司官网文章、博客、开源 README、公开招聘信息
- **保护要求**：无特殊保护要求，可公开传输和存储

### 2级 - 内部日常 (Low)
- **判定标准**：未公开，但不含可识别个人/商业关键；泄露仅带来轻微不便或品牌喧声
- **示例**：例行会议议程、团队 OKR 概览、个人兴趣偏好（爱喝拿铁）
- **保护要求**：内部访问控制，基础传输加密

### 3级 - 受限敏感 (Moderate)
- **判定标准**：间接识别个人（姓名+职位+公司电邮）；一般商业机密（产品路线图、成本结构）；法规要求"合理保护"
- **示例**：员工花名册（无身份证号）、未发布功能设计文档、财务预算概览
- **保护要求**：合理保护措施，访问权限管理，传输和存储加密

### 4级 - 机密/合规管控 (Confidential)
- **判定标准**：公司核心竞争信息：源代码、算法细节、技术价格；法规要求备案或严格披露义务；泄露将导致重大商业/法律风险
- **示例**：专利草稿、年度财务预测表、关键算法参数
- **保护要求**：严格访问控制，强加密保护，审计日志记录，合规报告要求

### 5级 - 极端敏感/关键凭证 (Critical)
- **判定标准**：直接识别或不可逆危害：身份证号、银行卡号、CVV、健康/基因数据；任一可造成账号接管、资金损失、重大安全事故的凭证；受 GDPR《特殊类别数据》、HIPAA、PCI-DSS 等强监管
- **示例**：私钥/助记词、生产数据库 root 密码、生物特征模板、MRI 影像、完整客户信用卡记录
- **保护要求**：最高级别安全措施，端到端加密，零信任架构，严格的监管合规，定期安全评估

## 快速开始

### 依赖安装

```bash
pip install -U google-genai
```

### 基本使用

#### 方式1：一站式分类（推荐）

```python
from privacy import PrivacyClassifier

# 初始化分类器（使用默认的Gemini API）
classifier = PrivacyClassifier()

# 直接对文本进行隐私分级
text = "用户身份证号：110101199001018080，银行卡号：6228482188888888888"
privacy_label = classifier.classify(text)

print(f"隐私级别: {privacy_label.level.value}级")
print(f"置信度: {privacy_label.confidence}")
print(f"分级理由: {privacy_label.reasoning}")
```

#### 方式2：自定义API配置

```python
# 使用自定义API密钥和模型
classifier = PrivacyClassifier(
    api_key="your-api-key",
    model_name="gemini-2.5-flash-lite"
)

privacy_label = classifier.classify("敏感文本内容")
```

#### 方式3：手动流程（适用于自定义AI服务）

```python
# 生成提示词
prompt = classifier.get_classification_prompt(text)

# 调用您自己的AI服务
ai_result = your_ai_service.complete(prompt)

# 解析结果
privacy_label = classifier.parse_classification_result(ai_result)
```

### 数据结构

#### PrivacyLevel 枚举
```python
class PrivacyLevel(Enum):
    LEVEL_1_PUBLIC = 1          # 公开可检索
    LEVEL_2_INTERNAL = 2        # 内部日常
    LEVEL_3_RESTRICTED = 3      # 受限敏感
    LEVEL_4_CONFIDENTIAL = 4    # 机密/合规管控
    LEVEL_5_CRITICAL = 5        # 极端敏感/关键凭证
```

#### PrivacyLabel 数据类
```python
@dataclass
class PrivacyLabel:
    level: PrivacyLevel         # 隐私级别
    confidence: float           # 置信度 (0.0-1.0)
    reasoning: str              # 分级理由
    risk_indicators: List[str]  # 风险指标
    compliance_notes: Optional[str] = None  # 合规注释
```

## API 参考

### PrivacyClassifier

#### `__init__(api_key: str, model_name: str)`
初始化隐私分类器，默认使用AiHubMix的Gemini模型。

#### `classify(context_fragment: str, additional_context: Optional[str] = None) -> PrivacyLabel`
**一站式隐私分级方法**，直接对文本进行AI分析并返回分级结果。

#### `get_classification_prompt(context_fragment: str, additional_context: Optional[str] = None) -> str`
生成用于AI模型的隐私分类提示词（手动流程使用）。

#### `parse_classification_result(result: dict) -> PrivacyLabel`
解析AI返回的分类结果为PrivacyLabel对象（手动流程使用）。


## AI响应格式

AI模型应返回以下JSON格式的结果：

```json
{
    "privacy_level": 1-5,
    "confidence": 0.0-1.0,
    "reasoning": "详细的分级理由说明",
    "risk_indicators": ["风险指标1", "风险指标2"],
    "compliance_notes": "相关的法规要求说明（可选）"
}
```

## AI模型配置

### 支持的模型

隐私分级模块默认使用AiHubMix平台的Gemini模型：

- **默认模型**: `gemini-2.5-flash-lite`
- **支持模型**: 任何支持JSON输出的Gemini系列模型
- **API平台**: https://aihubmix.com

### 配置选项

```python
# 使用默认配置
classifier = PrivacyClassifier()

# 自定义API密钥
classifier = PrivacyClassifier(api_key="your-api-key")

# 自定义模型
classifier = PrivacyClassifier(
    api_key="your-api-key",
    model_name="gemini-pro"
)
```

### 模型参数

- **Temperature**: 0.1 (降低随机性，提高分类一致性)
- **Max Tokens**: 1000
- **Timeout**: 30秒

## 使用示例

### 运行测试代码

```bash
cd privacy
python test_ai_integration.py
```

### 运行示例代码

```bash
cd privacy
python example_usage.py
```

示例将展示：
- Gemini模型的实际分类效果
- 不同敏感度级别的文本分类
- JSON格式的输入输出
- 边界情况的处理

## 集成指南

### 与现有系统集成

#### 推荐方式：使用内置AI分类

```python
from privacy import PrivacyClassifier, PrivacyLevel

# 1. 初始化分类器
classifier = PrivacyClassifier()

# 2. 直接分析用户输入
privacy_label = classifier.classify(user_input)

# 3. 根据级别采取保护措施
if privacy_label.level.value >= 4:
    # 实施严格的安全措施
    apply_strict_security(user_input)
elif privacy_label.level.value >= 3:
    # 实施标准保护措施
    apply_standard_protection(user_input)
else:
    # 基础处理
    process_normally(user_input)
```

#### 自定义AI服务集成

```python
# 1. 导入模块
from privacy import PrivacyClassifier, PrivacyLevel

# 2. 初始化分类器
classifier = PrivacyClassifier()

# 3. 生成提示词
prompt = classifier.get_classification_prompt(user_text)

# 4. 调用您的AI服务
ai_response = your_ai_service.complete(prompt)

# 5. 解析结果
privacy_label = classifier.parse_classification_result(ai_response)

# 6. 根据级别处理
handle_based_on_privacy_level(privacy_label)
```

## 最佳实践

### 1. 保守原则
在不确定的情况下，倾向于选择更高的安全级别。

### 2. 组合敏感度
如果文本包含多种敏感度的信息，选择最高敏感度级别。

### 3. 上下文考虑
结合具体的业务场景和使用上下文进行判断。

### 4. 定期审核
定期审核和更新分类结果，确保准确性。

### 5. 合规遵循
严格遵循相关的法规要求，如GDPR、HIPAA、PCI-DSS等。

## 注意事项

1. **独立模块**: 该模块设计为独立运行，不与其他系统组件产生依赖关系
2. **AI模型要求**: 需要有效的AiHubMix API密钥
3. **敏感数据处理**: 在处理5级敏感数据时，建议实施额外的安全措施
4. **定期更新**: 建议定期更新分级标准以适应新的法规要求

## 许可证

该模块遵循项目主许可证。

## 贡献

欢迎提交问题报告和功能请求。如需贡献代码，请遵循项目的贡献指南。 