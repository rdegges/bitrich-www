"""
BitRich Web Application
~~~~~~~~~~~~~~~~~~~~~~~

A modern Flask application for Bitcoin micro-investments.
Note: This is a joke application. Do not invest real money.
"""

from datetime import datetime
from functools import wraps
import json
import os
from uuid import uuid4

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

import httpx
import stripe
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from config import get_config


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect(app)

# Initialize Stripe
stripe.api_key = app.config['STRIPE_SECRET_KEY']


# Database Models
class User(UserMixin, db.Model):
    """User model for authentication and data storage."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    given_name = db.Column(db.String(100), default='')
    surname = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to investments
    investments = db.relationship('Investment', backref='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Investment(db.Model):
    """Investment model for tracking user investments."""
    
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deposit_amount_usd = db.Column(db.Integer, nullable=False)  # in cents
    deposit_amount_bitcoin = db.Column(db.Float, nullable=False)
    lower_limit = db.Column(db.Integer, default=50)  # percentage
    upper_limit = db.Column(db.Integer, default=50)  # percentage
    current_value = db.Column(db.Float, default=0.0)
    
    def __repr__(self) -> str:
        return f'<Investment {self.uuid}>'
    
    def to_dict(self) -> dict:
        """Convert investment to dictionary for template rendering."""
        return {
            'id': self.uuid,
            'created': self.created_at.isoformat(),
            'updated': self.updated_at.isoformat(),
            'deposit_amount_usd': self.deposit_amount_usd,
            'deposit_amount_bitcoin': self.deposit_amount_bitcoin,
            'lower_limit': self.lower_limit,
            'upper_limit': self.upper_limit,
            'current_value': self.current_value,
        }


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Load user by ID for Flask-Login."""
    return db.session.get(User, int(user_id))


# Helper functions
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using SendGrid."""
    api_key = app.config.get('SENDGRID_API_KEY')
    if not api_key:
        app.logger.warning("SendGrid API key not configured")
        return False
    
    try:
        sg = SendGridAPIClient(api_key)
        from_email = Email(app.config.get('DEFAULT_FROM_EMAIL'))
        to_email = To(to_email)
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        sg.send(mail)
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        return False


def get_bitcoin_rate() -> float:
    """Get current USD to BTC exchange rate."""
    try:
        # Using CoinGecko's free API as Coinbase API has changed
        response = httpx.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd'},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        usd_price = data['bitcoin']['usd']
        return 1 / usd_price  # Convert USD price to BTC per USD
    except Exception as e:
        app.logger.error(f"Failed to get Bitcoin rate: {e}")
        return 0.0


# Routes
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    
    Creates a new user account and logs them in automatically.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('register.html')
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    
    # Validation
    if not email or not password:
        return render_template('register.html', error='Email and password are required.')
    
    if len(password) < 8:
        return render_template('register.html', error='Password must be at least 8 characters.')
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return render_template('register.html', error='An account with this email already exists.')
    
    try:
        # Create new user
        user = User(email=email, given_name='User', surname='')
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        
        # Send welcome email
        html_content = render_template('email/verification_email.html', user=user)
        send_email(user.email, 'Welcome to BitRich!', html_content)
        
        flash('Welcome to BitRich! Your account has been created.', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {e}")
        return render_template('register.html', error='An error occurred during registration.')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    Validates credentials and creates a user session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    
    if not email or not password:
        return render_template('login.html', error='Email and password are required.')
    
    user = User.query.filter_by(email=email).first()
    
    if user is None or not user.check_password(password):
        return render_template('login.html', error='Invalid email or password.')
    
    login_user(user, remember=True)
    
    # Redirect to next page if provided, otherwise dashboard
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    Render the user dashboard.
    
    Shows current investments and allows new deposits.
    """
    rate = get_bitcoin_rate()
    
    total_btc = 0.0
    total_usd = 0
    
    # Calculate current values for all investments
    investments = []
    for investment in current_user.investments.all():
        total_usd += investment.deposit_amount_usd
        total_btc += investment.deposit_amount_bitcoin
        
        # Calculate current value based on Bitcoin rate
        if rate > 0:
            btc_amount = investment.deposit_amount_bitcoin
            original_usd = investment.deposit_amount_usd / 100.0
            current_btc_value = btc_amount / rate  # Current USD value of BTC
            
            if original_usd > 0:
                differential = ((current_btc_value - original_usd) / original_usd) * 100
                investment.current_value = original_usd + (original_usd * (differential / 100))
            else:
                investment.current_value = 0.0
        
        investments.append(investment.to_dict())
    
    db.session.commit()
    
    return render_template(
        'dashboard.html',
        total_usd=total_usd,
        total_btc=total_btc,
        investments=investments
    )


@app.route('/charge', methods=['POST'])
@login_required
def charge():
    """
    Process a payment and create a new investment.
    
    Uses Stripe for payment processing and records the investment.
    """
    # Investment parameters
    amount = 2000  # $20.00 in cents
    lower_limit = 50
    upper_limit = 50
    investment_uuid = uuid4().hex
    
    try:
        # Create Stripe customer and charge
        token = request.form.get('stripeToken')
        if not token:
            flash('Payment token missing.', 'error')
            return redirect(url_for('dashboard'))
        
        customer = stripe.Customer.create(
            email=current_user.email,
            source=token,
        )
        
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='BitRich Investment',
        )
        
        # Get current Bitcoin rate and calculate BTC amount
        rate = get_bitcoin_rate()
        btc_amount = (amount / 100.0) * rate if rate > 0 else 0.0
        
        # Create investment record
        investment = Investment(
            uuid=investment_uuid,
            user_id=current_user.id,
            deposit_amount_usd=amount,
            deposit_amount_bitcoin=btc_amount,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            current_value=amount / 100.0,
        )
        
        db.session.add(investment)
        db.session.commit()
        
        # Send confirmation email
        html_content = render_template('email/deposit_email.html', user=current_user)
        send_email(current_user.email, 'Thanks for your Investment!', html_content)
        
        flash('Investment successful! Thank you.', 'success')
        
    except stripe.error.CardError as e:
        flash(f'Card error: {e.user_message}', 'error')
    except stripe.error.StripeError as e:
        app.logger.error(f"Stripe error: {e}")
        flash('Payment processing failed. Please try again.', 'error')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Charge error: {e}")
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# CLI commands for database management
@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


@app.cli.command('drop-db')
def drop_db():
    """Drop all database tables."""
    db.drop_all()
    print('Database tables dropped.')


# Create tables on first request (for development)
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
