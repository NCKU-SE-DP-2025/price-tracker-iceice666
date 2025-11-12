"""Security headers middleware for defense-in-depth protection."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add comprehensive security headers to all HTTP responses.

    Implements defense-in-depth security through browser-level protections:
    - Clickjacking prevention (X-Frame-Options)
    - MIME type sniffing prevention (X-Content-Type-Options)
    - XSS filtering for legacy browsers (X-XSS-Protection)
    - Content Security Policy (CSP) for modern browsers
    - Referrer policy for privacy
    - Permissions policy to disable unnecessary features
    - HSTS for HTTPS enforcement (production only)
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with security headers added
        """
        response: Response = await call_next(request)

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS filtering (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy (strict configuration)
        # Adjust based on actual frontend requirements
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "  # unsafe-inline needed for some frameworks
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Referrer policy for privacy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (disable unnecessary browser features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=()"
        )

        # HSTS (HTTP Strict Transport Security) - only for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
