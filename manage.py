#!/usr/bin/env python
import os
import sys
import subprocess

# import eventlet and monkey patch threading native objects so they
# work with eventlet
import eventlet
eventlet.monkey_patch()

from flask_script import Manager
from pibrew import create_app, socketio


os.environ['PIBREW_DB_FILENAME'] = 'pibrew.sqlite'
manager = Manager(create_app)


@manager.command
def run():
    app = create_app()
    socketio.run(app, host='localhost', port=5000)


@manager.command
def test():
    """Runs unit tests."""
    tests = subprocess.call(['python', '-c', 'import tests; tests.run()'])
    sys.exit(tests)


@manager.command
def lint():
    """Runs code linter."""
    lint = subprocess.call(['flake8', '--ignore=E402', 'pibrew.py',
                            'manage.py', 'tests/']) == 0
    if lint:
        print('OK')
    sys.exit(lint)


if __name__ == '__main__':
    manager.run()
