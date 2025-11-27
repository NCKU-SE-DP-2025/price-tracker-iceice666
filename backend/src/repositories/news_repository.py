"""Repository for news article database operations."""

from typing import Optional

from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from src.models.database import NewsArticle, user_news_association_table


class NewsRepository:
    """Handles database operations for news articles."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_news_article(
        self,
        url: str,
        title: str,
        time: str,
        content: str,
        summary: str,
        reason: str,
    ) -> NewsArticle:
        """Create a new news article in the database.

        Args:
            url: Article URL (must be unique)
            title: Article title
            time: Publication time
            content: Article content
            summary: AI-generated summary
            reason: AI-generated reason

        Returns:
            Created NewsArticle instance
        """
        news_article = NewsArticle(
            url=url,
            title=title,
            time=time,
            content=content,
            summary=summary,
            reason=reason,
        )
        self.db.add(news_article)
        self.db.commit()
        self.db.refresh(news_article)
        return news_article

    def get_all_news(
        self, skip: int = 0, limit: int = 100
    ) -> list[NewsArticle]:
        """Get news articles ordered by time (descending) with pagination.

        Args:
            skip: Number of articles to skip (for pagination)
            limit: Maximum number of articles to return (default 100)

        Returns:
            List of NewsArticle instances
        """
        return (
            self.db.query(NewsArticle)
            .order_by(NewsArticle.time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_news_by_id(self, news_id: int) -> Optional[NewsArticle]:
        """Get a news article by ID.

        Args:
            news_id: Article ID

        Returns:
            NewsArticle instance if found, None otherwise
        """
        return self.db.query(NewsArticle).filter_by(id=news_id).first()

    def news_exists(self, news_id: int) -> bool:
        """Check if a news article exists.

        Args:
            news_id: Article ID

        Returns:
            True if article exists, False otherwise
        """
        return self.get_news_by_id(news_id) is not None

    def get_upvote_count(self, news_id: int) -> int:
        """Get the number of upvotes for a news article.

        Args:
            news_id: Article ID

        Returns:
            Number of upvotes
        """
        return (
            self.db.query(user_news_association_table)
            .filter_by(news_articles_id=news_id)
            .count()
        )

    def user_has_upvoted(self, news_id: int, user_id: int) -> bool:
        """Check if a user has upvoted a news article.

        Args:
            news_id: Article ID
            user_id: User ID

        Returns:
            True if user has upvoted, False otherwise
        """
        return (
            self.db.query(user_news_association_table)
            .filter_by(news_articles_id=news_id, user_id=user_id)
            .first()
            is not None
        )

    def add_upvote(self, news_id: int, user_id: int) -> None:
        """Add an upvote to a news article.

        Args:
            news_id: Article ID
            user_id: User ID
        """
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=news_id, user_id=user_id
        )
        self.db.execute(insert_stmt)
        self.db.commit()

    def remove_upvote(self, news_id: int, user_id: int) -> None:
        """Remove an upvote from a news article.

        Args:
            news_id: Article ID
            user_id: User ID
        """
        delete_stmt = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == news_id,
            user_news_association_table.c.user_id == user_id,
        )
        self.db.execute(delete_stmt)
        self.db.commit()

    def count_articles(self) -> int:
        """Count total number of news articles.

        Returns:
            Number of articles in database
        """
        return self.db.query(NewsArticle).count()
