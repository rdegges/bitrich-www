"""HTTP routes for the BitRich application."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

import stripe
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .emailing import EmailClient
from .models import Investment, User
from .services import fetch_rate_snapshot

bp = Blueprint('pages', __name__)


def _email_client() -> EmailClient:
    return current_app.extensions['email_client']


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard'))

    error = None
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not email or not password:
            error = 'Email and password are required.'
        elif User.query.filter_by(email=email).first():
            error = 'That email is already registered.'
        else:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)

            _email_client().send_html(
                recipient=user.email,
                subject='Welcome to BitRich!',
                html=render_template('email/verification_email.html', user=user),
            )
            return redirect(url_for('pages.dashboard'))

    return render_template('register.html', error=error)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard'))

    error = None
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            error = 'Invalid email or password.'
        else:
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('pages.dashboard'))

    return render_template('login.html', error=error)


@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    snapshot = fetch_rate_snapshot()
    investments = list(current_user.investments)

    total_usd = sum(inv.deposit_amount_usd for inv in investments)
    total_btc = sum(Decimal(inv.deposit_amount_bitcoin) for inv in investments)

    serialized_investments = []
    for inv in investments:
        serialized = inv.to_dict()
        serialized['current_value'] = float(
            Decimal(inv.deposit_amount_bitcoin) * snapshot.usd_per_btc
            if snapshot.usd_per_btc
            else Decimal('0')
        )
        serialized_investments.append(serialized)

    return render_template(
        'dashboard.html',
        total_usd=total_usd,
        total_btc=float(total_btc),
        investments=serialized_investments,
        snapshot=snapshot,
    )


def _parse_limits(value: str | None, fallback: int) -> int:
    try:
        parsed = int(value) if value else fallback
        return max(1, parsed)
    except (TypeError, ValueError):
        return fallback


@bp.route('/charge', methods=['POST'])
@login_required
def charge():
    amount_cents = int(request.form.get('amount') or current_app.config['DEFAULT_DEPOSIT_CENTS'])
    lower_limit = _parse_limits(request.form.get('lower-limit'), current_app.config['DEFAULT_LOWER_LIMIT'])
    upper_limit = _parse_limits(request.form.get('upper-limit'), current_app.config['DEFAULT_UPPER_LIMIT'])

    token = request.form.get('stripeToken')
    secret_key = current_app.config.get('STRIPE_SECRET_KEY')

    if token and secret_key:
        try:
            customer = stripe.Customer.create(
                email=current_user.email,
                source=token,
            )
            stripe.Charge.create(
                customer=customer.id,
                amount=amount_cents,
                currency='usd',
                description='BitRich Investment',
            )
        except stripe.error.StripeError as exc:
            current_app.logger.error('Stripe charge failed: %s', exc)
            flash('Your card could not be charged. Please try again.', 'danger')
            return redirect(url_for('pages.dashboard'))

    snapshot = fetch_rate_snapshot()
    btc_amount = (
        Decimal(amount_cents) / Decimal('100') * snapshot.usd_to_btc
        if snapshot.usd_to_btc
        else Decimal('0')
    )
    btc_amount = btc_amount.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)

    investment = Investment(
        deposit_amount_usd=amount_cents,
        deposit_amount_bitcoin=btc_amount,
        lower_limit=lower_limit,
        upper_limit=upper_limit,
        user=current_user,
    )
    db.session.add(investment)
    db.session.commit()

    _email_client().send_html(
        recipient=current_user.email,
        subject='Thanks for your BitRich investment!',
        html=render_template('email/deposit_email.html', user=current_user, investment=investment.to_dict()),
    )

    flash('Investment recorded successfully.', 'success')
    return redirect(url_for('pages.dashboard'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.index'))
