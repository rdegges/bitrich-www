"""Authentication routes blueprint."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.utils.email import send_welcome_email

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration.
    
    Returns:
        Rendered registration template or redirect to dashboard
    """
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(email=form.email.data)
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            login_user(user, remember=True)
            
            # Send welcome email
            try:
                send_welcome_email(user)
            except Exception as e:
                # Log error but don't fail registration
                print(f"Failed to send welcome email: {e}")
            
            flash('Welcome to BitRich! Your account has been created.', 'success')
            return redirect(url_for('investment.dashboard'))
            
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email already exists.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'error')
    
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.
    
    Returns:
        Rendered login template or redirect to dashboard/next page
    """
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('investment.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout.
    
    Returns:
        Redirect to home page
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
