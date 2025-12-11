"""Application factory and shared extensions for BitRich."""

from __future__ import annotations

import stripe
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from .config import Settings

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'pages.login'
login_manager.login_message_category = 'info'


def create_app(config_class: type[Settings] | None = None) -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__, instance_relative_config=False)

    config_obj = config_class or Settings
    app.config.from_object(config_obj)

    db.init_app(app)
    login_manager.init_app(app)

    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

    from .emailing import EmailClient

    app.extensions['email_client'] = EmailClient(
        api_key=app.config.get('SENDGRID_API_KEY'),
        sender=app.config.get('SENDGRID_FROM_EMAIL'),
    )

    from . import models  # noqa: F401  # register SQLAlchemy models

    with app.app_context():
        db.create_all()

    from .routes import bp as pages_bp

    app.register_blueprint(pages_bp)

    from .cli import register_cli

    register_cli(app)

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        return {'config': app.config}

    return app


__all__ = ['create_app', 'db', 'login_manager']
