"""
上下文质量与相关性Filter层

该模块提供对候选上下文进行二次筛选的功能，确保交付给AI的是
最高质量、最相关的信息。
"""

from .filter_service import FilterService
from schemas.filter import FilteredResult, ContextItem

__version__ = "1.0.0"
__all__ = ["FilterService", "FilteredResult", "ContextItem"] 