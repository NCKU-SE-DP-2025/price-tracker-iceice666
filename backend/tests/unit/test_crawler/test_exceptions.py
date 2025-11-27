"""Unit tests for crawler custom exceptions."""
import unittest
from src.crawler.exceptions import DomainMismatchException


class TestDomainMismatchException(unittest.TestCase):
    """Test suite for DomainMismatchException."""

    def test_exception_message_contains_url(self):
        """Test that exception message contains the invalid URL."""
        invalid_url = "https://www.invalid-domain.com/article"
        exception = DomainMismatchException(invalid_url)

        error_message = str(exception)
        self.assertIn(invalid_url, error_message)

    def test_exception_inheritance(self):
        """Test that DomainMismatchException inherits from Exception."""
        exception = DomainMismatchException("https://www.invalid.com")

        self.assertIsInstance(exception, Exception)

    def test_exception_raised_with_context(self):
        """Test that exception can be raised and caught with context."""
        invalid_url = "https://www.wrong-domain.com/article"

        with self.assertRaises(DomainMismatchException) as context:
            raise DomainMismatchException(invalid_url)

        self.assertIn(invalid_url, str(context.exception))

    def test_exception_with_different_urls(self):
        """Test exception works correctly with various URL formats."""
        test_urls = [
            "https://www.example.com/page",
            "http://invalid-site.org",
            "https://wrong.domain.net/article/12345",
        ]

        for url in test_urls:
            with self.assertRaises(DomainMismatchException) as context:
                raise DomainMismatchException(url)

            self.assertIn(url, str(context.exception))

    def test_exception_message_is_informative(self):
        """Test that exception message provides useful information."""
        invalid_url = "https://www.wrong-domain.com/article"
        exception = DomainMismatchException(invalid_url)

        error_message = str(exception).lower()
        # Check that message is informative (contains key terms)
        self.assertTrue(
            any(term in error_message for term in ["domain", "url", "mismatch", "invalid"])
        )


if __name__ == '__main__':
    unittest.main()
