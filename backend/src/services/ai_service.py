"""AI service for OpenAI interactions."""

import json
import logging

from fastapi import HTTPException
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Handles interactions with OpenAI API."""

    def __init__(self) -> None:
        """Initialize AI service with OpenAI client."""
        self.enabled = bool(settings.openai_api_key)
        self.client = OpenAI(api_key=settings.openai_api_key) if self.enabled else None
        self.model = settings.openai_model

    def _check_enabled(self) -> None:
        """Check if AI service is enabled.

        Raises:
            HTTPException: If OpenAI API key is not configured
        """
        if not self.enabled:
            raise HTTPException(
                status_code=503,
                detail="AI service is not available. OpenAI API key is not configured.",
            )

    def assess_relevance(self, title: str) -> str:
        """Assess news relevance to consumer goods pricing.

        Args:
            title: News article title

        Returns:
            Relevance score: 'high', 'medium', or 'low'

        Raises:
            HTTPException: If OpenAI API call fails or service is disabled
        """
        self._check_enabled()
        # noinspection PyTypeChecker
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            },
            {"role": "user", "content": title},
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            relevance = completion.choices[0].message.content
            if not relevance:
                logger.error(f"Empty relevance response for title: {title}")
                raise HTTPException(
                    status_code=500, detail="Failed to assess news relevance"
                )
            return relevance
        except Exception as e:
            logger.error(f"Error assessing relevance: {e}")
            raise HTTPException(
                status_code=500, detail=f"AI service error: {str(e)}"
            ) from e

    def generate_summary(self, content: str) -> dict[str, str]:
        """Generate news summary with impact and reason.

        Args:
            content: News article content

        Returns:
            Dictionary with '影響' (impact) and '原因' (reason) keys

        Raises:
            HTTPException: If OpenAI API call fails, response is invalid, or service is disabled
        """
        self._check_enabled()
        # noinspection PyTypeChecker
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
            },
            {"role": "user", "content": content},
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            result = completion.choices[0].message.content
            if not result:
                logger.error("Empty summary response from OpenAI")
                raise HTTPException(
                    status_code=500, detail="Failed to generate news summary"
                )

            parsed_result: dict[str, str] = json.loads(result)
            if "影響" not in parsed_result or "原因" not in parsed_result:
                logger.error(f"Invalid summary format: {parsed_result}")
                raise HTTPException(
                    status_code=500, detail="Invalid summary format from AI"
                )

            return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise HTTPException(
                status_code=500, detail="Invalid JSON response from AI"
            ) from e
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise HTTPException(
                status_code=500, detail=f"AI service error: {str(e)}"
            ) from e

    def extract_keywords(self, prompt: str) -> str:
        """Extract search keywords from user prompt.

        Args:
            prompt: User's search prompt

        Returns:
            Extracted keywords

        Raises:
            HTTPException: If OpenAI API call fails or service is disabled
        """
        self._check_enabled()
        # noinspection PyTypeChecker
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            keywords = completion.choices[0].message.content
            if not keywords:
                logger.error(f"Empty keywords response for prompt: {prompt}")
                raise HTTPException(
                    status_code=500, detail="Failed to extract keywords"
                )
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            raise HTTPException(
                status_code=500, detail=f"AI service error: {str(e)}"
            ) from e
