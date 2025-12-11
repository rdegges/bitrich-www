"""Database models for the BitRich application."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    """Registered BitRich user."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        default=lambda: uuid4().hex,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    investments: Mapped[list['Investment']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Investment(db.Model):
    """Individual micro-investment."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        default=lambda: uuid4().hex,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deposit_amount_usd: Mapped[int] = mapped_column(Integer, nullable=False)
    deposit_amount_bitcoin: Mapped[Decimal] = mapped_column(
        Numeric(18, 8),
        nullable=False,
    )
    lower_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    upper_limit: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped[User] = relationship(back_populates='investments')

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialization compatible with the legacy templates."""
        return {
            'id': self.public_id,
            'created': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deposit_amount_usd': self.deposit_amount_usd,
            'deposit_amount_bitcoin': float(self.deposit_amount_bitcoin),
            'lower_limit': self.lower_limit,
            'upper_limit': self.upper_limit,
        }


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Return the user associated with the given session identifier."""
    if not user_id:
        return None
    return db.session.get(User, int(user_id))
