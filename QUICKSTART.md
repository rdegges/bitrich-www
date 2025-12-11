# BitRich - Quick Start Guide

This is a modernized version of the BitRich joke/demo application, now running on Python 3.10+ with Flask 3.0+ and modern best practices.

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# At minimum, set a SECRET_KEY for development
```

Example `.env` for development:
```bash
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-this
DATABASE_URL=sqlite:///bitrich.db
```

### 3. Initialize Database

```bash
flask --app manage.py init-db
```

### 4. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

## ✅ Verify Setup

Run the verification script to check your setup:

```bash
python verify_setup.py
```

## 🧪 Run Tests

```bash
pytest
```

## 📝 Create Test User

```bash
flask --app manage.py create-user
# Enter email and password when prompted
```

## 🔑 Required API Keys (for full functionality)

### Stripe (Payment Processing)
1. Sign up at https://stripe.com
2. Get your test API keys from the dashboard
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

### SendGrid (Email)
1. Sign up at https://sendgrid.com
2. Create an API key
3. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG...
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   ```

### CoinGecko (Crypto Rates)
- No API key needed! Uses free public API

## 📂 Project Structure

```
bitrich-www/
├── app/                     # Main application package
│   ├── __init__.py         # App factory
│   ├── models.py           # Database models
│   ├── forms.py            # WTForms
│   ├── routes/             # Route blueprints
│   │   ├── main.py        # Home page
│   │   ├── auth.py        # Login/Register/Logout
│   │   └── investment.py  # Dashboard and investments
│   └── utils/              # Utility functions
│       ├── crypto.py      # Cryptocurrency functions
│       ├── email.py       # Email functions
│       └── payment.py     # Payment processing
├── tests/                  # Test suite
├── templates/              # Jinja2 templates
├── static/                 # CSS, JS, images
├── config.py              # Configuration classes
├── app.py                 # Application entry point
├── manage.py              # CLI commands
├── requirements.txt       # Dependencies
└── .env                   # Environment variables (create this)
```

## 🛠️ CLI Commands

```bash
# Initialize database
flask --app manage.py init-db

# Create a user
flask --app manage.py create-user

# List all users
flask --app manage.py list-users

# Check investments and send notifications
flask --app manage.py check-investments
```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "No module named 'app'"
Make sure you're in the project root directory (`/workspace`)

### "Database is locked"
Stop any running instances of the app and try again

### "Invalid API key"
Check that your `.env` file has the correct API keys

## 📚 Documentation

- **README.md** - Full documentation
- **MODERNIZATION.md** - What changed from the 2014 version
- **QUICKSTART.md** - This file!

## ⚠️ Important Notes

1. **This is a demo/joke application** - Do not use for real investments!
2. Use Stripe **test mode** keys during development
3. The default investment amount is $20
4. Bitcoin purchases are simulated (not real transactions)
5. Keep your `.env` file secret (it's in `.gitignore`)

## 🎯 What's New vs 2014 Version

- ✅ Python 3.10+ (was Python 2.7)
- ✅ Flask 3.0+ (was Flask 0.12)
- ✅ Modern authentication (replaced Stormpath)
- ✅ Type hints throughout
- ✅ Comprehensive tests
- ✅ Better security
- ✅ Modern APIs (Stripe v7, SendGrid v6)
- ✅ Proper error handling
- ✅ CLI management commands

## 🚢 Deployment

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_...
heroku config:set SENDGRID_API_KEY=SG...
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Initialize database
heroku run flask --app manage.py init-db
```

## 📞 Support

This is an open-source demo project. For issues:
1. Check the documentation
2. Run `python verify_setup.py`
3. Check the logs
4. Review MODERNIZATION.md for changes

## 🎉 Success!

If you see the BitRich homepage at http://localhost:5000, you're all set! 

**Remember**: This is a satirical demo. Don't invest real money! 🚀
