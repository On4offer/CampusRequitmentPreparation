from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use an absolute path so IDE/working-directory differences won't break loading.
        env_file=str(_DEFAULT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM (OpenAI-compatible)
    llm_base_url: str = "https://api.openai.com"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = 60.0

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    debug: bool = False


settings = Settings()

