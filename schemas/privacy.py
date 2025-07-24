from enum import Enum

class PrivacyLabel(str, Enum):
    """上下文片段的隐私等级"""
    PUBLIC = "PUBLIC"          # 完全公开信息
    PERSONAL = "PERSONAL"      # 个人但非敏感信息，如偏好
    CONFIDENTIAL = "CONFIDENTIAL" # 机密信息，如项目细节、非公开对话
    SENSITIVE = "SENSITIVE"    # 高度敏感信息，如PII、密码、密钥
