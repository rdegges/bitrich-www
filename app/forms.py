"""WTForms for user input validation."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=120)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters long')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )


class LoginForm(FlaskForm):
    """User login form."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required')]
    )


class InvestmentForm(FlaskForm):
    """Investment creation form."""
    
    lower_limit = IntegerField(
        'Lower Limit',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message='Must be between 0 and 100')
        ],
        default=50
    )
    upper_limit = IntegerField(
        'Upper Limit',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message='Must be between 0 and 100')
        ],
        default=50
    )
