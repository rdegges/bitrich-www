"""Management scripts and utilities."""


from flask import render_template
from flask.ext.script import Manager
from flask.ext.stormpath import User
from requests import get
from sendgrid import Mail

from app import app, sendgrid


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
                print 'btc_adjusted (old):', btc_adjusted
                print 'rate (new):', rate

                # Now that we know how much bitcoin is currently worth, vs what
                # the user has -- we can calculate the net gain of this user's
                # investment.
                differential = float('%.2f' % (((rate - btc_adjusted) / btc_adjusted) * 100))
                print 'differential: %s%%' % differential

                message = Mail(
                    to = user.email,
                    subject = 'BitRich Investment Notification',
                    text = '',
                    from_email = 'randall@stormpath.com',
                )

                investment['lower_limit'] = .0001
                if differential < (investment['lower_limit'] * -1):
                    print "We've lost %s%%! Time to sell! Our lower limit is %s%%!" % (
                        differential,
                        investment['lower_limit'],
                    )
                    message.set_html(render_template(
                        'email/lower_sell_email.html',
                        user = user,
                        differential = differential,
                        investment = investment,
                    ).encode('utf_8').decode('unicode_escape'))
                    sendgrid.send(message)

                if differential > investment['upper_limit']:
                    print "We've made %s%%! Time to sell! Our upper limit is %s%%!" % (
                        differential,
                        investment['upper_limit'],
                    )
                    message.set_html(render_template(
                        'email/upper_sell_email.html',
                        user = user,
                        differential = differential,
                        investment = investment,
                    ).encode('utf_8').decode('unicode_escape'))
                    sendgrid.send(message)


if __name__ == '__main__':
    manager.run()
