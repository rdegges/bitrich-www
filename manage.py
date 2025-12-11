"""
Management commands for BitRich.

This module provides CLI commands for administrative tasks
such as checking investments and sending notifications.

Usage:
    flask sell-or-not    # Check if investments should be sold
    flask init-db        # Initialize database
"""

import click
from flask import render_template

from app import app, db, User, Investment, send_email, get_bitcoin_rate


@app.cli.command('sell-or-not')
def sell_or_not():
    """Check all investments and send notifications if limits are reached."""
    rate = get_bitcoin_rate()
    
    if rate <= 0:
        click.echo('Error: Could not fetch Bitcoin rate.')
        return
    
    click.echo(f'Checking investments with current BTC rate: {rate:.8f} BTC/USD')
    
    with app.app_context():
        users = User.query.all()
        
        for user in users:
            click.echo(f'\nChecking user: {user.email}')
            
            for investment in user.investments.all():
                click.echo(f'  Investment: {investment.uuid}')
                click.echo(f'    Lower limit: {investment.lower_limit}%')
                click.echo(f'    Upper limit: {investment.upper_limit}%')
                
                # Calculate investment performance
                total_btc = investment.deposit_amount_bitcoin
                total_usd_cents = investment.deposit_amount_usd
                original_usd = total_usd_cents / 100.0
                
                # Current value in USD
                current_usd = total_btc / rate if rate > 0 else 0
                
                # Calculate differential
                if original_usd > 0:
                    differential = ((current_usd - original_usd) / original_usd) * 100
                else:
                    differential = 0
                
                click.echo(f'    Original value: ${original_usd:.2f}')
                click.echo(f'    Current value: ${current_usd:.2f}')
                click.echo(f'    Differential: {differential:.2f}%')
                
                # Check if we should sell based on limits
                lower_threshold = -investment.lower_limit
                upper_threshold = investment.upper_limit
                
                if differential < lower_threshold:
                    click.echo(f'    ⚠️  SELL (lower limit reached): Lost {abs(differential):.2f}%!')
                    
                    html_content = render_template(
                        'email/lower_sell_email.html',
                        user=user,
                        differential=differential,
                        investment=investment.to_dict(),
                    )
                    send_email(
                        user.email,
                        'BitRich Investment Notification - Lower Limit Reached',
                        html_content
                    )
                    
                elif differential > upper_threshold:
                    click.echo(f'    ✅ SELL (upper limit reached): Gained {differential:.2f}%!')
                    
                    html_content = render_template(
                        'email/upper_sell_email.html',
                        user=user,
                        differential=differential,
                        investment=investment.to_dict(),
                    )
                    send_email(
                        user.email,
                        'BitRich Investment Notification - Upper Limit Reached',
                        html_content
                    )
                else:
                    click.echo('    📊 HOLD (within limits)')
                
                # Update current value
                investment.current_value = current_usd
            
            db.session.commit()
    
    click.echo('\nDone checking investments.')


@app.cli.command('list-users')
def list_users():
    """List all registered users."""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            click.echo('No users found.')
            return
        
        click.echo(f'Found {len(users)} user(s):')
        for user in users:
            investment_count = user.investments.count()
            click.echo(f'  - {user.email} ({investment_count} investments)')


@app.cli.command('create-user')
@click.argument('email')
@click.argument('password')
def create_user(email: str, password: str):
    """Create a new user account."""
    with app.app_context():
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            click.echo(f'Error: User {email} already exists.')
            return
        
        user = User(email=email.lower())
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'Created user: {email}')


if __name__ == '__main__':
    app.cli()
