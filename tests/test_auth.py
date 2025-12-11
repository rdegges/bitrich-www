"""Tests for authentication routes."""
import pytest
from flask import url_for
from app.models import User
from app import db


def test_register_page_loads(client):
    """Test that the registration page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Sign up for a free account' in response.data


def test_login_page_loads(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Log in' in response.data


def test_user_registration(client, app):
    """Test user registration."""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'csrf_token': 'dummy'  # In testing, CSRF is disabled
    }, follow_redirects=True)
    
    # Should redirect to dashboard
    assert response.status_code == 200
    
    # Verify user was created
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.check_password('password123')


def test_user_login(client, user):
    """Test user login."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'csrf_token': 'dummy'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_user_login_invalid_credentials(client, user):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword',
        'csrf_token': 'dummy'
    }, follow_redirects=True)
    
    assert b'Invalid email or password' in response.data


def test_logout(client, user):
    """Test user logout."""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'csrf_token': 'dummy'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data


def test_dashboard_requires_login(client):
    """Test that dashboard requires authentication."""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login
