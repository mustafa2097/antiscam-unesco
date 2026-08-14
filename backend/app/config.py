from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Anti-Scam Job Platform API"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/antiscam"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    cookie_secure: bool = False
    link_validation_api_url: str = ""
    link_validation_api_key: str = ""
    max_text_length: int = 10000
    max_upload_bytes: int = 5 * 1024 * 1024
    seed_user_email: str = "mustafa@antiscam.local"
    seed_user_password: str = "Mustafa#M2026"
    seed_user_full_name: str = "مصطفى محمد"


@lru_cache
def get_settings() -> Settings:
    return Settings()
