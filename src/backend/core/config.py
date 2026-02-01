from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Security
    DESKTOP_PASSWORD: str = "Genesis_777"
    MOBILE_PATTERN: str = "Z"

    # Ritual
    KNOCK_TIMEOUT: float = 2.0
    REQUIRED_KNOCKS: int = 3

    # Device
    DEFAULT_DEVICE: str = "DESKTOP"

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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
