"""Global pytest configuration and fixtures."""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment variables before any imports
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only_not_for_production_use_32chars"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENVIRONMENT"] = "testing"
