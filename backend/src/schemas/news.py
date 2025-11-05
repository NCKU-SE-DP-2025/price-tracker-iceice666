"""Pydantic schemas for news-related API endpoints."""

from pydantic import BaseModel, Field


class NewsArticleResponse(BaseModel):
    """Schema for news article response."""

    id: int
    url: str
    title: str
    time: str
    content: str
    summary: str
    reason: str
    upvotes: int
    is_upvoted: bool

    class Config:
        from_attributes = True


class PromptRequest(BaseModel):
    """Schema for news search prompt request."""

    prompt: str = Field(..., min_length=1)


class SearchNewsResponse(BaseModel):
    """Schema for searched news article response."""

    id: int
    url: str
    title: str
    time: str
    content: str


class NewsSummaryRequest(BaseModel):
    """Schema for news summary generation request."""

    content: str = Field(..., min_length=1)


class NewsSummaryResponse(BaseModel):
    """Schema for news summary generation response."""

    summary: str
    reason: str
