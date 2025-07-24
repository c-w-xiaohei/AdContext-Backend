from pydantic import BaseModel, Field
from schemas.privacy import PrivacyLabel
class Metadata(BaseModel):
    """存储在mem0中的元数据结构"""
    privacy_level: PrivacyLabel
