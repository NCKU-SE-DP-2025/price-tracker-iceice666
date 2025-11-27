"""Authentication service for user management and JWT tokens."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

from src.config import settings
from src.models.database import User
from src.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


def create_access_token(
        data: dict[str, str], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in token (typically {'sub': username})
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token

    Raises:
        HTTPException: If JWT_SECRET_KEY is not configured
    """
    if not settings.jwt_secret_key:
        logger.error("JWT_SECRET_KEY not configured - cannot create access token")
        raise HTTPException(
            status_code=500,
            detail="Authentication is not properly configured. Please set JWT_SECRET_KEY in .env file"
        )

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update([("exp", expire)])
    # Security: Don't log token expiry time to prevent timing attacks
    logger.info("Access token created successfully")
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> str:
    """Decode a JWT token and extract username.

    Args:
        token: JWT token

    Returns:
        Username from token

    Raises:
        HTTPException: If token is invalid, expired, or JWT_SECRET_KEY is not configured
    """
    if not settings.jwt_secret_key:
        logger.error("JWT_SECRET_KEY not configured - cannot decode token")
        raise HTTPException(
            status_code=500,
            detail="Authentication is not properly configured. Please set JWT_SECRET_KEY in .env file"
        )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.error("Token payload missing 'sub' field")
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e


class AuthService:
    """Handles user authentication and JWT token management."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize authentication service.

        Args:
            user_repository: UserRepository instance for database operations
        """
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a plain text password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def register_user(self, username: str, password: str) -> User:
        """Register a new user.

        Args:
            username: Unique username
            password: Plain text password

        Returns:
            Created User instance

        Raises:
            HTTPException: If username already exists
        """
        if self.user_repository.user_exists(username):
            # Security: Don't log username to prevent enumeration attacks
            logger.warning("Registration attempt with existing username")
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = self.hash_password(password)
        user = self.user_repository.create_user(username, hashed_password)
        # Security: Don't log username to prevent information disclosure
        logger.info("User registration completed successfully")
        return user

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate a user by username and password.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User instance if authentication successful

        Raises:
            HTTPException: If credentials are invalid
        """
        user = self.user_repository.get_user_by_username(username)
        if not user:
            # Security: Generic message prevents username enumeration
            logger.warning("Authentication attempt failed")
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not self.verify_password(password, user.hashed_password):
            # Security: Generic message prevents username enumeration
            logger.warning("Authentication attempt failed")
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Security: Don't log username to prevent information disclosure
        logger.info("User authentication successful")
        return user

    def get_current_user(self, token: str) -> User:
        """Get current user from JWT token.

        Args:
            token: JWT token

        Returns:
            User instance

        Raises:
            HTTPException: If token is invalid or user not found
        """
        username = decode_token(token)
        user = self.user_repository.get_user_by_username(username)
        if not user:
            # Security: Don't log username to prevent information disclosure
            logger.error("User from token not found in database")
            raise HTTPException(status_code=401, detail="User not found")
        return user
