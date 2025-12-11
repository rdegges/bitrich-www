"""Payment processing utility functions using Stripe."""
from typing import Optional
from flask import current_app
import stripe


def get_stripe_api_key() -> Optional[str]:
    """Get Stripe API key from configuration.
    
    Returns:
        Stripe API key or None
    """
    return current_app.config.get('STRIPE_SECRET_KEY')


def create_stripe_customer(email: str, token: str) -> str:
    """Create a Stripe customer.
    
    Args:
        email: Customer email address
        token: Stripe token from frontend
        
    Returns:
        Stripe customer ID
        
    Raises:
        Exception: If customer creation fails
    """
    stripe.api_key = get_stripe_api_key()
    
    try:
        customer = stripe.Customer.create(
            email=email,
            source=token
        )
        return customer.id
    except stripe.error.StripeError as e:
        current_app.logger.error(f"Stripe customer creation error: {e}")
        raise Exception(f"Failed to create payment customer: {str(e)}")


def charge_customer(customer_id: str, amount: int, description: str = '') -> str:
    """Charge a Stripe customer.
    
    Args:
        customer_id: Stripe customer ID
        amount: Amount in cents
        description: Charge description
        
    Returns:
        Stripe charge ID
        
    Raises:
        Exception: If charge fails
    """
    stripe.api_key = get_stripe_api_key()
    
    try:
        charge = stripe.Charge.create(
            customer=customer_id,
            amount=amount,
            currency='usd',
            description=description
        )
        return charge.id
    except stripe.error.StripeError as e:
        current_app.logger.error(f"Stripe charge error: {e}")
        raise Exception(f"Payment failed: {str(e)}")
