"""Pydantic schemas for user-related API endpoints."""

from pydantic import BaseModel, Field


class UserAuth(BaseModel):
    """Schema for user registration and authentication."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response data."""

    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str
