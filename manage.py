"""Management CLI commands."""
import os
import click
from dotenv import load_dotenv
from flask import render_template

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import User, Investment
from app.utils.crypto import get_btc_exchange_rate, should_sell_investment
from app.utils.email import send_sell_notification

app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Database initialized successfully.')


@app.cli.command()
def check_investments():
    """Check all investments and send sell notifications if limits reached."""
    try:
        current_rate = get_btc_exchange_rate()
        click.echo(f'Current BTC rate: ${current_rate:.2f}')
        
        with app.app_context():
            users = User.query.all()
            
            for user in users:
                click.echo(f'\nChecking user: {user.email}')
                
                for investment in user.investments:
                    click.echo(f'  Investment ID: {investment.id}')
                    click.echo(f'  Lower limit: {investment.lower_limit}%')
                    click.echo(f'  Upper limit: {investment.upper_limit}%')
                    
                    should_sell, differential, reason = should_sell_investment(
                        deposit_btc=investment.deposit_amount_bitcoin,
                        deposit_usd_cents=investment.deposit_amount_usd,
                        current_rate=current_rate,
                        lower_limit=investment.lower_limit,
                        upper_limit=investment.upper_limit
                    )
                    
                    click.echo(f'  Differential: {differential}%')
                    
                    if should_sell:
                        if reason == 'lower':
                            click.echo(f'  ⚠️  Lower limit reached! Sending notification...')
                            send_sell_notification(
                                user=user,
                                investment=investment,
                                differential=differential,
                                is_upper_limit=False
                            )
                        elif reason == 'upper':
                            click.echo(f'  ✅ Upper limit reached! Sending notification...')
                            send_sell_notification(
                                user=user,
                                investment=investment,
                                differential=differential,
                                is_upper_limit=True
                            )
                    else:
                        click.echo(f'  ℹ️  No action needed.')
        
        click.echo('\n✅ Investment check completed.')
        
    except Exception as e:
        click.echo(f'❌ Error: {e}', err=True)


@app.cli.command()
@click.option('--email', prompt='Email', help='User email address')
@click.option('--password', prompt='Password', hide_input=True, help='User password')
def create_user(email: str, password: str):
    """Create a new user."""
    try:
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f'✅ User {email} created successfully.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'❌ Error creating user: {e}', err=True)


@app.cli.command()
def list_users():
    """List all users."""
    users = User.query.all()
    
    if not users:
        click.echo('No users found.')
        return
    
    click.echo(f'\nTotal users: {len(users)}\n')
    
    for user in users:
        investment_count = len(user.investments)
        total_usd = user.get_total_investment_usd()
        total_btc = user.get_total_investment_btc()
        
        click.echo(f'ID: {user.id}')
        click.echo(f'Email: {user.email}')
        click.echo(f'Created: {user.created_at}')
        click.echo(f'Investments: {investment_count}')
        click.echo(f'Total Invested: ${total_usd:.2f} ({total_btc:.8f} BTC)')
        click.echo('-' * 50)


if __name__ == '__main__':
    app.run()
