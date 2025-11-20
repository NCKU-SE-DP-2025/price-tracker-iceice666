"""Web scraper utility for extracting news article content."""

import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement, ResultSet, Tag

logger = logging.getLogger(__name__)


class WebScraper:
    """Handles web scraping operations for news articles."""

    @staticmethod
    def _soup_find(soup: Tag, *args, **kwargs) -> Optional[PageElement]:
        """Safely find an element in BeautifulSoup.

        Args:
            soup: BeautifulSoup Tag object
            *args: Positional arguments for find()
            **kwargs: Keyword arguments for find()

        Returns:
            Found element or None
        """
        return soup.find(*args, **kwargs)

    @staticmethod
    def _soup_find_all(soup: Tag, *args, **kwargs) -> ResultSet:
        """Safely find all elements in BeautifulSoup.

        Args:
            soup: BeautifulSoup Tag object
            *args: Positional arguments for find_all()
            **kwargs: Keyword arguments for find_all()

        Returns:
            ResultSet of found elements
        """
        return soup.find_all(*args, **kwargs)

    def scrape_udn_article(self, url: str) -> Optional[dict[str, str | list[str]]]:
        """Scrape a UDN news article.

        Args:
            url: Article URL

        Returns:
            Dictionary with title, time, and content, or None if scraping fails
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_element = self._soup_find(soup, "h1", class_="article-content__title")
            if not title_element:
                logger.error(f"Title not found for URL: {url}")
                return None
            title = title_element.text

            # Extract time
            time_element = self._soup_find(soup, "time", class_="article-content__time")
            if not time_element:
                logger.error(f"Time not found for URL: {url}")
                return None
            time = time_element.text

            # Extract content
            content_section = soup.find("section", class_="article-content__editor")
            if not content_section:
                logger.error(f"Content section not found for URL: {url}")
                return None

            paragraphs = [
                p.text
                for p in self._soup_find_all(content_section, "p")
                if p.text.strip() != "" and "▪" not in p.text
            ]

            return {
                "title": title,
                "time": time,
                "content": paragraphs,
            }

        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None
