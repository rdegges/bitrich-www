"""Email utility functions using SendGrid."""
import os
from typing import Optional
from flask import render_template, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from app.models import User, Investment


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using SendGrid.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        
    Returns:
        True if email sent successfully, False otherwise
    """
    api_key = current_app.config.get('SENDGRID_API_KEY')
    from_email = current_app.config.get('SENDGRID_FROM_EMAIL')
    
    if not api_key:
        current_app.logger.warning("SendGrid API key not configured")
        return False
    
    try:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            return True
        else:
            current_app.logger.error(f"SendGrid error: {response.status_code} - {response.body}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False


def send_welcome_email(user: User) -> bool:
    """Send welcome email to new user.
    
    Args:
        user: User object
        
    Returns:
        True if email sent successfully
    """
    subject = 'Welcome to BitRich!'
    html_content = render_template('email/verification_email.html', user=user)
    return send_email(user.email, subject, html_content)


def send_investment_email(user: User, investment: Investment) -> bool:
    """Send investment confirmation email.
    
    Args:
        user: User object
        investment: Investment object
        
    Returns:
        True if email sent successfully
    """
    subject = 'Thanks for your Investment!'
    html_content = render_template('email/deposit_email.html', user=user, investment=investment)
    return send_email(user.email, subject, html_content)


def send_sell_notification(
    user: User,
    investment: Investment,
    differential: float,
    is_upper_limit: bool = True
) -> bool:
    """Send sell notification email.
    
    Args:
        user: User object
        investment: Investment object
        differential: Percentage gain/loss
        is_upper_limit: True if upper limit reached, False if lower
        
    Returns:
        True if email sent successfully
    """
    subject = 'BitRich Investment Notification'
    template = 'email/upper_sell_email.html' if is_upper_limit else 'email/lower_sell_email.html'
    html_content = render_template(
        template,
        user=user,
        investment=investment,
        differential=differential
    )
    return send_email(user.email, subject, html_content)
