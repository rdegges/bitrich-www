"""Management utilities for BitRich."""

from decimal import Decimal

import click

from app import Investment, app, fetch_exchange_rate


@click.group()
def cli():
    """Command group for BitRich management tasks."""


@cli.command()
def sell_or_not():
    """Evaluate every investment and print when thresholds are crossed."""
    with app.app_context():
        market_rate = fetch_exchange_rate()
        if market_rate is None:
            click.echo("Unable to fetch BTC price. Please try again later.")
            return

        click.echo(f"Checking {Investment.query.count()} investments @ ${market_rate:.2f}")
        alerts = 0
        for investment in Investment.query.all():
            diff = investment.performance(market_rate)
            msg = (
                f"[{investment.public_id}] {investment.owner.email} "
                f"{diff:+.2f}% (limits: -{investment.lower_limit}% / +{investment.upper_limit}%)"
            )
            if diff <= Decimal(-investment.lower_limit):
                alerts += 1
                click.echo(f"🔻 {msg}")
            elif diff >= Decimal(investment.upper_limit):
                alerts += 1
                click.echo(f"🚀 {msg}")

        click.echo(f"Done. Alerts triggered: {alerts}")


if __name__ == "__main__":
    cli()
