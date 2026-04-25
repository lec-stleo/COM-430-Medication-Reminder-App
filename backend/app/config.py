"""Environment-backed configuration values for the Flask application."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parents[0]
load_dotenv(PROJECT_ROOT / ".env")


class Config:  # pylint: disable=too-few-public-methods
    """Default runtime configuration for local development and tests."""

    # These defaults keep the app runnable from a fresh clone while still letting
    # environment variables override paths and runtime behavior when needed.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "medication_reminder.db")
    INSTANCE_DIR = os.getenv("INSTANCE_DIR", str(BASE_DIR / "instance"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(INSTANCE_DIR) / DATABASE_NAME))
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", "3600"))

    @classmethod
    def database_file(cls):
        """Return the absolute SQLite database path for the current config."""
        return cls.DATABASE_PATH
