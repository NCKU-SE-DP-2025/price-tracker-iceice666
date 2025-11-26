"""Abstract base class for news crawlers with Pydantic models."""

import abc
from pydantic import BaseModel, Field, AnyHttpUrl
from sqlalchemy.orm import Session
import tldextract

from .exceptions import DomainMismatchException


class Headline(BaseModel):
    """Basic news headline with title and URL.

    Attributes:
        title: The title of the article
        url: The URL of the article
    """

    title: str = Field(
        default=...,
        example="Title of the article",
        description="The title of the article"
    )
    url: AnyHttpUrl | str = Field(
        default=...,
        example="https://www.example.com",
        description="The URL of the article"
    )


class News(Headline):
    """Complete news article with content and timestamp.

    Inherits title and url from Headline, adds time and content.

    Attributes:
        time: Publication timestamp
        content: Full article content
    """

    time: str = Field(
        default=...,
        example="2021-10-01T00:00:00",
        description="The time the article was published"
    )
    content: str = Field(
        default=...,
        example="Content of the article",
        description="The content of the article"
    )


class NewsWithSummary(News):
    """News article with AI-generated summary and reason.

    Inherits all fields from News, adds summary and reason.

    Attributes:
        summary: AI-generated summary of the article
        reason: Reason why the article is relevant
    """

    summary: str = Field(
        default=...,
        example="Summary of the article",
        description="The summary of the article"
    )
    reason: str = Field(
        default=...,
        example="Reason of the article",
        description="The reason of the article"
    )


class NewsCrawlerBase(metaclass=abc.ABCMeta):
    """Abstract base class for news website crawlers.

    Defines the interface for crawling news websites, including:
    - Searching for headlines
    - Parsing article content
    - Domain validation
    - Saving to database

    Attributes:
        news_website_url: Main URL of the news website
        news_website_news_child_urls: List of valid child URLs for the news website
    """

    news_website_url: AnyHttpUrl | str
    news_website_news_child_urls: list[AnyHttpUrl | str]

    @abc.abstractmethod
    def get_headline(
            self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:
        """Search for news headlines based on search term.

        This method searches through the news_website_url using the specified search term,
        and returns a list of Headline objects. The page parameter can be an integer
        representing a single page number or a tuple representing a range of page numbers.

        Args:
            search_term: A search term to search for news articles
            page: A page number (int) or a tuple of start and end page numbers (tuple[int, int])

        Returns:
            A list of Headline objects, each containing a title and a URL

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        return NotImplemented

    @abc.abstractmethod
    def parse(self, url: AnyHttpUrl | str) -> News:
        """Fetch and parse detailed news content from URL.

        This method takes a URL that belongs to a news article on the news_website_url,
        retrieves the full content of the news article, and returns it as a News object.

        Args:
            url: The URL of the news article to be fetched and parsed

        Returns:
            A News object containing the title, URL, time, and content of the news article

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        return NotImplemented

    def validate_and_parse(self, url: AnyHttpUrl | str) -> News:
        """Validate URL domain and parse news content.

        Validates that the provided URL belongs to the news website or its child URLs.
        If valid, proceeds with parsing the news content by invoking the parse method.

        Args:
            url: The URL of the news article to be validated and parsed

        Returns:
            A News object containing the parsed news details

        Raises:
            DomainMismatchException: If the URL does not belong to the allowed domain or child URLs
        """
        if not self._is_valid_url(url):
            raise DomainMismatchException(url)
        return self.parse(url)

    @staticmethod
    @abc.abstractmethod
    def save(news: News, db: Session | None):
        """Save news content to persistent storage.

        This method takes a News object and saves it to a persistent storage,
        such as a database. The method should handle the storage of the news content,
        ensuring that duplicate news articles are not saved.

        Args:
            news: A News object containing the title, URL, time, and content of the news article
            db: An instance of the database session to use for saving the news content

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        return NotImplemented

    def _is_valid_url(self, url: AnyHttpUrl | str) -> bool:
        """Check if the given URL belongs to the news website or its child URLs.

        Uses tldextract to compare the registered domain of the URL with the main
        news website domain.

        Args:
            url: The URL to be checked for validity

        Returns:
            True if the URL is valid, False otherwise
        """
        main_domain = tldextract.extract(str(self.news_website_url)).registered_domain
        url_domain = tldextract.extract(str(url)).registered_domain

        if url_domain == main_domain:
            return True
        return False
