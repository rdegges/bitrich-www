"""Cryptocurrency utility functions."""
from typing import Optional
import requests
from flask import current_app


def get_btc_exchange_rate() -> float:
    """Get current BTC to USD exchange rate.
    
    Note: This now uses CoinGecko API as Coinbase v1 API is deprecated.
    
    Returns:
        Current BTC/USD rate
        
    Raises:
        Exception: If unable to fetch rate
    """
    try:
        # Use CoinGecko API (free, no API key required)
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd'},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        return float(data['bitcoin']['usd'])
        
    except requests.RequestException as e:
        current_app.logger.error(f"Failed to fetch BTC rate: {e}")
        raise Exception("Unable to fetch current exchange rate")


def purchase_bitcoin(amount_usd: float, rate: float) -> float:
    """Simulate Bitcoin purchase.
    
    Note: This is now a simulation. In production, you would integrate
    with a cryptocurrency exchange API like Coinbase Commerce, Kraken, etc.
    
    Args:
        amount_usd: Amount in USD to convert
        rate: BTC/USD exchange rate
        
    Returns:
        Amount of BTC purchased
    """
    # Calculate BTC amount (USD / BTC_price = BTC_amount)
    btc_amount = amount_usd / rate
    
    # Log the simulated purchase
    current_app.logger.info(
        f"Simulated BTC purchase: ${amount_usd:.2f} = {btc_amount:.8f} BTC at rate ${rate:.2f}"
    )
    
    return btc_amount


def should_sell_investment(
    deposit_btc: float,
    deposit_usd_cents: int,
    current_rate: float,
    lower_limit: int,
    upper_limit: int
) -> tuple[bool, float, Optional[str]]:
    """Determine if an investment should be sold.
    
    Args:
        deposit_btc: Original BTC amount
        deposit_usd_cents: Original USD amount in cents
        current_rate: Current BTC/USD rate
        lower_limit: Lower sell limit percentage
        upper_limit: Upper sell limit percentage
        
    Returns:
        Tuple of (should_sell, differential_percentage, reason)
        reason is 'upper', 'lower', or None
    """
    # Calculate the adjusted BTC value
    btc_adjusted = deposit_btc * (deposit_usd_cents / 100.0)
    
    # Calculate percentage differential
    differential = ((current_rate - btc_adjusted) / btc_adjusted) * 100
    differential = round(differential, 2)
    
    # Check limits
    if differential < (lower_limit * -1):
        return True, differential, 'lower'
    elif differential > upper_limit:
        return True, differential, 'upper'
    else:
        return False, differential, None
