from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and .env files.
    """

    # This tells pydantic-settings to look for a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    LLM_MODE: Literal["MOCK", "GEMINI"] = "MOCK"
    GOOGLE_API_KEY: str | None = None
