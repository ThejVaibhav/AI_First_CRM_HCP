"""Application configuration loaded from environment variables."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central settings object. Values are read from the .env file / environment."""

    def __init__(self) -> None:
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "postgresql://user:pass@localhost:5432/hcp_crm"
        )
        # Comma-separated list of allowed CORS origins.
        self.ALLOWED_ORIGINS: list[str] = [
            o.strip()
            for o in os.getenv(
                "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
            ).split(",")
            if o.strip()
        ]
        self.BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

        # Groq model identifiers (per BRD Section 11).
        self.PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "gemma2-9b-it")
        self.SECONDARY_MODEL: str = os.getenv(
            "SECONDARY_MODEL", "llama-3.3-70b-versatile"
        )
        self.WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "whisper-large-v3")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
