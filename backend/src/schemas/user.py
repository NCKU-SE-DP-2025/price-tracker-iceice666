"""Pydantic schemas for user-related API endpoints."""

from pydantic import BaseModel, Field, field_validator

from src.utils.password_validator import PasswordStrength, validate_username


class UserAuth(BaseModel):
    """Schema for user registration and authentication."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password complexity requirements.

        Args:
            v: Password value

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet complexity requirements
        """
        error = PasswordStrength.validate(v)
        if error:
            raise ValueError(error)
        return v

    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Validate username format and security.

        Args:
            v: Username value

        Returns:
            Validated username

        Raises:
            ValueError: If username format is invalid
        """
        error = validate_username(v)
        if error:
            raise ValueError(error)
        return v


class UserResponse(BaseModel):
    """Schema for user response data."""

    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str
