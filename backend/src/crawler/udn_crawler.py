"""UDN News Crawler implementation."""

import logging
from urllib.parse import quote
from typing import Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement, ResultSet, Tag
from pydantic import AnyHttpUrl
from sqlalchemy.orm import Session

from .crawler_base import NewsCrawlerBase, Headline, News
from src.config import settings

logger = logging.getLogger(__name__)


class UDNCrawler(NewsCrawlerBase):
    """Concrete implementation of news crawler for UDN (聯合新聞網).

    Implements all abstract methods from NewsCrawlerBase to crawl,
    parse, and store news articles from UDN news website.

    Attributes:
        news_website_url: UDN main website URL
        news_website_news_child_urls: List of valid UDN child URLs
    """

    news_website_url: str = "https://udn.com"
    news_website_news_child_urls: list[str] = []

    def get_headline(
            self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:
        """Fetch news headlines from UDN API based on search term.

        Args:
            search_term: Search keyword to query UDN news
            page: Page number (int) or page range (tuple[int, int]) to fetch

        Returns:
            List of Headline objects with title and URL

        Raises:
            requests.RequestException: If API request fails
        """
        try:
            headlines = []

            # Determine page range
            if isinstance(page, tuple):
                start_page, end_page = page
                pages_to_fetch = range(start_page, end_page + 1)
            else:
                pages_to_fetch = range(page, page + 1)

            # Fetch headlines from each page
            for page_num in pages_to_fetch:
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

                news_items = response.json().get("lists", [])

                # Convert to Headline objects
                for item in news_items:
                    title = item.get("title")
                    url = item.get("titleLink")
                    if title and url:
                        headlines.append(Headline(title=title, url=url))

            logger.info(f"Fetched {len(headlines)} headlines for '{search_term}'")
            return headlines

        except requests.RequestException as e:
            logger.error(f"Failed to fetch headlines: {e}")
            raise

    def parse(self, url: AnyHttpUrl | str) -> News:
        """Parse UDN article content from given URL.

        Scrapes the article page and extracts title, publication time,
        and content paragraphs.

        Args:
            url: URL of the UDN article to parse

        Returns:
            News object with title, url, time, and content

        Raises:
            ValueError: If article parsing fails or required elements not found
            requests.RequestException: If HTTP request fails
        """
        try:
            response = requests.get(str(url), timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_element = soup.find("h1", class_="article-content__title")
            if not title_element:
                raise ValueError(f"Title not found for URL: {url}")
            title = title_element.text.strip()

            # Extract time
            time_element = soup.find("time", class_="article-content__time")
            if not time_element:
                raise ValueError(f"Time not found for URL: {url}")
            time = time_element.text.strip()

            # Extract content
            content_section = soup.find("section", class_="article-content__editor")
            if not content_section:
                raise ValueError(f"Content section not found for URL: {url}")

            paragraphs = [
                p.text.strip()
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]

            content = " ".join(paragraphs)

            logger.info(f"Successfully parsed article: {title}")
            return News(title=title, url=str(url), time=time, content=content)

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing article {url}: {e}")
            raise ValueError(f"Failed to parse article: {e}") from e

    @staticmethod
    def save(news: News, db: Session | None):
        """Save news article to database.

        Note: This is a static method that should be called with appropriate
        repository implementation. Current implementation is a placeholder
        and should be integrated with the actual repository layer.

        Args:
            news: News object to save
            db: Database session (optional, for future use)

        Returns:
            None

        Raises:
            NotImplementedError: Actual database implementation pending
        """
        # This will be implemented when integrating with NewsService
        # For now, this is a placeholder that satisfies the abstract method requirement
        logger.info(f"Save method called for article: {news.title}")
        # Actual implementation will use repository pattern:
        # from src.repositories.news_repository import NewsRepository
        # repository = NewsRepository(db)
        # repository.create_news_article(...)
        pass
