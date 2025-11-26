"""Unit tests for UDNCrawler implementation."""
import unittest
from unittest.mock import MagicMock, patch, Mock
import pytest
import requests

from src.crawler.udn_crawler import UDNCrawler
from src.crawler.crawler_base import Headline, News
from src.crawler.exceptions import DomainMismatchException


class TestUDNCrawler(unittest.TestCase):
    """Test suite for UDNCrawler concrete implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.crawler = UDNCrawler()

    def test_crawler_initialization(self):
        """Test UDNCrawler initializes with correct attributes."""
        self.assertEqual(self.crawler.news_website_url, "https://udn.com")
        self.assertIsInstance(self.crawler.news_website_news_child_urls, list)

    def test_udn_domain_validation(self):
        """Test that UDN domain URLs are validated correctly."""
        # Valid UDN URLs
        self.assertTrue(self.crawler._is_valid_url("https://udn.com/news/story/1/12345"))
        self.assertTrue(self.crawler._is_valid_url("https://www.udn.com/article"))

        # Invalid domains
        self.assertFalse(self.crawler._is_valid_url("https://www.cnn.com/article"))
        self.assertFalse(self.crawler._is_valid_url("https://www.bbc.com/news"))

    @patch('src.crawler.udn_crawler.requests.get')
    def test_get_headline_single_page(self, mock_get):
        """Test get_headline returns headlines for a single page."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {"title": "Test Article 1", "titleLink": "https://udn.com/news/story/1/12345"},
                {"title": "Test Article 2", "titleLink": "https://udn.com/news/story/1/12346"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Execute
        headlines = self.crawler.get_headline(search_term="test", page=1)

        # Verify
        self.assertEqual(len(headlines), 2)
        self.assertIsInstance(headlines[0], Headline)
        self.assertEqual(headlines[0].title, "Test Article 1")
        self.assertEqual(headlines[0].url, "https://udn.com/news/story/1/12345")
        self.assertEqual(headlines[1].title, "Test Article 2")

        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('params', call_args[1])
        self.assertEqual(call_args[1]['params']['page'], 1)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_get_headline_page_range(self, mock_get):
        """Test get_headline returns headlines for page range."""
        # Mock API response for multiple pages
        def mock_response_side_effect(*args, **kwargs):
            page_num = kwargs['params']['page']
            mock_resp = Mock()
            mock_resp.json.return_value = {
                "lists": [
                    {"title": f"Page {page_num} Article", "titleLink": f"https://udn.com/news/page{page_num}"}
                ]
            }
            mock_resp.raise_for_status = Mock()
            return mock_resp

        mock_get.side_effect = mock_response_side_effect

        # Execute with page range
        headlines = self.crawler.get_headline(search_term="test", page=(1, 3))

        # Verify
        self.assertEqual(len(headlines), 3)
        self.assertEqual(headlines[0].title, "Page 1 Article")
        self.assertEqual(headlines[1].title, "Page 2 Article")
        self.assertEqual(headlines[2].title, "Page 3 Article")

        # Verify API was called 3 times (pages 1, 2, 3)
        self.assertEqual(mock_get.call_count, 3)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_get_headline_empty_response(self, mock_get):
        """Test get_headline handles empty API response."""
        mock_response = Mock()
        mock_response.json.return_value = {"lists": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        headlines = self.crawler.get_headline(search_term="nonexistent", page=1)

        self.assertEqual(len(headlines), 0)
        self.assertIsInstance(headlines, list)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_get_headline_handles_missing_fields(self, mock_get):
        """Test get_headline skips items with missing title or URL."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "lists": [
                {"title": "Valid Article", "titleLink": "https://udn.com/news/1"},
                {"title": "No URL"},  # Missing titleLink
                {"titleLink": "https://udn.com/news/2"},  # Missing title
                {"title": "", "titleLink": "https://udn.com/news/3"},  # Empty title
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        headlines = self.crawler.get_headline(search_term="test", page=1)

        # Only the valid article should be included
        self.assertEqual(len(headlines), 1)
        self.assertEqual(headlines[0].title, "Valid Article")

    @patch('src.crawler.udn_crawler.requests.get')
    def test_get_headline_raises_on_request_error(self, mock_get):
        """Test get_headline raises exception on API error."""
        mock_get.side_effect = requests.RequestException("API Error")

        with self.assertRaises(requests.RequestException):
            self.crawler.get_headline(search_term="test", page=1)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_parse_valid_article(self, mock_get):
        """Test parse extracts article content correctly."""
        # Mock HTML response matching UDN structure
        mock_html = """
        <html>
            <head><title>Test Article Title</title></head>
            <body>
                <h1 class="article-content__title">Test Article Title</h1>
                <time class="article-content__time">2023-09-08 10:30</time>
                <section class="article-content__editor">
                    <p>First paragraph of content.</p>
                    <p>Second paragraph of content.</p>
                </section>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Execute
        news = self.crawler.parse("https://udn.com/news/story/1/12345")

        # Verify
        self.assertIsInstance(news, News)
        self.assertEqual(news.url, "https://udn.com/news/story/1/12345")
        self.assertIn("Test Article Title", news.title)
        self.assertIsNotNone(news.time)
        self.assertIn("First paragraph", news.content)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_parse_raises_on_request_error(self, mock_get):
        """Test parse raises exception on HTTP error."""
        mock_get.side_effect = requests.RequestException("HTTP Error")

        with self.assertRaises(requests.RequestException):
            self.crawler.parse("https://udn.com/news/story/1/12345")

    def test_validate_and_parse_raises_for_invalid_domain(self):
        """Test validate_and_parse raises DomainMismatchException for invalid domain."""
        invalid_url = "https://www.cnn.com/article"

        with self.assertRaises(DomainMismatchException):
            self.crawler.validate_and_parse(invalid_url)

    @patch('src.crawler.udn_crawler.requests.get')
    def test_validate_and_parse_success(self, mock_get):
        """Test validate_and_parse successfully parses valid UDN URL."""
        mock_html = """
        <html>
            <head><title>Valid Article</title></head>
            <body>
                <h1 class="article-content__title">Valid Article</h1>
                <time class="article-content__time">2023-09-08 10:30</time>
                <section class="article-content__editor">
                    <p>Content paragraph.</p>
                </section>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        news = self.crawler.validate_and_parse("https://udn.com/news/story/1/12345")

        self.assertIsInstance(news, News)
        self.assertEqual(news.url, "https://udn.com/news/story/1/12345")


class TestUDNCrawlerSave(unittest.TestCase):
    """Test suite for UDNCrawler save functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.crawler = UDNCrawler()
        self.sample_news = News(
            title="Test Article",
            url="https://udn.com/news/story/1/12345",
            time="2023-09-08T10:30:00",
            content="This is test content."
        )

    @patch('src.crawler.udn_crawler.Session')
    def test_save_with_mock_db(self, mock_session):
        """Test save method with mocked database session."""
        mock_db = MagicMock()

        # Execute save (returns None currently as placeholder implementation)
        result = self.crawler.save(self.sample_news, mock_db)

        # Verify the method completes without error (implementation is placeholder)
        # The save method logs but doesn't return a value
        self.assertIsNone(result)

    def test_save_with_none_db(self):
        """Test save handles None database session gracefully."""
        # This should not raise an exception
        result = self.crawler.save(self.sample_news, db=None)

        # Verify method completes without error (placeholder implementation returns None)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
