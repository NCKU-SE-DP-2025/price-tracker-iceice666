"""Unit tests for NewsCrawlerBase abstract class."""
import unittest
from unittest.mock import MagicMock
from pydantic import AnyHttpUrl, ValidationError
import pytest

from src.crawler.crawler_base import NewsCrawlerBase, News, Headline, NewsWithSummary
from src.crawler.exceptions import DomainMismatchException


class MockNewsCrawler(NewsCrawlerBase):
    """Mock implementation of NewsCrawlerBase for testing."""

    news_website_url = "https://www.example.com"
    news_website_news_child_urls = ["https://news.example.com"]

    def get_headline(self, search_term: str, page: int | tuple[int, int]):
        """Mock implementation returning sample headlines."""
        return [Headline(title="Test Article", url="https://www.example.com/article")]

    def parse(self, url: AnyHttpUrl | str):
        """Mock implementation returning sample news."""
        return News(
            title="Test Article",
            url=url,
            time="2023-09-08T00:00:00",
            content="This is the content of the article."
        )

    @staticmethod
    def save(news: News, db=None):
        """Mock implementation always returns True."""
        return True


class TestNewsCrawlerBase(unittest.TestCase):
    """Test suite for NewsCrawlerBase abstract class."""

    def setUp(self):
        """Set up test fixtures."""
        self.crawler = MockNewsCrawler()

    def test_is_valid_url_valid(self):
        """Test that valid main domain URL passes validation."""
        valid_url = "https://www.example.com/article"
        self.assertTrue(self.crawler._is_valid_url(valid_url))

    def test_is_valid_url_invalid(self):
        """Test that invalid domain URL fails validation."""
        invalid_url = "https://www.invalid.com/article"
        self.assertFalse(self.crawler._is_valid_url(invalid_url))

    def test_is_valid_url_child(self):
        """Test that child domain URL passes validation."""
        valid_child_url = "https://news.example.com/article"
        self.assertTrue(self.crawler._is_valid_url(valid_child_url))

    def test_validate_and_parse_raises_domain_mismatch(self):
        """Test that DomainMismatchException is raised for invalid URL."""
        invalid_url = "https://www.invalid.com/article"

        with self.assertRaises(DomainMismatchException):
            self.crawler.validate_and_parse(invalid_url)

    def test_validate_and_parse_success(self):
        """Test successful validation and parsing of valid URL."""
        valid_url = "https://www.example.com/article"
        news = self.crawler.validate_and_parse(valid_url)

        self.assertIsInstance(news, News)
        self.assertEqual(news.title, "Test Article")
        self.assertEqual(news.url, valid_url)
        self.assertEqual(news.time, "2023-09-08T00:00:00")
        self.assertEqual(news.content, "This is the content of the article.")

    def test_get_headline(self):
        """Test get_headline returns list of headlines."""
        headlines = self.crawler.get_headline(search_term="test", page=1)

        self.assertEqual(len(headlines), 1)
        self.assertIsInstance(headlines[0], Headline)
        self.assertEqual(headlines[0].title, "Test Article")
        self.assertEqual(headlines[0].url, "https://www.example.com/article")

    def test_parse(self):
        """Test parse returns News object with correct fields."""
        news = self.crawler.parse("https://www.example.com/article")

        self.assertIsInstance(news, News)
        self.assertEqual(news.title, "Test Article")
        self.assertEqual(news.url, "https://www.example.com/article")
        self.assertEqual(news.time, "2023-09-08T00:00:00")
        self.assertEqual(news.content, "This is the content of the article.")

    def test_save(self):
        """Test save method returns True."""
        news = News(
            title="Test Article",
            url="https://www.example.com/article",
            time="2023-09-08T00:00:00",
            content="This is the content of the article."
        )
        result = self.crawler.save(news, None)
        self.assertTrue(result)

    def test_abstract_methods_not_implemented(self):
        """Test that NewsCrawlerBase cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            # This should fail because NewsCrawlerBase has abstract methods
            NewsCrawlerBase()


class TestPydanticModels(unittest.TestCase):
    """Test suite for Pydantic models (Headline, News, NewsWithSummary)."""

    def test_headline_valid(self):
        """Test valid Headline creation."""
        headline = Headline(
            title="Test Title",
            url="https://www.example.com/article"
        )
        self.assertEqual(headline.title, "Test Title")
        self.assertEqual(str(headline.url), "https://www.example.com/article")

    def test_headline_missing_title(self):
        """Test that missing required field raises ValidationError."""
        # Test missing title field
        with self.assertRaises(ValidationError):
            Headline(url="https://www.example.com/article")

    def test_news_valid(self):
        """Test valid News creation."""
        news = News(
            title="Test Article",
            url="https://www.example.com/article",
            time="2023-09-08T00:00:00",
            content="Article content"
        )
        self.assertEqual(news.title, "Test Article")
        self.assertEqual(str(news.url), "https://www.example.com/article")
        self.assertEqual(news.time, "2023-09-08T00:00:00")
        self.assertEqual(news.content, "Article content")

    def test_news_inherits_from_headline(self):
        """Test that News inherits from Headline."""
        news = News(
            title="Test Article",
            url="https://www.example.com/article",
            time="2023-09-08T00:00:00",
            content="Article content"
        )
        self.assertIsInstance(news, Headline)

    def test_news_with_summary_valid(self):
        """Test valid NewsWithSummary creation."""
        news_with_summary = NewsWithSummary(
            title="Test Article",
            url="https://www.example.com/article",
            time="2023-09-08T00:00:00",
            content="Article content",
            summary="Article summary",
            reason="Reason for selection"
        )
        self.assertEqual(news_with_summary.title, "Test Article")
        self.assertEqual(news_with_summary.summary, "Article summary")
        self.assertEqual(news_with_summary.reason, "Reason for selection")

    def test_news_with_summary_inherits_from_news(self):
        """Test that NewsWithSummary inherits from News."""
        news_with_summary = NewsWithSummary(
            title="Test Article",
            url="https://www.example.com/article",
            time="2023-09-08T00:00:00",
            content="Article content",
            summary="Article summary",
            reason="Reason for selection"
        )
        self.assertIsInstance(news_with_summary, News)
        self.assertIsInstance(news_with_summary, Headline)

    def test_news_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with self.assertRaises(ValidationError):
            News(title="Test Article", url="https://www.example.com/article")
            # Missing time and content


if __name__ == '__main__':
    unittest.main()
