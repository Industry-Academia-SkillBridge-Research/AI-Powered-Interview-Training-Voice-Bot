from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root
# env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv()


class Settings(BaseSettings):
    """
    Central configuration object for the application.
    Loaded once and reused everywhere.
    """

    # ========= Ollama =========
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # ========= Application =========
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # ========= Interview Settings =========
    MAX_INTERVIEW_QUESTIONS: int = int(
        os.getenv("MAX_INTERVIEW_QUESTIONS", 7)
    )

    # ========= Security (future-ready) =========
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")


# Singleton settings object
settings = Settings()
