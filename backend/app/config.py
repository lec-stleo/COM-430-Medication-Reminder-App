"""Environment-backed configuration values for the Flask application."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parents[0]
load_dotenv(PROJECT_ROOT / ".env")


class Config:  # pylint: disable=too-few-public-methods
    """Default runtime configuration for local development and tests."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "medication_reminder_v2.db")
    INSTANCE_DIR = os.getenv("INSTANCE_DIR", str(BASE_DIR / "instance"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(INSTANCE_DIR) / DATABASE_NAME))
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def database_file(cls):
        """Return the absolute SQLite database path for the current config."""
        return cls.DATABASE_PATH
