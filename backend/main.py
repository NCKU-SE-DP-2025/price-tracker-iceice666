"""Main application entry point.

This module serves as the root entry point for uvicorn/deployment tools
that expect 'main:app' while keeping the actual application logic in src/.

For development: uvicorn main:app --reload
For production: uvicorn main:app --host 0.0.0.0 --port 8000
Alternative: uvicorn src.main:app (if PYTHONPATH includes backend/)
"""

from src.main import app

__all__ = ["app"]
