"""Main FastAPI application."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.config import settings
from src.core.lifespan import lifespan
from src.core.logging import setup_logging

# Configure logging
setup_logging()

# Initialize Sentry if DSN is provided
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
    )

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

# Include API router with prefix
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {"message": "Price Tracker API - Visit /docs for API documentation"}
