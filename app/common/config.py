import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "10"))
    DATABASE_PATH = Path(
        os.getenv("DB_PATH", "default")
    ).resolve()
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    TABLE_NAME = os.getenv("TABLE_NAME", "trades")

    def get_value_of(self, key, default=None):
        return os.getenv(key, default)
