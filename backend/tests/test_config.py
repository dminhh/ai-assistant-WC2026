import pytest
from app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear lru_cache between tests to avoid stale settings."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("FOOTBALL_DATA_API_KEY", "fd_test_key")
    monkeypatch.setenv("API_FOOTBALL_KEY", "af_test_key")
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-that-is-long-enough")
    monkeypatch.setenv("JWT_EXPIRE_DAYS", "7")

    settings = get_settings()
    assert settings.football_data_api_key == "fd_test_key"
    assert settings.jwt_expire_days == 7
