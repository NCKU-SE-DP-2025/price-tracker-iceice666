"""Main FastAPI application."""

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.api.v1.api import api_router
from src.config import settings
from src.core.lifespan import lifespan
from src.core.logging import setup_logging
from src.middleware.security_headers import SecurityHeadersMiddleware
from src.middleware.request_id import RequestIDMiddleware

# Configure logging
setup_logging()

# Initialize Sentry if DSN is provided
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
    )

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app with lifespan
app = FastAPI(
    title="Price Tracker API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Middleware (order matters - applied in reverse)
# 1. Security headers (applied last, affects all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request ID tracking
app.add_middleware(RequestIDMiddleware)

# 3. HTTPS enforcement (production only)
if settings.environment == "production":
    # Redirect HTTP to HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)

    # Prevent host header injection attacks
    # Configure via TRUSTED_HOSTS environment variable (comma-separated domains)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts
    )

# 4. CORS Configuration (restrictive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    # Restrict to necessary HTTP methods only
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    # Restrict to necessary headers only
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Request-ID",
    ],
    # Cache preflight requests for 1 hour
    max_age=3600,
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
