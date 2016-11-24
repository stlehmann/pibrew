#!/usr/bin/env python
import os
import subprocess
import sys
import eventlet
from flask_script import Manager
from pibrew import create_app, socketio, brew_controller


manager = Manager(create_app)


@manager.command
def run():
    eventlet.monkey_patch()
    app = create_app()
    socketio.run(app, host='localhost', port=5000, )


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
