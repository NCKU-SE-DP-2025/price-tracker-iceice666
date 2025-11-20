"""News-related API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from src.models.database import User
from src.schemas.news import NewsSummaryRequest, NewsSummaryResponse, PromptRequest
from src.services.ai_service import AIService
from src.services.news_service import NewsService
from src.utils.dependencies import get_ai_service, get_current_user, get_news_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.get("/news")
def get_news(
    news_service: NewsService = Depends(get_news_service),
) -> list[dict[str, Any]]:
    """Get all news articles (public endpoint).

    Args:
        news_service: News service

    Returns:
        List of news articles with upvote information
    """
    return news_service.get_all_news_with_upvotes(user_id=None)


@router.get("/user_news")
def get_user_news(
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
) -> list[dict[str, Any]]:
    """Get all news articles with user's upvote status (authenticated endpoint).

    Args:
        current_user: Current authenticated user
        news_service: News service

    Returns:
        List of news articles with upvote information including user's upvote status
    """
    return news_service.get_all_news_with_upvotes(user_id=current_user.id)


@router.post("/search_news")
def search_news(
    request: PromptRequest,
    news_service: NewsService = Depends(get_news_service),
) -> list[dict[str, Any]]:
    """Search for news articles based on user prompt.

    Args:
        request: Search prompt request
        news_service: News service

    Returns:
        List of news articles matching search criteria

    Raises:
        HTTPException: If search fails
    """
    return news_service.search_news(request.prompt)


@router.post("/news_summary", response_model=NewsSummaryResponse)
def generate_news_summary(
    request: NewsSummaryRequest,
        ai_service: AIService = Depends(get_ai_service),
) -> NewsSummaryResponse:
    """Generate summary for news content (authenticated endpoint).

    Args:
        request: News content for summary generation
        ai_service: AI service

    Returns:
        Generated summary with impact and reason

    Raises:
        HTTPException: If summary generation fails
    """
    result = ai_service.generate_summary(request.content)
    return NewsSummaryResponse(summary=result["影響"], reason=result["原因"])


@router.post("/{news_id}/upvote")
def upvote_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
) -> dict[str, str]:
    """Toggle upvote for a news article (authenticated endpoint).

    Args:
        news_id: News article ID
        current_user: Current authenticated user
        news_service: News service

    Returns:
        Message indicating action taken

    Raises:
        HTTPException: If article not found
    """
    message = news_service.toggle_upvote(news_id, current_user.id)
    return {"message": message}
