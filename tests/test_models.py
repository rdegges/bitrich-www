"""Tests for database models."""
import pytest
from app.models import User, Investment
from app import db


def test_user_password_hashing(app):
    """Test that passwords are properly hashed."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('mypassword')
        
        # Password should be hashed
        assert user.password_hash != 'mypassword'
        
        # Check password should work
        assert user.check_password('mypassword')
        assert not user.check_password('wrongpassword')


def test_user_investment_relationship(app):
    """Test the user-investment relationship."""
    with app.app_context():
        user = User(email='investor@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Add an investment
        investment = Investment(
            user_id=user.id,
            deposit_amount_usd=2000,
            deposit_amount_bitcoin=0.001,
            lower_limit=50,
            upper_limit=50
        )
        db.session.add(investment)
        db.session.commit()
        
        # Refresh to load relationships
        db.session.refresh(user)
        
        # Check relationship
        assert len(user.investments) == 1
        assert user.investments[0].deposit_amount_usd == 2000


def test_investment_calculations(app):
    """Test investment value calculations."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        investment = Investment(
            user_id=user.id,
            deposit_amount_usd=2000,  # $20
            deposit_amount_bitcoin=0.001,
            lower_limit=50,
            upper_limit=50
        )
        
        # Test current value calculation
        current_rate = 0.00002  # Simulated BTC rate
        current_value = investment.calculate_current_value(current_rate)
        assert isinstance(current_value, float)
        
        # Test differential calculation
        differential = investment.calculate_differential(current_rate)
        assert isinstance(differential, float)


def test_user_total_calculations(app):
    """Test user total investment calculations."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Add multiple investments
        for i in range(3):
            investment = Investment(
                user_id=user.id,
                deposit_amount_usd=2000,
                deposit_amount_bitcoin=0.001,
                lower_limit=50,
                upper_limit=50
            )
            db.session.add(investment)
        db.session.commit()
        
        db.session.refresh(user)
        
        # Test totals
        assert user.get_total_investment_usd() == 60.0  # $20 * 3
        assert user.get_total_investment_btc() == 0.003  # 0.001 * 3
