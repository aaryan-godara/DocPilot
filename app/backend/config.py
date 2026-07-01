"""
DocPilot — Application Configuration

Centralized settings management using pydantic-settings.
Reads from environment variables and .env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (two levels up from this file)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Reads from a .env file if present. All settings can be overridden
    via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "DocPilot"
    app_version: str = "0.1.0"
    debug: bool = False

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # --- Paths ---
    upload_dir: str = "data/raw"
    processed_dir: str = "data/processed"

    # --- Logging ---
    log_level: str = "INFO"

    # --- Chunking (Week 2+) ---
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # --- OpenAI (Week 2+) ---
    openai_api_key: Optional[str] = None

    # --- ChromaDB (Week 3+) ---
    chroma_persist_dir: str = "data/processed/chroma"

    @property
    def upload_path(self) -> Path:
        """Resolve the upload directory as an absolute path."""
        path = PROJECT_ROOT / self.upload_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def processed_path(self) -> Path:
        """Resolve the processed data directory as an absolute path."""
        path = PROJECT_ROOT / self.processed_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached singleton of the application settings.

    Using lru_cache ensures the .env file is read only once.
    """
    return Settings()
