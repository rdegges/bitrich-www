"""Management scripts and utilities."""


from flask.ext.script import Manager
from flask.ext.stormpath import User
from requests import get

from app import app


##### GLOBALS
manager = Manager(app)


##### COMMANDS
@manager.command
def sell_or_not():
    resp = get('https://coinbase.com/api/v1/currencies/exchange_rates')
    rate = float(resp.json()['usd_to_btc'])
    print 'Checking whether we should sell or not with current BTC rates of:', rate

    with app.app_context():
        for user in app.stormpath_manager.application.accounts:
            user.__class__ = User

            print 'Checking user:', user.email
            for investment in user.custom_data.get('investments', []):

                print 'Checking investment:', investment['id']
                print 'Lower sell limit is set to: %s%%' % investment['lower_limit']
                print 'Upper sell limit is set to: %s%%' % investment['upper_limit']

                # Grab the total BTC / USD that this user has in their account
                # (when the investment was made).
                total_btc = float(investment['deposit_amount_bitcoin'])
                total_usd_cents = investment['deposit_amount_usd']

                # btc_adjusted is the amount of bitcoin this user's money is
                # worth at current rates
                btc_adjusted = total_btc * (total_usd_cents / 100.0)
                print 'btc_adjusted:', btc_adjusted

                # Now that we know how much bitcoin is currently worth, vs what
                # the user has -- we can calculate the net gain of this user's
                # investment.
                print 'differential: ', ((total_btc - btc_adjusted) / total_btc) * 100


if __name__ == '__main__':
    manager.run()
