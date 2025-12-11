"""Investment routes blueprint."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Investment
from app.forms import InvestmentForm
from app.utils.crypto import get_btc_exchange_rate, purchase_bitcoin
from app.utils.payment import create_stripe_customer, charge_customer
from app.utils.email import send_investment_email

bp = Blueprint('investment', __name__)


@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Render user dashboard with investment information.
    
    Returns:
        Rendered dashboard template
    """
    form = InvestmentForm()
    
    try:
        # Get current BTC rate
        current_rate = get_btc_exchange_rate()
        
        # Calculate totals and current values
        total_usd = 0
        total_btc = 0.0
        
        for investment in current_user.investments:
            total_usd += investment.deposit_amount_usd
            total_btc += investment.deposit_amount_bitcoin
            
            # Add current value to each investment for display
            investment.current_value = investment.calculate_current_value(current_rate)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching exchange rate: {e}")
        flash('Unable to fetch current exchange rates. Please try again later.', 'warning')
        total_usd = 0
        total_btc = 0.0
    
    return render_template(
        'dashboard.html',
        form=form,
        total_usd=total_usd,
        total_btc=total_btc
    )


@bp.route('/charge', methods=['POST'])
@login_required
def charge():
    """Process investment charge and Bitcoin purchase.
    
    Returns:
        Redirect to dashboard
    """
    form = InvestmentForm()
    
    if not form.validate_on_submit():
        flash('Invalid form data. Please try again.', 'error')
        return redirect(url_for('investment.dashboard'))
    
    # Investment parameters
    amount = 2000  # $20 in cents
    lower_limit = form.lower_limit.data or 50
    upper_limit = form.upper_limit.data or 50
    stripe_token = request.form.get('stripeToken')
    
    if not stripe_token:
        flash('Payment token missing. Please try again.', 'error')
        return redirect(url_for('investment.dashboard'))
    
    try:
        # Create Stripe customer and charge
        customer_id = create_stripe_customer(
            email=current_user.email,
            token=stripe_token
        )
        charge_id = charge_customer(
            customer_id=customer_id,
            amount=amount,
            description='BitRich Investment'
        )
        
        # Get current BTC exchange rate
        btc_rate = get_btc_exchange_rate()
        
        # Purchase Bitcoin (this is now simulated since Coinbase API changed)
        btc_amount = purchase_bitcoin(
            amount_usd=amount / 100.0,
            rate=btc_rate
        )
        
        # Create investment record
        investment = Investment(
            user_id=current_user.id,
            deposit_amount_usd=amount,
            deposit_amount_bitcoin=btc_amount,
            lower_limit=lower_limit,
            upper_limit=upper_limit,
            stripe_customer_id=customer_id,
            stripe_charge_id=charge_id
        )
        
        db.session.add(investment)
        db.session.commit()
        
        # Send confirmation email
        try:
            send_investment_email(current_user, investment)
        except Exception as e:
            current_app.logger.error(f"Failed to send investment email: {e}")
        
        flash(f'Successfully invested ${amount/100:.2f}! Your Bitcoin has been purchased.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Investment error: {e}")
        flash(f'An error occurred processing your investment: {str(e)}', 'error')
    
    return redirect(url_for('investment.dashboard'))
