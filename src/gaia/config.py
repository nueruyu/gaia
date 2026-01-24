from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    LLM_MODE: Literal["MOCK", "GEMINI"] = "GEMINI"
    DB_PATH: str = ".local/gaia.db"
