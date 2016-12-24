#!/usr/bin/env python
import os
import sys
import subprocess

# import eventlet and monkey patch threading native objects so they
# work with eventlet
import eventlet
eventlet.monkey_patch()

from pibrew import create_app, db
from pibrew.models import Setting, SequenceStep
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Setting=Setting, SequenceStep=SequenceStep)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def run():
    from pibrew import socketio
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True)


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
