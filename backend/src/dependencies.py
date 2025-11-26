"""FastAPI dependency injection functions."""

from functools import lru_cache
from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models.database import User
from src.repositories.news_repository import NewsRepository
from src.repositories.user_repository import UserRepository
from src.services.ai_service import AIService
from src.services.auth_service import AuthService
from src.services.news_service import NewsService
from src.services.price_service import PriceService
from src.utils.web_scraper import WebScraper

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_db() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Get user repository instance.

    Args:
        db: Database session

    Returns:
        UserRepository instance
    """
    return UserRepository(db)


def get_news_repository(db: Session = Depends(get_db)) -> NewsRepository:
    """Get news repository instance.

    Args:
        db: Database session

    Returns:
        NewsRepository instance
    """
    return NewsRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get authentication service instance.

    Args:
        user_repository: UserRepository instance

    Returns:
        AuthService instance
    """
    return AuthService(user_repository)


@lru_cache()
def get_ai_service() -> AIService:
    """Get AI service instance (singleton).

    Returns:
        AIService instance (cached)
    """
    return AIService()


@lru_cache()
def get_web_scraper() -> WebScraper:
    """Get web scraper instance (singleton).

    Returns:
        WebScraper instance (cached)
    """
    return WebScraper()


def get_news_service(
    news_repository: NewsRepository = Depends(get_news_repository),
    ai_service: AIService = Depends(get_ai_service),
) -> NewsService:
    """Get news service instance.

    Args:
        news_repository: NewsRepository instance
        ai_service: AIService instance

    Returns:
        NewsService instance
    """
    return NewsService(news_repository, ai_service)


def get_price_service() -> PriceService:
    """Get price service instance.

    Returns:
        PriceService instance
    """
    return PriceService()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current authenticated user.

    Args:
        token: JWT token from request
        auth_service: AuthService instance

    Returns:
        Current User instance

    Raises:
        HTTPException: If authentication fails
    """
    return auth_service.get_current_user(token)
