"""Modern Flask application for the satirical BitRich landing page."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional
from uuid import uuid4

import requests
from dotenv import load_dotenv
from flask import Flask, current_app, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config


load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    register_cli(app)
    register_routes(app)
    return app


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    investments = db.relationship(
        "Investment",
        backref="owner",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="Investment.created_at.desc()",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(32), default=lambda: uuid4().hex, unique=True, nullable=False
    )
    amount_cents = db.Column(db.Integer, nullable=False)
    deposit_btc = db.Column(db.Numeric(18, 8), nullable=False)
    spot_rate_usd = db.Column(db.Numeric(12, 2), nullable=False)
    lower_limit = db.Column(db.Integer, nullable=False, default=50)
    upper_limit = db.Column(db.Integer, nullable=False, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def principal_usd(self) -> Decimal:
        return Decimal(self.amount_cents) / Decimal("100")

    def market_value(self, market_rate: Optional[Decimal]) -> Decimal:
        rate = _as_decimal(market_rate) or Decimal(str(self.spot_rate_usd))
        return Decimal(self.deposit_btc) * rate

    def performance(self, market_rate: Optional[Decimal]) -> Decimal:
        current_value = self.market_value(market_rate)
        original_value = Decimal(self.deposit_btc) * Decimal(str(self.spot_rate_usd))
        if original_value == 0:
            return Decimal("0")
        return ((current_value - original_value) / original_value) * Decimal("100")


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    if not user_id:
        return None
    try:
        return db.session.get(User, int(user_id))
    except ValueError:
        return None


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html")

        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "warning")
            return render_template("register.html")

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash("Welcome to BitRich! Time to make that 'investment'.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return render_template("login.html")

        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        login_user(user, remember=True)
        flash("Logged in successfully.", "success")
        next_url = request.args.get("next") or url_for("dashboard")
        return redirect(next_url)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        market_rate = fetch_exchange_rate()
        investments = list(current_user.investments)

        total_usd_cents = sum(investment.amount_cents for investment in investments)
        total_btc = Decimal(
            sum(
                (_as_decimal(investment.deposit_btc) or Decimal("0"))
                for investment in investments
            )
        )

        for investment in investments:
            investment.current_value = investment.market_value(market_rate)
            investment.differential = investment.performance(market_rate)

        return render_template(
            "dashboard.html",
            investments=investments,
            total_usd=Decimal(total_usd_cents) / Decimal("100"),
            total_btc=total_btc,
            market_rate=market_rate,
            min_deposit=app.config["MIN_DEPOSIT_USD"],
            max_deposit=app.config["MAX_DEPOSIT_USD"],
        )

    @app.route("/charge", methods=["POST"])
    @login_required
    def charge():
        amount = request.form.get("amount", "").strip()
        lower_limit = _coerce_percentage(request.form.get("lower-limit"), default=50)
        upper_limit = _coerce_percentage(request.form.get("upper-limit"), default=50)

        amount_decimal = _coerce_amount(amount)
        if amount_decimal is None:
            flash("Enter a valid deposit amount using numbers only.", "danger")
            return redirect(url_for("dashboard"))

        min_amount = Decimal(app.config["MIN_DEPOSIT_USD"])
        max_amount = Decimal(app.config["MAX_DEPOSIT_USD"])

        if amount_decimal < min_amount or amount_decimal > max_amount:
            flash(
                f"Deposits must be between {min_amount} and {max_amount} USD.",
                "warning",
            )
            return redirect(url_for("dashboard"))

        market_rate = fetch_exchange_rate() or Decimal("27500")
        if market_rate <= 0:
            flash("Unable to fetch a current BTC price. Please try again later.", "danger")
            return redirect(url_for("dashboard"))

        deposit_btc = (amount_decimal / market_rate).quantize(
            Decimal("0.00000001"), rounding=ROUND_HALF_UP
        )

        investment = Investment(
            amount_cents=int(amount_decimal * 100),
            deposit_btc=deposit_btc,
            spot_rate_usd=market_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            owner=current_user,
        )
        db.session.add(investment)
        db.session.commit()

        flash("Deposit simulated successfully. We'll guard it... probably.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("See you next time.", "info")
        return redirect(url_for("index"))


def register_cli(app: Flask) -> None:
    @app.cli.command("check-investments")
    def check_investments() -> None:
        """Evaluate every investment and print threshold notifications."""
        market_rate = fetch_exchange_rate()
        if market_rate is None:
            app.logger.warning("Could not fetch BTC price; aborting check.")
            return

        alerts = 0
        investments = Investment.query.all()
        for investment in investments:
            differential = investment.performance(market_rate)
            if differential <= Decimal(-investment.lower_limit):
                alerts += 1
                app.logger.warning(
                    "Investment %s for %s lost %s%% (limit %s%%).",
                    investment.public_id,
                    investment.owner.email,
                    round(float(differential), 2),
                    investment.lower_limit,
                )
            elif differential >= Decimal(investment.upper_limit):
                alerts += 1
                app.logger.info(
                    "Investment %s for %s gained %s%% (limit %s%%).",
                    investment.public_id,
                    investment.owner.email,
                    round(float(differential), 2),
                    investment.upper_limit,
                )

        app.logger.info(
            "Checked %s investments. Alerts triggered: %s", len(investments), alerts
        )


def fetch_exchange_rate() -> Optional[Decimal]:
    """Fetch the USD price of BTC from the configured upstream API."""
    url = current_app.config.get("EXCHANGE_RATE_URL", Config.EXCHANGE_RATE_URL)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        payload = response.json()
    except Exception as err:  # noqa: BLE001 - we want to fall back gracefully
        current_app.logger.warning("Failed to fetch BTC price: %s", err)
        return None

    if isinstance(payload, dict):
        if "bpi" in payload:
            return Decimal(str(payload["bpi"]["USD"]["rate_float"]))
        if "data" in payload and "amount" in payload["data"]:
            return Decimal(str(payload["data"]["amount"]))

    return None


def _coerce_amount(value: str) -> Optional[Decimal]:
    if not value:
        return None

    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError):
        return None

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _coerce_percentage(value: Optional[str], default: int) -> int:
    try:
        parsed = int(value)
        return max(1, min(parsed, 100))
    except (TypeError, ValueError):
        return default


def _as_decimal(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
