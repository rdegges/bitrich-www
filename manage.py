"""Management scripts and utilities."""


from flask.ext.script import Manager

from app import app


##### GLOBALS
manager = Manager(app)


##### COMMANDS
@manager.command
def blah():
    print 'Iterating through all users, '


if __name__ == '__main__':
    manager.run()
