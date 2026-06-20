"""Root conftest.py — sets required environment variables before any app modules
are imported (needed because app/database.py calls get_settings() at import time).
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/wc2026_test")
os.environ.setdefault("FOOTBALL_DATA_API_KEY", "test_fd_key")
os.environ.setdefault("API_FOOTBALL_KEY", "test_af_key")
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-32chars")
os.environ.setdefault("JWT_EXPIRE_DAYS", "7")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
