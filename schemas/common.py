from pydantic import BaseModel, Field
from schemas.privacy import PrivacyLevel

class Metadata(BaseModel):
    """存储在mem0中的元数据结构"""
    privacy_level: PrivacyLevel
    source: str
    
class RetriveResult(BaseModel):
    """
    检索结果
    """
    context:str
    metadata:Metadata
    score:float
    
class ListResult(BaseModel):
    """
    列出结果
    """
    context:str
    metadata:Metadata
