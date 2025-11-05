"""Repository for user database operations."""

from typing import Optional

from sqlalchemy.orm import Session

from src.models.database import User


class UserRepository:
    """Handles database operations for users."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_user(self, username: str, hashed_password: str) -> User:
        """Create a new user in the database.

        Args:
            username: Unique username
            hashed_password: Hashed password

        Returns:
            Created User instance
        """
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User instance if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def user_exists(self, username: str) -> bool:
        """Check if a user exists by username.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        return self.get_user_by_username(username) is not None
