from schemas.privacy import PrivacyLabel
from schemas.mcp import MCPMessage

class PrivacyService:
    """
    隐私评级Agent
    职责：评估文本的隐私等级。
    """
    def classify(
        self, 
        text_content: str, 
    ) -> PrivacyLabel:
        """
        使用混合模式（规则+LLM）为给定的文本评定隐私等级。

        Args:
            text_content: 需要被分析的文本片段。

        Returns:
            评定出的隐私等级标签。
        """
        pass
