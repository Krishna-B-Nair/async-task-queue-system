import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration settings extracted from environment variables."""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"