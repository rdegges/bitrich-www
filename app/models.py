"""Database models."""
from datetime import datetime
from typing import Optional
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from app import db, login_manager, bcrypt


class User(UserMixin, db.Model):
    """User model for authentication and profile."""
    
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    # Relationships
    investments: Mapped[list["Investment"]] = relationship(
        'Investment',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password.
        
        Args:
            password: Plain text password
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_total_investment_usd(self) -> float:
        """Calculate total USD invested.
        
        Returns:
            Total USD amount invested
        """
        return sum(inv.deposit_amount_usd for inv in self.investments) / 100.0
    
    def get_total_investment_btc(self) -> float:
        """Calculate total BTC invested.
        
        Returns:
            Total BTC amount
        """
        return sum(inv.deposit_amount_bitcoin for inv in self.investments)
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class Investment(db.Model):
    """Investment model for tracking cryptocurrency purchases."""
    
    __tablename__ = 'investments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    
    # Investment details
    deposit_amount_usd: Mapped[int] = mapped_column(Integer, nullable=False)  # Amount in cents
    deposit_amount_bitcoin: Mapped[float] = mapped_column(Float, nullable=False)
    lower_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=50)  # Percentage
    upper_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=50)  # Percentage
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Payment tracking
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100))
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    user: Mapped["User"] = relationship('User', back_populates='investments')
    
    def calculate_current_value(self, current_btc_rate: float) -> float:
        """Calculate the current value of this investment.
        
        Args:
            current_btc_rate: Current BTC to USD rate
            
        Returns:
            Current value in USD
        """
        btc_adjusted = self.deposit_amount_bitcoin * (self.deposit_amount_usd / 100.0)
        differential = ((current_btc_rate - btc_adjusted) / btc_adjusted) * 100
        current_value = (
            (self.deposit_amount_usd / 100) + 
            ((self.deposit_amount_usd / 100) * (differential / 100))
        )
        return round(current_value, 2)
    
    def calculate_differential(self, current_btc_rate: float) -> float:
        """Calculate the gain/loss percentage.
        
        Args:
            current_btc_rate: Current BTC to USD rate
            
        Returns:
            Percentage gain (positive) or loss (negative)
        """
        btc_adjusted = self.deposit_amount_bitcoin * (self.deposit_amount_usd / 100.0)
        differential = ((current_btc_rate - btc_adjusted) / btc_adjusted) * 100
        return round(differential, 2)
    
    def __repr__(self) -> str:
        return f'<Investment {self.id} - User {self.user_id}>'


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Load user by ID for Flask-Login.
    
    Args:
        user_id: User ID as string
        
    Returns:
        User object or None
    """
    return User.query.get(int(user_id))
