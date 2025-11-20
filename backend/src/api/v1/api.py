"""API v1 router aggregation."""

from fastapi import APIRouter

from src.api.v1.endpoints import news, prices, users

api_router = APIRouter()

# Include all endpoint routers with prefixes
api_router.include_router(users.router, prefix="/users")
api_router.include_router(news.router, prefix="/news")
api_router.include_router(prices.router, prefix="/prices")
