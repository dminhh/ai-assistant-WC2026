# app/config.py
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    football_data_api_key: str
    api_football_key: str
    jwt_secret: str
    jwt_expire_days: int = 7
    openai_api_key: str

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("jwt_secret must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
