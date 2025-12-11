import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Application defaults that can be overridden with environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'bitrich.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXCHANGE_RATE_URL = os.environ.get(
        "EXCHANGE_RATE_URL",
        "https://api.coindesk.com/v1/bpi/currentprice/USD.json",
    )
    MIN_DEPOSIT_USD = int(os.environ.get("MIN_DEPOSIT_USD", "20"))
    MAX_DEPOSIT_USD = int(os.environ.get("MAX_DEPOSIT_USD", "10000"))
