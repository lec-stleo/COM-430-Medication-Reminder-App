import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parents[0]
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "medication_reminder.db")
    INSTANCE_DIR = os.getenv("INSTANCE_DIR", str(BASE_DIR / "instance"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(INSTANCE_DIR) / DATABASE_NAME))
    LOG_DIR = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    TESTING = os.getenv("TESTING", "false").lower() == "true"
