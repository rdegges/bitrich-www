"""Custom Flask CLI commands."""

from __future__ import annotations

from decimal import Decimal

import click
from flask import current_app, render_template
from flask.cli import with_appcontext

from .emailing import EmailClient
from .models import Investment, User
from .services import fetch_rate_snapshot


def register_cli(app) -> None:
    """Attach project specific CLI commands to the app instance."""

    @app.cli.command('sell-or-not')
    @with_appcontext
    def sell_or_not() -> None:
        """Scan investments and email users when thresholds are crossed."""
        snapshot = fetch_rate_snapshot()
        click.echo(f'Current BTC price: ${snapshot.usd_per_btc:,.2f} per BTC')

        client: EmailClient = current_app.extensions['email_client']
        total_notifications = 0

        for user in User.query.order_by(User.email).all():
            click.echo(f'Checking user: {user.email}')
            for investment in user.investments:
                current_value = Decimal(investment.deposit_amount_bitcoin) * snapshot.usd_per_btc
                original_value = Decimal(investment.deposit_amount_usd) / Decimal('100')
                if not original_value:
                    continue

                differential = float(
                    ((current_value - original_value) / original_value) * Decimal('100')
                )

                if differential <= -investment.lower_limit:
                    _send_threshold_email(
                        client=client,
                        template='email/lower_sell_email.html',
                        subject='BitRich lower limit reached',
                        user=user,
                        investment=investment,
                        differential=differential,
                    )
                    total_notifications += 1
                elif differential >= investment.upper_limit:
                    _send_threshold_email(
                        client=client,
                        template='email/upper_sell_email.html',
                        subject='BitRich upper limit reached',
                        user=user,
                        investment=investment,
                        differential=differential,
                    )
                    total_notifications += 1

        click.echo(f'Finished processing investments. Notifications sent: {total_notifications}')


def _send_threshold_email(
    *,
    client: EmailClient,
    template: str,
    subject: str,
    user: User,
    investment: Investment,
    differential: float,
) -> None:
    html = render_template(
        template,
        user=user,
        investment=investment.to_dict(),
        differential=differential,
    )
    client.send_html(recipient=user.email, subject=subject, html=html)
