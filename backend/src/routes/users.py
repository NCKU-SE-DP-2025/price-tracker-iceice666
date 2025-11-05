"""User-related API endpoints."""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.config import settings
from src.models.database import User
from src.schemas.user import Token, UserAuth, UserResponse
from src.services.auth_service import AuthService, create_access_token
from src.utils.dependencies import get_auth_service, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserAuth,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user.

    Args:
        user_data: User registration data
        auth_service: Authentication service

    Returns:
        User response with username

    Raises:
        HTTPException: If username already exists
    """
    user = auth_service.register_user(user_data.username, user_data.password)
    return UserResponse(username=user.username)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Login and get access token.

    Args:
        form_data: OAuth2 form data with username and password
        auth_service: Authentication service

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User response with username
    """
    return UserResponse(username=current_user.username)
