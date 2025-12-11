# BitRich 🪙

> **⚠️ DISCLAIMER: This is a joke application. Do not invest real money!**

A modern Flask web application for Bitcoin micro-investments. Built with Flask 3.0+, Bootstrap 5, and modern Python practices.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![Bootstrap](https://img.shields.io/badge/bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## Features

- 🔐 **User Authentication** - Secure login/registration with Flask-Login
- 💳 **Payment Processing** - Stripe integration for payments
- 📈 **Bitcoin Tracking** - Real-time BTC exchange rates via CoinGecko API
- 📧 **Email Notifications** - SendGrid integration for transactional emails
- 🎨 **Modern UI** - Responsive Bootstrap 5 design
- 🗄️ **SQLite/PostgreSQL** - Flexible database support via SQLAlchemy

## How It Works

1. **Deposit Money** - Make a $20 micro-investment
2. **Set Limits** - Configure upper and lower sell thresholds (default: 50%)
3. **Sit Back** - We notify you when limits are reached

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bitrich-www.git
   cd bitrich-www
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the bootstrap script** (optional - helps configure environment)
   ```bash
   python bootstrap.py
   ```

   Or manually create a `.env` file:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   
   # Database
   DATABASE_URL=sqlite:///bitrich.db
   
   # Stripe (get keys from https://stripe.com)
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   
   # SendGrid (get key from https://sendgrid.com)
   SENDGRID_API_KEY=SG...
   DEFAULT_FROM_EMAIL=noreply@example.com
   ```

5. **Initialize the database**
   ```bash
   flask init-db
   ```

6. **Run the development server**
   ```bash
   flask run
   ```

7. **Visit** http://localhost:5000

## CLI Commands

```bash
# Database management
flask init-db          # Initialize database tables
flask drop-db          # Drop all tables

# User management  
flask list-users                    # List all users
flask create-user EMAIL PASSWORD    # Create a new user

# Investment monitoring
flask sell-or-not      # Check investments and send notifications
```

## Project Structure

```
bitrich-www/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── manage.py           # CLI commands
├── bootstrap.py        # Setup script
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   ├── images/        # Static images
│   └── fonts/         # Web fonts
└── templates/
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── login.html     # Login page
    ├── register.html  # Registration page
    ├── dashboard.html # User dashboard
    └── email/         # Email templates
```

## Configuration

The application uses environment variables for configuration. See `config.py` for all available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Flask secret key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///bitrich.db` |
| `STRIPE_SECRET_KEY` | Stripe secret key | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - |
| `SENDGRID_API_KEY` | SendGrid API key | - |

## Production Deployment

For production:

1. Set `FLASK_ENV=production`
2. Use a strong `SECRET_KEY`
3. Use PostgreSQL instead of SQLite
4. Run with gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

## Technology Stack

- **Backend**: Flask 3.0+, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Payments**: Stripe
- **Email**: SendGrid
- **HTTP Client**: HTTPX

## Modernization Changes

This codebase was modernized from Python 2 to Python 3.10+ with:

- ✅ Python 3 syntax (f-strings, type hints, modern exception handling)
- ✅ Flask 3.0+ with modern patterns
- ✅ Replaced deprecated Flask-Stormpath with Flask-Login + SQLAlchemy
- ✅ Replaced Flask-Script with Flask CLI (Click)
- ✅ Updated SendGrid to v6+ API
- ✅ Modern Stripe API
- ✅ Bootstrap 5 (from Bootstrap 3)
- ✅ HTTPS for all external resources
- ✅ CSRF protection with Flask-WTF
- ✅ Proper configuration management
- ✅ Modern responsive email templates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational/entertainment purposes only. See [LICENSE](LICENSE) for details.

---

**Remember: This is a joke! Do not invest real money! 😄**
