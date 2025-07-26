from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class PrivacyLevel(Enum):
    """隐私敏感度级别枚举"""
    LEVEL_1_PUBLIC = 1          # 公开可检索 (Non-Sensitive)
    LEVEL_2_INTERNAL = 2        # 内部日常 (Low)
    LEVEL_3_RESTRICTED = 3      # 受限敏感 (Moderate)  
    LEVEL_4_CONFIDENTIAL = 4    # 机密/合规管控 (Confidential)
    LEVEL_5_CRITICAL = 5        # 极端敏感/关键凭证 (Critical)


@dataclass
class PrivacyLabel:
    """隐私标签数据结构"""
    level: PrivacyLevel
    confidence: float           # 置信度 (0.0-1.0)
    brief: str              # 摘要
    risk_indicators: List[str]  # 风险指标
    compliance_notes: Optional[str] = None  # 合规注释
