"""Global pytest configuration and fixtures."""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables before any imports
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only_not_for_production_use_32chars"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "testing"


# Crawler test fixtures
import pytest
from pydantic import AnyHttpUrl


@pytest.fixture
def mock_udn_search_html():
    """Mock HTML response for UDN search results."""
    return """
    <html>
        <body>
            <div class="story-list__news">
                <h2><a href="https://udn.com/news/story/1/12345">Test Article 1</a></h2>
            </div>
            <div class="story-list__news">
                <h2><a href="https://udn.com/news/story/1/12346">Test Article 2</a></h2>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_udn_article_html():
    """Mock HTML response for UDN article page."""
    return """
    <html>
        <head>
            <title>Test Article Title</title>
        </head>
        <body>
            <time datetime="2023-09-08T10:30:00">2023-09-08 10:30</time>
            <article>
                <p>This is the content of the test article.</p>
                <p>More content here.</p>
            </article>
        </body>
    </html>
    """


@pytest.fixture
def sample_headlines():
    """Sample headlines for testing."""
    from src.crawler.crawler_base import Headline
    return [
        Headline(title="Test Article 1", url="https://udn.com/news/story/1/12345"),
        Headline(title="Test Article 2", url="https://udn.com/news/story/1/12346"),
    ]


@pytest.fixture
def sample_news_article():
    """Sample news article for testing."""
    from src.crawler.crawler_base import News
    return News(
        title="Test Article",
        url="https://udn.com/news/story/1/12345",
        time="2023-09-08T10:30:00",
        content="This is the content of the test article."
    )
