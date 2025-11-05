"""News service for fetching, processing, and managing news articles."""

import itertools
import logging
from typing import Optional
from urllib.parse import quote

import requests
from fastapi import HTTPException

from src.config import settings
from src.repositories.news_repository import NewsRepository
from src.services.ai_service import AIService
from src.utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


def fetch_news_data(search_term: str, is_initial: bool = False) -> list[dict]:
    """Fetch news data from UDN API.

    Args:
        search_term: Search keyword
        is_initial: If True, fetch multiple pages; if False, fetch only first page

    Returns:
        List of news items from API

    Raises:
        HTTPException: If API request fails
    """
    try:
        if is_initial:
            news_pages = []
            for page_num in range(1, 10):
                params = {
                    "page": page_num,
                    "id": f"search:{quote(search_term)}",
                    "channelId": 2,
                    "type": "searchword",
                }
                response = requests.get(
                    settings.udn_news_api_url, params=params, timeout=30
                )
                response.raise_for_status()
                news_pages.extend(response.json().get("lists", []))
            return news_pages
        else:
            params = {
                "page": 1,
                "id": f"search:{quote(search_term)}",
                "channelId": 2,
                "type": "searchword",
            }
            response = requests.get(
                settings.udn_news_api_url, params=params, timeout=30
            )
            response.raise_for_status()
            return response.json().get("lists", [])
    except requests.RequestException as e:
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
        web_scraper: WebScraper,
    ) -> None:
        """Initialize news service.

        Args:
            news_repository: NewsRepository instance for database operations
            ai_service: AIService instance for AI operations
            web_scraper: WebScraper instance for web scraping
        """
        self.news_repository = news_repository
        self.ai_service = ai_service
        self.web_scraper = web_scraper
        self._id_counter = itertools.count(start=1000000)

    def process_and_store_news_article(self, news_item: dict) -> bool:
        """Process a single news item and store if relevant.

        Args:
            news_item: News item from API with 'title' and 'titleLink' keys

        Returns:
            True if article was stored, False otherwise
        """
        title = news_item.get("title")
        url = news_item.get("titleLink")

        if not title or not url:
            logger.warning("News item missing title or URL")
            return False

        # Check relevance
        relevance = self.ai_service.assess_relevance(title)
        if relevance != "high":
            logger.info(f"Article not relevant (relevance: {relevance}): {title}")
            return False

        # Scrape article content
        article_data = self.web_scraper.scrape_udn_article(url)
        if not article_data:
            logger.error(f"Failed to scrape article: {url}")
            return False

        # Generate summary
        content_text = " ".join(article_data["content"])
        summary_data = self.ai_service.generate_summary(content_text)

        # Store in database
        try:
            self.news_repository.create_news_article(
                url=url,
                title=article_data["title"],
                time=article_data["time"],
                content=content_text,
                summary=summary_data["影響"],
                reason=summary_data["原因"],
            )
            logger.info(f"Article stored successfully: {title}")
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
        news_data = fetch_news_data("價格", is_initial=is_initial)

        stored_count = 0
        for news_item in news_data:
            if self.process_and_store_news_article(news_item):
                stored_count += 1

        logger.info(
            f"News fetch complete: processed {len(news_data)}, stored {stored_count}"
        )

    def get_all_news_with_upvotes(
        self, user_id: Optional[int] = None
    ) -> list[dict[str, any]]:
        """Get all news articles with upvote information.

        Args:
            user_id: Optional user ID to check if user has upvoted

        Returns:
            List of news articles with upvote counts and user's upvote status
        """
        news_articles = self.news_repository.get_all_news()
        result = []

        for article in news_articles:
            upvote_count = self.news_repository.get_upvote_count(article.id)
            is_upvoted = False
            if user_id:
                is_upvoted = self.news_repository.user_has_upvoted(article.id, user_id)

            result.append(
                {
                    **article.__dict__,
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

        # Fetch news based on keywords
        news_items = fetch_news_data(keywords, is_initial=False)

        news_list = []
        for news_item in news_items:
            url = news_item.get("titleLink")
            if not url:
                continue

            try:
                article_data = self.web_scraper.scrape_udn_article(url)
                if not article_data:
                    continue

                news_list.append(
                    {
                        "id": next(self._id_counter),
                        "url": url,
                        "title": article_data["title"],
                        "time": article_data["time"],
                        "content": " ".join(article_data["content"]),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to process news item: {e}")
                continue

        # Sort by time (descending)
        return sorted(news_list, key=lambda x: x["time"], reverse=True)
