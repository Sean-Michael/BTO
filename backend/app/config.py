from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BTO_", env_file=".env")

    # Directory holding the built frontend (dist/). Served as static files in
    # production. When unset or missing, the API runs without a UI (dev mode
    # uses the Vite dev server instead).
    static_dir: Path | None = None

    # CORS origins allowed in development (Vite dev server).
    cors_origins: list[str] = ["http://localhost:5173"]

    # Seconds to cache NOAA prediction responses in-memory.
    cache_ttl: int = 900


@lru_cache
def get_settings() -> Settings:
    return Settings()
