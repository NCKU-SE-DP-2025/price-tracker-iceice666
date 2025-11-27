"""News service for fetching, processing, and managing news articles."""

import itertools
import logging
from typing import Optional

from fastapi import HTTPException

from src.crawler import UDNCrawler, Headline
from src.repositories.news_repository import NewsRepository
from src.services.ai_service import AIService
from src.utils.sanitizer import sanitize_html, sanitize_text

logger = logging.getLogger(__name__)


def fetch_news_data(search_term: str, is_initial: bool = False) -> list[Headline]:
    """Fetch news headlines using UDNCrawler.

    Args:
        search_term: Search keyword
        is_initial: If True, fetch multiple pages; if False, fetch only first page

    Returns:
        List of Headline objects from UDNCrawler

    Raises:
        HTTPException: If API request fails
    """
    try:
        crawler = UDNCrawler()
        if is_initial:
            # Fetch pages 1-9 for initial load
            headlines = crawler.get_headline(search_term, page=(1, 9))
        else:
            # Fetch only page 1
            headlines = crawler.get_headline(search_term, page=1)

        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch news data: {e}")
        raise HTTPException(
            status_code=502, detail="Failed to fetch news from external API"
        ) from e


class NewsService:
    """Handles news fetching, scraping, and storage operations."""

    def __init__(
        self,
        news_repository: NewsRepository,
        ai_service: AIService,
    ) -> None:
        """Initialize news service.

        Args:
            news_repository: NewsRepository instance for database operations
            ai_service: AIService instance for AI operations
        """
        self.news_repository = news_repository
        self.ai_service = ai_service
        self.crawler = UDNCrawler()
        self._id_counter = itertools.count(start=1000000)

    def process_and_store_news_article(self, headline: Headline) -> bool:
        """Process a single news headline and store if relevant.

        Args:
            headline: Headline object with title and URL

        Returns:
            True if article was stored, False otherwise
        """
        # Check relevance
        relevance = self.ai_service.assess_relevance(headline.title)
        if relevance != "high":
            logger.info(f"Article not relevant (relevance: {relevance}): {headline.title}")
            return False

        # Parse article content using crawler
        try:
            news = self.crawler.parse(headline.url)
        except Exception as e:
            logger.error(f"Failed to parse article: {e}")
            return False

        # Sanitize content to prevent XSS attacks
        sanitized_content = sanitize_html(news.content)

        # Generate summary with sanitized content
        summary_data = self.ai_service.generate_summary(sanitized_content)

        # Store in database with sanitized data
        try:
            self.news_repository.create_news_article(
                url=str(news.url),
                title=sanitize_text(news.title),  # Title should be plain text
                time=news.time,
                content=sanitized_content,  # HTML content sanitized
                summary=sanitize_text(summary_data["影響"]),  # Summary as plain text
                reason=sanitize_text(summary_data["原因"]),  # Reason as plain text
            )
            logger.info(f"Article stored successfully: {headline.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to store article: {e}")
            return False

    def fetch_and_process_news(self, is_initial: bool = False) -> None:
        """Fetch news from API and process relevant articles.

        Args:
            is_initial: If True, fetch multiple pages for initial load
        """
        logger.info(f"Starting news fetch (initial: {is_initial})")
        headlines = fetch_news_data("價格", is_initial=is_initial)

        stored_count = 0
        for headline in headlines:
            if self.process_and_store_news_article(headline):
                stored_count += 1

        logger.info(
            f"News fetch complete: processed {len(headlines)}, stored {stored_count}"
        )

    def get_all_news_with_upvotes(
        self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> list[dict[str, any]]:
        """Get news articles with upvote information and pagination.

        Args:
            user_id: Optional user ID to check if user has upvoted
            skip: Number of articles to skip (for pagination)
            limit: Maximum number of articles to return

        Returns:
            List of news articles with upvote counts and user's upvote status
        """
        news_articles = self.news_repository.get_all_news(skip=skip, limit=limit)
        result = []

        for article in news_articles:
            upvote_count = self.news_repository.get_upvote_count(article.id)
            is_upvoted = False
            if user_id:
                is_upvoted = self.news_repository.user_has_upvoted(article.id, user_id)

            result.append(
                {
                    "id": article.id,
                    "url": article.url,
                    "title": article.title,
                    "time": article.time,
                    "content": article.content,
                    "summary": article.summary,
                    "reason": article.reason,
                    "upvotes": upvote_count,
                    "is_upvoted": is_upvoted,
                }
            )

        return result

    def toggle_upvote(self, news_id: int, user_id: int) -> str:
        """Toggle upvote for a news article.

        Args:
            news_id: Article ID
            user_id: User ID

        Returns:
            Message indicating action taken

        Raises:
            HTTPException: If article not found
        """
        if not self.news_repository.news_exists(news_id):
            raise HTTPException(status_code=404, detail="News article not found")

        if self.news_repository.user_has_upvoted(news_id, user_id):
            self.news_repository.remove_upvote(news_id, user_id)
            return "Upvote removed"
        else:
            self.news_repository.add_upvote(news_id, user_id)
            return "Article upvoted"

    def search_news(self, prompt: str) -> list[dict[str, any]]:
        """Search for news based on user prompt.

        Args:
            prompt: User's search query

        Returns:
            List of news articles matching the search

        Raises:
            HTTPException: If keyword extraction fails or news fetch fails
        """
        # Extract keywords using AI
        keywords = self.ai_service.extract_keywords(prompt)
        logger.info(f"Extracted keywords from prompt: {keywords}")

        # Fetch news headlines based on keywords
        headlines = fetch_news_data(keywords, is_initial=False)

        news_list = []
        for headline in headlines:
            try:
                # Parse article using crawler
                news = self.crawler.parse(headline.url)

                news_list.append(
                    {
                        "id": next(self._id_counter),
                        "url": str(news.url),
                        "title": news.title,
                        "time": news.time,
                        "content": news.content,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to process news item: {e}")
                continue

        # Sort by time (descending)
        return sorted(news_list, key=lambda x: x["time"], reverse=True)
