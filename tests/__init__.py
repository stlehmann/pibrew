import os
import sys
import subprocess
import unittest

import coverage


def run():
    os.environ['DATABASE_URL'] = 'sqlite://'

    # start coverage engine
    cov = coverage.Coverage(branch=True)
    cov.start()

    # run tests
    tests = unittest.TestLoader().discover('.')
    tests_ok = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()

    # print coverage report
    cov.stop()
    print('')
    cov.report(omit=['manage.py', 'tests/*', 'venv/*'])

    # lint the code
    print('')
    lint_ok = subprocess.call(['flake8', '--ignore=E402', 'pibrew.py',
                               'tests']) == 0

    sys.exit((0 if tests_ok else 1) + (0 if lint_ok else 2))
