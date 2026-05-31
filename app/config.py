import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    meta_verify_token: str
    meta_page_access_token: str
    meta_app_secret: str
    instagram_business_account_id: str
    public_base_url: str | None = None
    graph_api_version: str = "v22.0"

    @field_validator("meta_verify_token", "meta_page_access_token", "meta_app_secret", "instagram_business_account_id")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Required environment variable must not be empty")
        return value.strip()

    @property
    def base_url(self) -> str:
        url = self.public_base_url or os.environ.get("RENDER_EXTERNAL_URL", "")
        return url.rstrip("/")

    @property
    def messages_api_url(self) -> str:
        return f"https://graph.facebook.com/{self.graph_api_version}/me/messages"


@lru_cache
def get_settings() -> Settings:
    return Settings()
