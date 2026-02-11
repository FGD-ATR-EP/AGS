from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # OAuth 2.0
    AUTH_PROVIDER: str = "mock"
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    SECRET_KEY: str = "dev-secret-key"

    # DEEPGRAM
    DEEPGRAM_API_KEY: Optional[str] = None

    # GEMINI
    GOOGLE_API_KEY: Optional[str] = None

    # CHALLENGE MODE
    CHALLENGE_MODE_ENABLED: bool = False
    CHALLENGE_MODE_INTENSITY: float = 0.25
    CHALLENGE_MODE_SEED: int = 2026

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
