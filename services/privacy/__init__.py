"""
隐私分级模块

该模块提供基于敏感度分级的隐私数据分类功能，帮助AI系统
识别和区分用户数据的敏感程度，从1-5级进行精确分类。
"""

from .privacy_classifier import PrivacyClassifier
from schemas.privacy import PrivacyLabel, PrivacyLevel

__version__ = "1.0.0"
__all__ = ["PrivacyLabel", "PrivacyLevel", "PrivacyClassifier"] 