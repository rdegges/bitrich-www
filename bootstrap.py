"""Interactive helper to generate a local .env file."""

from __future__ import annotations

from pathlib import Path
from secrets import token_hex

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'


def prompt(message: str, default: str = '') -> str:
    suffix = f' [{default}]' if default else ''
    value = input(f'{message}{suffix}: ').strip()
    return value or default


def main() -> None:
    print('Welcome to the BitRich bootstrap utility.')
    if ENV_PATH.exists():
        overwrite = prompt('.env already exists. Overwrite? (y/N)', 'n').lower()
        if overwrite != 'y':
            print('Aborting without changes.')
            return

    secret = prompt('SECRET_KEY', token_hex(32))
    db_default = f"sqlite:///{(BASE_DIR / 'bitrich.db').resolve()}"
    database_url = prompt('DATABASE_URL', db_default)
    stripe_secret = prompt('STRIPE_SECRET_KEY')
    stripe_publishable = prompt('STRIPE_PUBLISHABLE_KEY')
    sendgrid_key = prompt('SENDGRID_API_KEY')
    sender = prompt('SENDGRID_FROM_EMAIL', 'randall@bitrich.fake')

    contents = [
        f'SECRET_KEY={secret}',
        f'DATABASE_URL={database_url}',
        f'STRIPE_SECRET_KEY={stripe_secret}',
        f'STRIPE_PUBLISHABLE_KEY={stripe_publishable}',
        f'SENDGRID_API_KEY={sendgrid_key}',
        f'SENDGRID_FROM_EMAIL={sender}',
    ]
    ENV_PATH.write_text('\n'.join(contents) + '\n', encoding='utf-8')

    print('Wrote configuration to .env\n')
    print('Next steps:')
    print('  1. python -m venv .venv && source .venv/bin/activate')
    print('  2. pip install -r requirements.txt')
    print('  3. flask --app app run --debug')


if __name__ == '__main__':
    main()
