# BITRICH

**Note: This is a joke/demo application. Do not invest real money using Bitrich.**

A satirical Bitcoin micro-investment platform built with Flask. This is a modernized version of the original 2014 demo application, now updated with current best practices and dependencies.

## Features

- User authentication with Flask-Login
- Bitcoin investment tracking
- Stripe payment integration
- Email notifications via SendGrid
- Investment limit monitoring
- SQLite/PostgreSQL database support

## Technology Stack

- **Backend**: Flask 3.0+ with Python 3.10+
- **Database**: SQLAlchemy with Flask-Migrate
- **Authentication**: Flask-Login with bcrypt password hashing
- **Forms**: Flask-WTF with WTForms validation
- **Payments**: Stripe API
- **Email**: SendGrid API
- **Crypto Rates**: CoinGecko API (free, no key required)

## How It Works

1. **Deposit Money**: Users invest $20, which is converted to Bitcoin
2. **Set Upper & Lower Limits**: Investments can be configured with sell limits (default 50%)
3. **Sit Back and Relax**: Watch your money pile up or turn to ashes

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- A Stripe account (for payment processing)
- A SendGrid account (for emails)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/rdegges/bitrich-www.git
cd bitrich-www
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:

```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:

```bash
# Required
SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
SENDGRID_API_KEY=your_sendgrid_api_key

# Optional
FLASK_ENV=development
DATABASE_URL=sqlite:///bitrich.db
```

### Running the Application

1. Initialize the database:

```bash
flask --app manage.py init-db
```

2. Run the development server:

```bash
python app.py
```

3. Visit `http://localhost:5000` in your browser

### Management Commands

The application includes several CLI commands for management:

```bash
# Initialize database
flask --app manage.py init-db

# Create a new user
flask --app manage.py create-user

# List all users
flask --app manage.py list-users

# Check investments and send notifications
flask --app manage.py check-investments
```

## Project Structure

```
bitrich-www/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms
│   ├── routes/              # Route blueprints
│   │   ├── __init__.py
│   │   ├── main.py          # Main pages
│   │   ├── auth.py          # Authentication
│   │   └── investment.py    # Investment management
│   └── utils/               # Utility modules
│       ├── __init__.py
│       ├── crypto.py        # Cryptocurrency functions
│       ├── email.py         # Email functions
│       └── payment.py       # Payment functions
├── static/                  # Static files (CSS, JS, images)
├── templates/               # Jinja2 templates
├── config.py                # Configuration classes
├── app.py                   # Application entry point
├── manage.py                # CLI management commands
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## Deployment

### Heroku

1. Install the Heroku CLI and login:

```bash
heroku login
```

2. Create a new Heroku app:

```bash
heroku create your-app-name
```

3. Add PostgreSQL:

```bash
heroku addons:create heroku-postgresql:mini
```

4. Set environment variables:

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
heroku config:set SENDGRID_API_KEY=SG...
heroku config:set FLASK_ENV=production
```

5. Deploy:

```bash
git push heroku main
```

6. Initialize the database:

```bash
heroku run flask --app manage.py init-db
```

## API Integrations

### Stripe

Used for payment processing. Sign up at [stripe.com](https://stripe.com) and get your API keys from the dashboard.

### SendGrid

Used for transactional emails. Sign up at [sendgrid.com](https://sendgrid.com) and create an API key.

### CoinGecko

Used for Bitcoin exchange rates. No API key required for basic usage.

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 style guidelines and uses type hints throughout.

## Security Notes

- Never commit your `.env` file
- Use strong, random secret keys in production
- Always use HTTPS in production
- Keep dependencies updated
- Use Stripe test keys during development

## Changes from Original

This is a modernized version of the original 2014 BitRich demo. Major changes include:

- ✅ Python 3.10+ (was Python 2.7)
- ✅ Flask 3.0+ with app factory pattern (was Flask 0.12)
- ✅ Flask-Login + SQLAlchemy (replaced deprecated Stormpath)
- ✅ Modern Stripe API (updated from v1 to v7)
- ✅ Modern SendGrid API (updated from v0.2 to v6)
- ✅ CoinGecko API (replaced deprecated Coinbase v1 API)
- ✅ Type hints and modern Python practices
- ✅ WTForms for form validation
- ✅ Proper error handling and security
- ✅ Environment variable management with python-dotenv
- ✅ Database migrations with Flask-Migrate
- ✅ CLI management commands

## License

This project is provided as-is for educational and entertainment purposes.

## Credits

Original concept and implementation by the Stormpath team during StormHack 0x00.
Modernization by the community.

## Support

This is a joke/demo project. For educational purposes only. Do not use for real investments!
