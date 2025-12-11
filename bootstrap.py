"""Simple helper script to create a local .env file for development."""

from __future__ import annotations

import secrets
from pathlib import Path


ENV_FILE = Path(__file__).resolve().parent / ".env"


def main() -> None:
    if ENV_FILE.exists():
        print(".env already exists. Nothing to do.")
        return

    secret_key = secrets.token_hex(32)
    ENV_FILE.write_text(
        "\n".join(
            [
                f"SECRET_KEY={secret_key}",
                "# DATABASE_URL=sqlite:///bitrich.db",
                "# EXCHANGE_RATE_URL=https://api.coindesk.com/v1/bpi/currentprice/USD.json",
            ]
        )
        + "\n"
    )
    print("Created .env with a random SECRET_KEY. Customize as needed.")
    print("Run `source .env` (or use python-dotenv) before starting the app.")


if __name__ == "__main__":
    main()
