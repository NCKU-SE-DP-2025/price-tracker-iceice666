"""Request ID tracking middleware for distributed tracing and debugging."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each HTTP request for tracing and debugging.

    Benefits:
    - Correlate logs across distributed systems
    - Track request flow through application
    - Debug production issues with specific request IDs
    - Support for distributed tracing (OpenTelemetry, etc.)
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add unique request ID.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with X-Request-ID header
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store in request state for access in handlers/logs
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
