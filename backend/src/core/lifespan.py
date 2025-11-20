"""Application lifespan management for startup and shutdown events."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.config import settings
from src.core.scheduler import create_scheduler
from src.database import SessionLocal, init_db
from src.repositories.news_repository import NewsRepository
from src.services.ai_service import AIService
from src.services.news_service import NewsService
from src.utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


def perform_initial_news_fetch() -> None:
    """Fetch initial news if database is empty and OpenAI is configured."""
    if not settings.openai_api_key:
        logger.warning(
            "OpenAI API key not configured. AI-powered features (news summarization, search) are disabled."
        )
        return

    db = SessionLocal()
    try:
        news_repository = NewsRepository(db)
        if news_repository.count_articles() == 0:
            logger.info("Database empty, fetching initial news...")
            ai_service = AIService()
            web_scraper = WebScraper()
            news_service = NewsService(news_repository, ai_service, web_scraper)
            news_service.fetch_and_process_news(is_initial=True)
    except Exception as e:
        logger.error(f"Error during initial news fetch: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan: startup and shutdown events.

    Args:
        fastapi_app: FastAPI application instance

    Yields:
        None during application runtime
    """
    # ============================== #
    #             STARTUP            #
    # ============================== #

    logger.info("Starting application...")

    # Initialize database
    init_db()

    # Fetch initial news if database is empty
    perform_initial_news_fetch()

    # Start background scheduler
    scheduler = create_scheduler()
    fastapi_app.state.scheduler = scheduler

    yield

    # =============================== #
    #             SHUTDOWN            #
    # =============================== #

    logger.info("Shutting down application...")
    if fastapi_app.state.scheduler:
        fastapi_app.state.scheduler.shutdown()
        logger.info("Background scheduler stopped")
