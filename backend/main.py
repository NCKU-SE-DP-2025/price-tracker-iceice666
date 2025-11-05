"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import SessionLocal, init_db
from src.repositories.news_repository import NewsRepository
from src.routes import news_router, prices_router, users_router
from src.services.ai_service import AIService
from src.services.news_service import NewsService
from src.utils.web_scraper import WebScraper

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Sentry if DSN is provided
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
    )
    logger.info("Sentry initialized")


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


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan: startup and shutdown events."""

    # ============================== #
    #             STARTUP            #
    # ============================== #

    # Startup
    logger.info("Starting application...")

    # Initialize database
    init_db()

    # Fetch initial news if database is empty (only if OpenAI is configured)
    if settings.openai_api_key:
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

        # Start background scheduler for news fetching
        background_scheduler = BackgroundScheduler()
        background_scheduler.add_job(
            scheduled_news_fetch,
            "interval",
            minutes=settings.news_fetch_interval_minutes,
        )
        background_scheduler.start()
        logger.info(
            f"Background scheduler started (interval: {settings.news_fetch_interval_minutes} minutes)"
        )

        # Store scheduler in app state for access if needed
        fastapi_app.state.scheduler = background_scheduler
    else:
        logger.warning(
            "OpenAI API key not configured. AI-powered features (news summarization, search) are disabled."
        )
        fastapi_app.state.scheduler = None

    yield

    # =============================== #
    #             SHUTDOWN            #
    # =============================== #

    # Shutdown
    logger.info("Shutting down application...")
    if fastapi_app.state.scheduler:
        fastapi_app.state.scheduler.shutdown()
        logger.info("Background scheduler stopped")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Price Tracker API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(news_router)
app.include_router(prices_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {"message": "Price Tracker API - Visit /docs for API documentation"}