# BITRICH

## *Note: This is still satire. Please do not invest real money with BitRich.*

BitRich is a tongue-in-cheek micro-investment dashboard that lets you “invest” a
fixed dollar amount into Bitcoin, set basic guard rails, and watch what would
have happened. The original demo depended on Python 2, Stormpath, and very old
versions of Flask. The project has been modernized to run on Python 3.11+ with
Flask 3, SQLAlchemy, and contemporary tooling.

## Features

- Email/password authentication backed by Flask-Login + SQLAlchemy
- SQLite database storage with auto-provisioning
- Stripe Checkout integration (optional) for demo charges
- SendGrid-powered notification hooks (optional; gracefully degrade if no key)
- CLI command to check investments against price thresholds

## Requirements

- Python 3.11 or newer
- Optional: Stripe API keys for real payment flows
- Optional: SendGrid API key for transactional email

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python bootstrap.py   # writes .env with your secrets
flask --app app run --debug
```

The SQLite database (`bitrich.db`) is created automatically on first run. When
running via Gunicorn/WSGI the exported `app` object in `app.py` is used.

## Environment Variables

`bootstrap.py` can generate a `.env`, but you can also set vars manually:

| Variable                 | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `SECRET_KEY`             | Flask session key                               |
| `DATABASE_URL`           | Any SQLAlchemy-compatible URI (defaults SQLite) |
| `STRIPE_SECRET_KEY`      | Live/test secret for charging cards             |
| `STRIPE_PUBLISHABLE_KEY` | Used by Stripe Checkout widget                  |
| `SENDGRID_API_KEY`       | Used for transactional email                    |
| `SENDGRID_FROM_EMAIL`    | From address for email                          |

Use `pip install python-dotenv` or `flask run`’s built-in dotenv support to
load the `.env` file automatically.

## CLI

The legacy `manage.py` script has been replaced with a standard Flask CLI
command:

```bash
flask --app app sell-or-not
```

This recomputes investment performance using the latest BTC price and sends
emails when lower/upper limits have been crossed.
