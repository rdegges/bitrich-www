"""Default configuration for the BitRich application."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Baseline configuration that can be extended or overridden."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'bitrich.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'randall@bitrich.fake')

    DEFAULT_DEPOSIT_CENTS = int(os.getenv('DEFAULT_DEPOSIT_CENTS', '2000'))
    DEFAULT_LOWER_LIMIT = int(os.getenv('DEFAULT_LOWER_LIMIT', '50'))
    DEFAULT_UPPER_LIMIT = int(os.getenv('DEFAULT_UPPER_LIMIT', '50'))

    BTC_RATE_URL = os.getenv(
        'BTC_RATE_URL',
        'https://api.coindesk.com/v1/bpi/currentprice/USD.json',
    )
