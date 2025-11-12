"""Background scheduler for periodic tasks."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from src.config import settings
from src.database import SessionLocal
from src.repositories.news_repository import NewsRepository
from src.services.ai_service import AIService
from src.services.news_service import NewsService
from src.utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


def scheduled_news_fetch() -> None:
    """Fetch news periodically in background."""
    if not settings.openai_api_key:
        logger.warning("Skipping scheduled news fetch: OpenAI API key not configured")
        return

    logger.info("Starting scheduled news fetch")
    db = SessionLocal()
    try:
        news_repository = NewsRepository(db)
        ai_service = AIService()
        web_scraper = WebScraper()
        news_service = NewsService(news_repository, ai_service, web_scraper)
        news_service.fetch_and_process_news(is_initial=False)
    except Exception as e:
        logger.error(f"Error in scheduled news fetch: {e}")
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler | None:
    """Create and configure background scheduler.

    Returns:
        BackgroundScheduler instance if OpenAI is configured, None otherwise
    """
    if not settings.openai_api_key:
        logger.warning(
            "OpenAI API key not configured. Background scheduler will not be started."
        )
        return None

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scheduled_news_fetch,
        "interval",
        minutes=settings.news_fetch_interval_minutes,
    )
    scheduler.start()
    logger.info(
        f"Background scheduler started (interval: {settings.news_fetch_interval_minutes} minutes)"
    )
    return scheduler
