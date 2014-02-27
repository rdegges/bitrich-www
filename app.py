"""
    bitrich-www
    ~~~~~~~~~~~
"""


from datetime import datetime
from json import dumps
from os import environ
from uuid import uuid4

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from flask.ext.stormpath import (
    StormpathManager,
    User,
    login_required,
    login_user,
    logout_user,
    user,
)

from requests import get, post
from stormpath.error import Error as StormpathError

import stripe


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['STORMPATH_API_KEY_ID'] = environ.get('STORMPATH_API_KEY_ID')
app.config['STORMPATH_API_KEY_SECRET'] = environ.get('STORMPATH_API_KEY_SECRET')
app.config['STORMPATH_APPLICATION'] = environ.get('STORMPATH_APPLICATION')
app.config['STRIPE_SECRET_KEY'] = environ.get('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = environ.get('STRIPE_PUBLISHABLE_KEY')
app.config['COINBASE_API_KEY'] = environ.get('COINBASE_API_KEY')
app.config['COINBASE_API_SECRET'] = environ.get('COINBASE_API_SECRET')

stormpath_manager = StormpathManager(app)
stormpath_manager.login_view = '.login'

stripe.api_key = app.config['STRIPE_SECRET_KEY']


##### Website
@app.route('/')
def index():
    """Basic home page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This view allows a user to register for the site.

    This will create a new User in Stormpath, and then log the user into their
    new account immediately (no email verification required).
    """
    if request.method == 'GET':
        return render_template('register.html')

    try:
        # Create a new Stormpath User.
        _user = stormpath_manager.application.accounts.create({
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'given_name': 'John',
            'surname': 'Doe',
        })
        _user.__class__ = User
    except StormpathError, err:
        # If something fails, we'll display a user-friendly error message.
        return render_template('register.html', error=err.message)

    login_user(_user, remember=True)
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    This view logs in a user given an email address and password.

    This works by querying Stormpath with the user's credentials, and either
    getting back the User object itself, or an exception (in which case well
    tell the user their credentials are invalid).

    If the user is valid, we'll log them in, and store their session for later.
    """
    if request.method == 'GET':
        return render_template('login.html')

    try:
        _user = User.from_login(
            request.form.get('email'),
            request.form.get('password'),
        )
    except StormpathError, err:
        return render_template('login.html', error=err.message)

    login_user(_user, remember=True)
    return redirect(request.args.get('next') or url_for('dashboard'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    This view renders a simple dashboard page for logged in users.

    Users can see their personal information on this page, as well as store
    additional data to their account (if they so choose).
    """
    if request.method == 'POST':
        print 'post on dashboard'

    return render_template('dashboard.html')


@app.route('/charge', methods=['POST'])
def charge():
    """
    Charge this user, and take their moneys!
    """
    # By default, the following is true:
    # - All investments are 20$.
    # - The default lower limit is 50%.
    # - The default upper limit is 50%.
    #amount = 2000
    amount = 100
    lower_limit = request.form.get('lower-limit') or 50
    upper_limit = request.form.get('upper-limit') or 50
    id = uuid4().hex

    # Create a Strip customer.
    customer = stripe.Customer.create(
        email = user.email,
        card = request.form['stripeToken'],
    )

    # Bill the user.
    stripe.Charge.create(
        customer = customer.id,
        amount = amount,
        currency = 'usd',
        description = 'BitRich Investment',
    )

    # Get current exchange rates:
    resp = get('https://coinbase.com/api/v1/currencies/exchange_rates')
    rate = float(resp.json()['usd_to_btc'])

    from time import time
    from hmac import new as hnew
    from hashlib import sha256

    nonce = int(time() * 1e6)
    message = str(nonce) + 'https://coinbase.com/api/v1/buys' + dumps({'qty': rate * (amount / 100)})
    signature = hnew(app.config['COINBASE_API_SECRET'], message, sha256).hexdigest()
    resp = post(
        'https://coinbase.com/api/v1/buys',
        params = {'api_key': app.config['COINBASE_API_KEY']},
        headers = {
            'Content-Type': 'application/json',
            'ACCESS_KEY': app.config['COINBASE_API_KEY'],
            'ACCESS_SIGNATURE': signature,
            'ACCESS_NONCE': nonce,
        },
        data = message,
    )
    print resp
    print resp.status_code
    print resp.text
    print dumps(resp.json(), indent=2, sort_keys=True)

    # Store investment details in Stormpath.
    try:
        user.custom_data['investments'].append({
            'id': id,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat(),
            'deposit_amount_usd': amount,
            'deposit_amount_bitcoin': None,
            'lower_limit': lower_limit,
            'upper_limit': upper_limit,
        })
    except:
        user.custom_data['investments'] = []
        user.custom_data['investments'].append({
            'id': id,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat(),
            'deposit_amount_usd': amount,
            'deposit_amount_bitcoin': None,
            'lower_limit': lower_limit,
            'upper_limit': upper_limit,
        })

    user.save()

    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    """
    Log out a logged in user.  Then redirect them back to the main page of the
    site.
    """
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
